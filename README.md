# ScreepsAutoSpawner

The ScreepsAutoSpawner identifies when a player is no longer spawned on the [Screeps](https://screeps.com/) server and then resets the memory before placing a spawn.

It uses a series of rules to make sure that the room it respawns in is approprirate, such as checking for two sources and confirming the player is allowed to spawn in that room, that the room has enough open space, and that the room isn't too swampy.


## Commands

* `screepsautospawner auth` - Give the username and password for the Screeps server. This command is the only interactive command.

* `screepsautospawner respawn` - If allowed identify a shard and room to respawn in and do so. This will also clear all memory and segments.

* `screepsautospawner shouldspawn` - Return `true` if the system believes it should respawn. Also returns a `-1` error code if respawning isn't appropriate.

* `screepsautospawner room` - Display the shard, room, and position that the system would respawn in. This will change between runs due to different starting rooms from the server.

* `screepsautospawner shard` - Display the selected shard.

* `screepsautospawner position ROOM SHARD` - Display the best position for the supplied room and shard.

* `screepsautospawner terrain ROOM SHARD` - Display a map of the terrain for the supplied room and shard.

* `screepsautospawner dt ROOM SHARD` - Display a distance transfor map for the supplied room and shard.
