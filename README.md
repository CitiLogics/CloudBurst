# CloudBurst
A docker-based ensemble simulation framework

# Running CloudBurst:
Supply your own python script and Pipenv requirements, and submit as many tasks as you like. The swarm will parallel-execute tasks FIFO and upload your results where you specify.
Use `buildstack.sh` to build, deploy, and teardown the cloud part.

To create the swarm and deploy the stack, make sure you have a Digital Ocean token in your env as `$DOTOKEN` and then run:
```
>$ ./buildstack.sh -n3
```

The `-n` flag specifies how many compute nodes you want. Be aware of your DO droplet limit, but also remember that DO provides droplet configurations up to 42 vCPUs.

To send work to the swarm, you need three things:

- A worker script to be executed by the worker nodes.
- A set of job descriptions that makes sense to the worker scripts.
- A script to send those job descriptions to redis-queue.

Set up your python worker script along with a Pipenv, and zip it up as `worker.zip`. Using the provided `run.py` as an example, HTTP/POST that file to the simple filestore. Your worker nodes will immediately start downloading that worker payload and start installing their dependencies.

Now, craft your job descriptions using `run.py` as an example and send the jobs to redis-queue. At this point, your worker nodes will start grabbing those descriptions and doing the work. In this example, InfluxDB and Grafana are used to recieve and visualize the results of the simulations, but your needs may vary so you need not use those services - the workers just do what they are told and can upload results wherever you specify.


# Work in progress
This is a work in progress. The goal is to have a stack that can be quickly and easily deployed to a properly configured swarm. All you have to bring is your simulation and analysis scripts.

# Container types
This project uses a few different container types, to be run on 2 different node types:

Master Node:
- Redis/RQ for job-queueing
- InfluxDB for collecting results
- Grafana for visualization
- Redis Queue Dashboard for visualizing worker node activity
- Nginx instance for serving the Pipfile, worker script, and other assets
- A Go-based simple-upload-server to reieve and serve file assets.

Swarm Nodes:
- openwateranalytics/ensemble_worker: runs tasks generically using a very simple worker script


```

+--------------+
| CLIENT       |
|              |
|   Scenario   |
|   Generator  |
|              +---------------+
+------------+-+               |
             |                 |
             |                 |
+-------------------------------------------------+
|MASTER      |                 |                  |
| +---------------------+  +---v---+  +---------+ |
| | FileStore|          |  | Redis |  | Grafana | |
| |          |          |  +---^---+  +----^----+ |
| |  input   v          |      |           |      |
| |  files              |      |           |      |
| |                     |      |           |      |
| |  worker.zip         |      |           |      |
| | [Pipfile,worker.py] |      |      +----+---+  |
| |                     |      |      | Influx |  |
| +-------+-------------+      |      +----^---+  |
|         |                    |           |      |
|         |                    |           |      |
+-------------------------------------------------+
          |                    |           |
          |                    |           |
          |                   job          |
          |               description      |
+---------v-------------+      |         results
|WORKER                 |      |           |
|                       <------+           |
| pipenv run rq worker  |                  |
|                       +------------------+
+-----------------------+



```


## Simulation (Worker) Nodes
The worker nodes will execute the following operations:

- download your `worker.zip` payload,
- extract it,
- install any dependencies,
- `pipenv run rq worker -u tcp://REDIS_HOST:6379`

This means that the worker nodes can use a very simple base docker image, since they will download their own dependencies on-the-fly, as specified in your `worker.zip` package.
