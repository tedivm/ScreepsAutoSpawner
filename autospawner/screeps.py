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

if 'token' in settings:
    screepsclient = screepsapi.API(
                    token=settings['token'],
                    ptr=settings['ptr'],
                    host=settings['host'])
else:
    screepsclient = screepsapi.API(
                    u=settings['username'],
                    p=settings['password'],
                    ptr=settings['ptr'],
                    host=settings['host'])

def api_error_except(api_result):
    if 'error' in api_result:
        raise Exception(api_result['error'])
    return api_result

setattr(screepsclient, "api_error_except", api_error_except)
