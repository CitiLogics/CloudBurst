FROM ubuntu:xenial
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-pip
RUN pip install numpy scipy networkx pandas matplotlib wntr
RUN pip install influxdb rq requests
WORKDIR /worker
VOLUME /worker
CMD ["bash"]
