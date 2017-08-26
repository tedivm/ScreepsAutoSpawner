import screepsapi
import os
import sys
import yaml

cwd = os.getcwd()
path = cwd + '/.screepsas.yaml'

if not os.path.isfile(path):
    print('no settings file found')
    sys.exit(-1)

with open(path, 'r') as f:
    settings = yaml.load(f)

if 'ptr' not in settings:
    settings['ptr']= None
if 'host' not in settings:
    settings['host']= None

screepsclient = screepsapi.API(
                u=settings['username'],
                p=settings['password'],
                ptr=settings['ptr'],
                host=settings['host'])
