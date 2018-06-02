#!/bin/bash
# this entry script just downloads a Pipenv,
# installs anything required by it,
# and then listens to a Redis Queue for jobs.
# include any custom scripts you want to reference.

# note that this script exits early if the worker.zip file can't be downloaded,
# which means that the service will be restarted until that download succeeds.

echo "downloading python environment from ${FILE_HOST}:${FILE_HOST_PORT}"
rm -rf worker_env
mkdir worker_env && cd worker_env && \
curl -v http://${FILE_HOST}:${FILE_HOST_PORT}/files/worker.zip?token=${FILE_HOST_TOKEN} --output worker.zip && \
unzip worker.zip && \
pipenv install && \
echo "starting worker process" && \
pipenv run rq worker -u tcp://${REDIS_HOST}:6379
