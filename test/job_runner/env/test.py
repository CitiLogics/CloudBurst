# pipenv run python3 test.py
#
# job = {
#     input: {
#         url: 'http://fs/model.inp',
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

from rq import Queue
from redis import Redis
import time

# Tell RQ what Redis connection to use
redis_conn = Redis(host='localhost', port=6379, db=0)
q = Queue(connection=redis_conn)  # no args implies the default queue

count = 0
while count < 10:
    params = {
    'input': {
        'url': 'http://fs/net3.inp',
        'startTimeUtc': '2017-01-01T00:00:00'
    },
    'output': {
        'host': 'influx',
        'db': 'ensemble',
        'dbTag': 'sim_id',
        'dbTagValue': count,
        'node': [['pressure','1'],['pressure','2']],
        'link': [['flowrate','101']]
    }
    }
    job = q.enqueue('en_worker.work', params)
    count += 1

exit(0)
