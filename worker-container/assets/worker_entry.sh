#!/bin/bash
# this entry script just downloads a Pipenv,
# installs anything required by it,
# and then listens to a Redis Queue for jobs.
# include any custom scripts you want to reference

echo "downloading python environment from ${FILE_HOST}"
rm -rf worker_env
mkdir worker_env && cd worker_env && \
curl http://${FILE_HOST}/env.zip --output env.zip && \
unzip env.zip && \
pipenv install && \
echo "starting worker process" && \
pipenv run rq worker -u tcp://${REDIS_HOST}:6379
