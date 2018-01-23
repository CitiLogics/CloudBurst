#!/bin/bash

# download the worker module
echo "downloading python module"
curl http://${FILE_HOST}/worker.py --output worker.py

# start the worker process
echo "starting worker process"
rq worker -u tcp://${REDIS_HOST}:6379
