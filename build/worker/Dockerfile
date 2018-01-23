##
## requires some environment variables:
## - REDIS_HOST: redis database on default port
## - FILE_HOST: nginx host to serve the pipenv and any other files you may need
##

FROM python:3
RUN apt-get update
RUN apt-get install -y zip
RUN pip install pipenv
WORKDIR /worker
COPY assets/worker_entry.sh ./
RUN chmod +x /worker/worker_entry.sh
ENTRYPOINT ["/worker/worker_entry.sh"]
