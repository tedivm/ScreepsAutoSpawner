import screepsapi
from screeps import screepsclient
import re
import random
import sys
from websocket import create_connection
import json


SPAWN_BUFFER = 3
MINIMUM_DENSITY = 0.35
MAXIMUM_SWAMPINESS = 0.20
MINIMUM_SOURCES = 2

class Spawner:

    def __init__(self):
        self.roominfo = RoomInfo()

    def shouldSpawn(self):
        statusres = screepsclient.world_status()
        return 'status' in statusres and statusres['status'] == 'empty'

    def respawn(self, shard, room, position):
        if not self.shouldSpawn():
            return False
        self.resetMemory()
        self.place_spawn(room, 'Spawn1', position['x'], position['y'], shard)

    def resetMemory(self):
        for shard in shards:
            screepsclient.set_memory('', '{"creeps":{},"spawn":{},"rooms":{},"flags":{}}', shard)
            for i in range(0, 100):
                screepsclient.set_segment(segid, '', shard)

    def getShard(self):
        shardinfo = screepsclient.shard_info()['shards']
        shards = {}

        max_density = 0
        max_tick = 0
        for info in shardinfo:
            shard = info['name']
            shards[shard] = info['name']
            if info['tick']/1000 > max_tick:
                max_tick = info['tick']/1000
            info['density'] = info['users'] / info['rooms']
            if info['density'] > max_density:
                max_density = info['density']
            shards[shard] = info

        min_score = 100
        winning_shard = False
        for shard in shards:
            # shard with highest density will be 1, everything else will be lower
            density_score = 1 * shards[shard]['density']/max_density
            tick_score = 2 * (shards[shard]['tick']/1000)/max_tick
            score = density_score + tick_score

            if not winning_shard or min_score > score:
                winning_shard = shard
                min_score = score

        return winning_shard

    def getRoom(self, shard):
        sectors = screepsclient.world_start_room(shard=shard)['room']

        while True:
            sector = sectors.pop()
            rooms = self.getRoomList(shard, sector)
            if len(rooms) < 1:
                if len(sectors) < 1:
                    return False
                continue

            rooms = self.sortRooms(rooms)
            return rooms[0]

    def sortRooms(self, rooms):
        random.shuffle(rooms)
        return rooms

    def getRoomList(self, shard, sector):
        p = re.compile('^(E|W)(\d+)(N|S)(\d+)$')
        matches = p.match(sector).groups()
        dir_x = matches[0]
        dir_y = matches[2]
        start_x = int(matches[1])-4
        start_y = int(matches[3])-4
        roomlist = []
        for x in range(start_x, start_x+9):
            sys.stdout.write('.')
            sys.stdout.flush()
            for y in range(start_y, start_y+9):
                roomname = "%s%s%s%s" % (dir_x, x, dir_y, y)
                if x < 7 and y < 7:
                    if x > 3 and y > 3:
                        continue
                if not self.filterRoom(roomname, shard):
                    continue
                roomlist.append(roomname)
        sys.stdout.write('\n')
        return roomlist

    def filterRoom(self, room, shard):
        sources = self.roominfo.getSourceLocations(room, shard)
        if not sources:
            return False
        if len(sources) < MINIMUM_SOURCES:
            return False

        if not self.roominfo.isClaimable(room, shard):
            return False

        if self.roominfo.getDensity(room, shard) < MINIMUM_DENSITY:
            return False

        if self.roominfo.getSwampiness(room, shard) < MAXIMUM_SWAMPINESS:
            return False

        return True

    def getPosition(self, room, shard):
        return self.roominfo.getPosition(room, shard)


OOB = 0

class RoomInfo:

    ws = False
    my_details = False
    cache_details = {}
    cache_terrain = {}

    def getControllerLocation(self, room, shard):
        details = self.getRoomDetails(room, shard)
        if 'c' not in details:
            return False
        return {'x': details['c'][0][0], 'y': details['c'][0][1]}

    def getSourceLocations(self, room, shard):
        details = self.getRoomDetails(room, shard)
        if 's' not in details:
            return False
        return details['s']

    def getClient(self):

        if self.ws:
            return self.ws

        if screepsclient.host:
            url = 'wss://' if screepsclient.secure else 'ws://'
            url += screepsclient.host + '/socket/websocket'
        elif not screepsclient.ptr:
            url = 'wss://screeps.com/socket/websocket'
        else:
            url = 'wss://screeps.com/ptr/socket/websocket'

        ws = create_connection(url)
        ws.send('auth ' + screepsclient.token)

        while True:
            response = ws.recv()
            if response.startswith('auth'):
                if response.startswith('auth ok'):
                    self.ws = ws
                    return ws
                else:
                    # Authentication Error
                    raise Exception('Unauthorized')

    def getRoomDetails(self, room, shard='shard0'):

        if shard not in self.cache_details:
            self.cache_details[shard] = {}

        if room in self.cache_details[shard]:
            return self.cache_details[shard][room]

        ws = self.getClient()
        if shard:
            ws.send('subscribe roomMap2:%s/%s' % (shard, room))
        else:
            ws.send('subscribe roomMap2:%s' % (room,))

        while True:
            response = ws.recv()
            if not response.startswith('["roomMap2'):
                continue
            try:
                data = json.loads(response)
            except ValueError:
                print(ValueError)
                continue

            if 'shard' in data[0]:
                p = re.compile("roomMap2:(.*)/(.*)")
                matches = p.match(data[0]).groups()
                shard = matches[0]
                room = matches[1]
            else:
                p = re.compile("roomMap2:(.*)")
                matches = p.match(data[0]).groups()
                shard = 'shard0'
                room = matches[0]

            if shard:
                ws.send('unsubscribe roomMap2:%s/%s' % (shard, room))
            else:
                ws.send('unsubscribe roomMap2:%s' % (room,))

            self.cache_details[shard][room] = data[1]
            return data[1]

    def isClaimable(self, room, shard):
        status_details = screepsclient.room_status(room, shard)['room']
        if status_details['status'] != 'normal':
            return False

        if 'novice' in status_details:
            if self.getGcl() > 3:
                return False

        overview = screepsclient.room_overview(room, shard=shard)

        if overview['owner'] is not None:
            return False

        return True

    def getRoomTerrain(self, room, shard):

        if shard not in self.cache_terrain:
            self.cache_terrain[shard] = {}

        if room in self.cache_terrain[shard]:
            return self.cache_terrain[shard][room]

        terrain_list = screepsclient.room_terrain(room, shard=shard)
        terrain_matrix = {}
        for terrain in terrain_list['terrain']:
            if terrain['x'] not in terrain_matrix:
                terrain_matrix[terrain['x']] = {}

            if terrain['x'] in terrain_matrix and terrain['y'] in terrain_matrix[terrain['x']]:
                terrain_matrix[terrain['x']][terrain['y']] = 'wall'
            else:
                terrain_matrix[terrain['x']][terrain['y']] = terrain['type']

        for x in range(0,50):
            if x not in terrain_matrix:
                continue
            for y in range(0,50):
                if y not in terrain_matrix[x]:
                    terrain_matrix[x][y] = 'plain'

        self.cache_terrain[shard][room] = terrain_matrix
        return terrain_matrix

    def getDistaceTranceform(self, room, shard):
        terrain = self.getRoomTerrain(room, shard)
        dt = {}
        for y in range(0, 50):
            for x in range(0, 50):
                if x not in dt:
                    dt[x] = {}

                if x in terrain and y in terrain[x] and terrain[x][y] == 'wall':
                    dt[x][y] = 0
                    continue

                A = self.getTerrainScore(x-1, y-1, dt, terrain)
                B = self.getTerrainScore(x  , y-1, dt, terrain)
                C = self.getTerrainScore(x+1, y-1, dt, terrain)
                D = self.getTerrainScore(x-1, y  , dt, terrain)
                # A, B, C
                # D, e, f
                # g, f, i
                # Get minimum value from A, B, C and D and then add one.
                dt[x][y] = min([A, B, C, D])+1

        for y in reversed(range(0, 50)):
            for x in reversed(range(0, 50)):
                # a, b, c
                # d, E, F,
                # G, H, I
                E = self.getTerrainScore(x  , y  , dt, terrain)
                F = self.getTerrainScore(x+1, y  , dt, terrain)
                G = self.getTerrainScore(x-1, y+1, dt, terrain)
                H = self.getTerrainScore(x  , y+1, dt, terrain)
                I = self.getTerrainScore(x+1, y+1, dt, terrain)
                # Add one to every value *except* current one (E), and then save minimum.
                dt[x][y] = min([E, F+1, G+1, H+1, I+1])

        return dt

    def getTerrainScore(self, x, y, dt, terrain):

        if x < 0 or x > 49 or y < 0 or y > 49:
            return OOB

        if x == 0 or x == 49 or y == 0 or y == 49:
            return 0

        if x in terrain and y in terrain[x] and terrain[x][y] == 'wall':
            return 0

        if x not in dt:
            return 0

        if y not in dt[x]:
            return 0

        return dt[x][y]

    def getDensity(self, room, shard):
        walkable - self.getWalkableCount()
        return walkable/(50*50)

    def getSwampiness(self, room, shard):
        terrain = self.getRoomTerrain(room, shard)
        swamps = 0
        for x in range(0, 50):
            for y in range(0, 50):
                if terrain[x][y] == 'swamp':
                    swamps += 1
        walkable - self.getWalkableCount()
        return swamps/walkable

    def getWalkableCount():
        terrain = self.getRoomTerrain(room, shard)
        walkable = 0
        for x in range(0, 50):
            for y in range(0, 50):
                if x not in terrain or y not in terrain[x]:
                    walkable += 1
                elif terrain[x][y] == 'swamp':
                    walkable += 1
        return walkable


    def getPosition(self, room, shard):
        dt = self.getDistaceTranceform(room, shard)
        cur_distance = 50
        controller_pos = self.getControllerLocation(room, shard)
        ret = {'x':25, 'y':25}
        x_list = list(range(0, 50))
        random.shuffle(x_list)
        for x in x_list:
            y_list = list(range(0, 50))
            random.shuffle(y_list)
            for y in y_list:
                position_buffer = dt[x][y]
                if position_buffer < (SPAWN_BUFFER+1):
                    continue
                test_pos = {'x': x, 'y': y}
                controller_distance = self.getDistanceBetween(test_pos, controller_pos)
                print(controller_distance)
                if controller_distance < cur_distance:
                    cur_distance = controller_distance
                    ret['x'] = x
                    ret['y'] = y

        return ret

    def getDistanceBetween(self, a, b):
        return max(abs(a['x']-b['x']), abs(a['y']-b['y']))

    def getGcl(self):
        if not self.my_details:
            self.my_details = screepsclient.me()
        if 'gcl' not in self.my_details:
            return 1
        return int((self.my_details['gcl']/1000000) ** (1/2.4))+1
