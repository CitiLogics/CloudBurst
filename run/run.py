# pipenv run python3 run.py [master_url ip addr]
#
#   Runs an ensemble simulation for net3, as a demonstration
#   You must provide en_worker.py to send to worker nodes.
#   Just give RedisQueue a job description that will make sense
#   to en_worker.py
#
# job = {
#     input: {
#         url: 'http://file_store/model.inp',
#         startTimeUtc: '2017-01-01T00:00:00'
#     },
#     run: {
#
#         ... // todo: support runtime alterations to networks
#     },
#     output: {
#         host: 'influx',
#         db: 'influx_database_name',
#         dbTag: 'simulation_id', # this tag will be appended to every series produced in this sim
#         dbTagValue: 'sim-123', # unique identifier for this simulation
#         node: ['*'] # specify type of element, or particular ids
#         link: [['flow',3600,]]
#     }
# }

import urllib
import os
import zipfile
import sys

from rq import Queue
from redis import Redis
import time
import requests

master_url = sys.argv[1]
file_store_port = 25478
redis_port = 6379
token = '2da30b10533d688e19f7'
envfile = 'worker.zip'
network = 'net3.inp'



# package up the worker script and send to file_store
print('zipping up worker script and Pipfile')
with zipfile.ZipFile(envfile,'w') as workerzip:
    workerzip.write('en_worker.py')
    workerzip.write('Pipfile')

fsUrl = 'http://{}:{}/upload?token={}'.format(master_url,file_store_port,token)
upFiles = {'file': open(envfile, 'rb')}
sendWorkerReq = requests.post(fsUrl, files=upFiles)

print('sending worker script to file store')
if sendWorkerReq.status_code != requests.codes.ok:
    print('sending worker script failed');
    exit(1)

print('sending network file to store')
netFile = {'file': open(network, 'rb')}
sendNetworkReq = requests.post(fsUrl, files=netFile)
if sendNetworkReq.status_code != requests.codes.ok:
    print('sending network file failed');
    exit(1)

print('establishing redis queue connection')
# Tell RQ what Redis connection to use
redis_conn = Redis(host=master_url, port=redis_port, db=0)
q = Queue(connection=redis_conn)  # no args implies the default queue

count = 0
while count < 100:
    params = {
        'input': {
            'url': 'http://file_store:{}/files/{}?token={}'.format(file_store_port, network, token),
            'startTimeUtc': '2018-05-28T00:00:00'
        },
        'options': {
            'adjust': 'diameter',
            'distribution': 'uniform',
            'seed': count,
            'parameters': {
                'min': 0.8,
                'max': 1.2
            }
        },
        'output': {
            'host': 'influx',
            'db': 'cloudburst',
            'dbTag': 'sim_id',
            'dbTagValue': count,
            'node': [['head', '1'], ['pressure', '101']],
            'link': [['flowrate', '101']]
        }
    }
    print('enqueuing job {}'.format(count))
    job = q.enqueue('en_worker.work', params)
    count += 1

exit(0)
