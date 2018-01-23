#!/bin/bash

cd v_fileStore/worker_env
zip env.zip en_worker.py Pipfile Pipfile.lock
mv env.zip ../
cd ../../../

docker stop cloudburst_queue_1
docker rm cloudburst_queue_1
docker-compose up -d queue

docker exec cloudburst_influx_1 influx -execute 'drop database ensemble; create database ensemble'

docker-compose up worker
