import click
import os
import sys
import yaml

@click.group()
@click.pass_context
def cli(ctx):
    if ctx.parent:
        print(ctx.parent.get_help())


@cli.command(short_help="Add Credentials")
def auth():
    username = click.prompt('Username')
    password = click.prompt('Password', hide_input=True)
    with open("%s/%s" % (os.getcwd(), '/.screepsas.yaml'), 'w') as fd:
        fd.write(
            yaml.dump({
                'username': username,
                'password': password,
            })
        )


@cli.command(short_help="Find Ideal Room and Position")
def respawn():
    from autospawner.spawner import Spawner
    spawner = Spawner()
    if not spawner.shouldSpawn():
        click.echo('Not appropriate to spawn at this time')
        sys.exit(-1)
    shard = spawner.getShard()
    room = spawner.getRoom(shard)
    position = spawner.getPosition(room, shard)
    click.echo("%s %s %s,%s" % (shard, room, position['x'], position['y']))


@cli.command(short_help="Find Ideal Room and Position")
def room():
    from autospawner.spawner import Spawner
    spawner = Spawner()
    shard = spawner.getShard()
    room = spawner.getRoom(shard)
    position = spawner.getPosition(room, shard)
    click.echo("%s %s %s,%s" % (shard, room, position['x'], position['y']))


@cli.command(short_help="Should respawn")
def shouldspawn():
    from autospawner.spawner import Spawner
    spawner = Spawner()
    doit = spawner.shouldSpawn()
    click.echo("%s" % (doit,))
    if not doit:
        sys.exit(-1)


@cli.command(short_help="Find ideal shard")
def shard():
    from autospawner.spawner import Spawner
    spawner = Spawner()
    shard = spawner.getShard()
    click.echo(shard)


@cli.command(short_help="Show the ideal room position for the specified room")
@click.argument('room')
@click.argument('shard')
def position(room, shard):
    from autospawner.spawner import Spawner
    spawner = Spawner()
    position = spawner.getPosition(room, shard)
    click.echo("%s %s %s,%s" % (shard, room, position['x'], position['y']))


@cli.command(short_help="Display the terrain matrix for any room")
@click.argument('room')
@click.argument('shard')
def terrain(room, shard):
    from autospawner.spawner import Spawner
    spawner = Spawner()
    terrain = spawner.roominfo.getRoomTerrain(room, shard)
    print(terrain[3][0])
    for y in range(0,50):
        row = ''
        for x in range(0,50):
            if terrain[x][y] == 'wall':
                score = 0
            elif terrain[x][y] == 'plain':
                score = 1
            elif terrain[x][y] == 'swamp':
                score = 2
            row = '%s%s' % (row, score)
        click.echo(row)


@cli.command(short_help="Show the distance transform matrix for any room")
@click.argument('room')
@click.argument('shard')
def dt(room, shard):
    from autospawner.spawner import Spawner
    spawner = Spawner()
    dt = spawner.roominfo.getDistaceTranceform(room, shard)
    for y in range(0,50):
        row = ''
        for x in range(0,50):
            row = '%s%s' % (row, dt[x][y])
        click.echo(row)


if __name__ == '__main__':
    cli()
