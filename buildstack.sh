#!/bin/bash

# cloudburst needs a Digital Ocean token
[ -z "$DOTOKEN" ] && echo "Need to set DOTOKEN" && exit 1;

blank(){
  for i in $(seq 1 $1);do echo "";done
}

blank 20

echo "
██████╗██╗      ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗   ██╗██████╗ ███████╗████████╗
██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔════╝╚══██╔══╝
██║     ██║     ██║   ██║██║   ██║██║  ██║██████╔╝██║   ██║██████╔╝███████╗   ██║
██║     ██║     ██║   ██║██║   ██║██║  ██║██╔══██╗██║   ██║██╔══██╗╚════██║   ██║
╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝██████╔╝╚██████╔╝██║  ██║███████║   ██║
╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝
"
blank 3


#
# specify the number of nodes with the -n option
# default is 3

usage(){
  cat <<EOF
  Usage: $0 [options]
  -n the number of worker nodes to create or destroy (default 3)
  -d destroy the stack
  -h displays this message
EOF
	exit $1
}


while getopts dhn: opt; do
	case "${opt}" in
		n) n_workers=$OPTARG ;;
		d) removeflag="TRUE" ;;
    h) usage 0 ;;
		\?)
      echo "Invalid option: -$OPTARG" >&2
      usage 1
        ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage 1
        ;;
	esac
done

if [[ -z "$n_workers" ]]; then
	n_workers=3
fi
if ! [[ -z "$removeflag" ]]; then
	echo "WARNING: this will remove a deployed stack and destroy the droplets";
  # TODO: confirm destroy
fi

shift $(($OPTIND-1))


openpages(){
  open http://${1}:8080
  open http://${1}:9181
  open http://${1}:3000
}

create(){
  # $1 is the count
  # create the master node
  docker-machine create \
  --driver digitalocean \
  --digitalocean-image docker \
  --digitalocean-size s-2vcpu-4gb \
  --digitalocean-access-token $DOTOKEN \
  cloudburst-master

  # get the IP address of cloudburst master
  export CBM_IP=$(docker-machine ls | grep cloudburst-master | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}')
  # initialize swarm mode on the master and capture the token
  export SWARMTOKEN=$(docker-machine ssh cloudburst-master "docker swarm init --advertise-addr ${CBM_IP}" | grep -o 'SWMTKN[^[:space:]]*')

  # create some worker nodes
  for node_number in $(seq 1 $1);
  do
    export CREATE_WORKER_COMMAND="\
    docker-machine create \
    --driver digitalocean \
    --digitalocean-image docker \
    --digitalocean-size s-1vcpu-1gb \
    --digitalocean-access-token $DOTOKEN \
    cloudburst-worker-${node_number} \
    && \
    docker-machine ssh cloudburst-worker-${node_number} \"docker swarm join --token ${SWARMTOKEN} ${CBM_IP}:2377\""

    bash -c "${CREATE_WORKER_COMMAND}" &
  done

  # configure the shell to talk to master
  eval $(docker-machine env cloudburst-master)
  docker stack deploy -c docker-compose.yml cloudburst
  echo "Master IP is ${CBM_IP}"
  echo "Swarm token is ${SWARMTOKEN}"

  openpages $CBM_IP
}


destroy(){
  eval $(docker-machine env cloudburst-master)
  for node_number in $(seq 1 $1);
  do
    docker-machine rm -y cloudburst-worker-${node_number}
  done
  docker-machine rm -y cloudburst-master
}



if [[ -z "$removeflag" ]]
then
	create $n_workers
else
  destroy $n_workers
fi
