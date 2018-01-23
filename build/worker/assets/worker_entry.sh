#!/bin/bash
# download the worker module
echo "downloading python environment"
rm -rf worker_env
mkdir worker_env && cd worker_env && \
curl http://${FILE_HOST}/env.zip --output env.zip && \
unzip env.zip && \
pipenv install && \
echo "starting worker process" && \
pipenv run rq worker -u tcp://${REDIS_HOST}:6379
