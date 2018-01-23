##
## requires some environment variables:
## - REDIS_HOST: redis database on default port
## - FILE_HOST: nginx host to serve worker.py module
##

FROM python:3
RUN pip install numpy scipy networkx pandas matplotlib wntr
RUN pip install influxdb rq requests
WORKDIR /worker
COPY assets/worker_entry.sh ./
RUN chmod +x /worker/worker_entry.sh
ENTRYPOINT ["/worker/worker_entry.sh"]
