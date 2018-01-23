# CloudBurst
A docker-based ensemble simulation framework

# TLDR:
Supply your own python script and Pipenv requirements, and submit as many tasks as you like. The swarm will parallel-execute tasks FIFO and upload your results where you specify.

# Work in progress
This is a work in progress. The goal is to have a docker-compose file that can be quickly and easily deployed to a properly configured swarm. All you have to bring is your analysis script.

# Container types
This project uses a few different container types, to be run on 2 different node types:

Master Node:
- Redis/RQ for job-queueing
- InfluxDB for collecting results
- Grafana for visualization
- Redis Queue Dashboard for visualizing worker node activity
- Nginx instance for serving the Pipenv and other assets

Swarm Nodes:
- openwateranalytics/ensemble_worker -> runs tasks

The project also needs you to run a script for generating EPANET input files and sending the job descriptions to RQ. An example script is given - it can be run from anywhere you have a Python interpreter and an internet connection.

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
| | Nginx    |          |  | Redis |  | Grafana | |
| |          v          |  +---^---+  +----^----+ |
| |  input              |      |           |      |
| |  files              |      |           |      |
| |                     |      |           |      |
| |  env.zip            |      |           |      |
| |  [Pipenv,worker.py] |      |      +----+---+  |
| |                     |      |      | Influx |  |
| +-------+-------------+      |      +----^---+  |
|         |                    |           |      |
|         |                    |           |      |
+-------------------------------------------------+
          |                    |           |
          |                    |           |
          |                    |           |
          |                    |           |
+---------v-------------+      |           |
|WORKER                 |      |           |
|                       <------+           |
| pipenv run rq worker  |                  |
|                       +------------------+
+-----------------------+




```

# Performing work on the swarm

First, set up your worker script. Use Pipenv to specify any requirements. Zip up the `Pipenv[.lock]` and `worker.py` files and put that archive on the Nginx volume.

From your client of choice, call the rq `enqueue` function with a string representation of your `module.function` you want to run. The argument can be whatever your module takes, but the example provided here is a job description of the format:

```
{
     input: {
         url: 'http://fs/model.inp',
         startTimeUtc: '2017-01-01T00:00:00'
     },
     run: {
       ... // todo: support runtime alterations to networks
     },
     output: {
         host: 'influx',
         db: 'influx_database_name',
         dbTag: 'simulation_id', # this tag will be appended to every series produced in this sim
         dbTagValue: 'sim-123', # unique identifier for this simulation
         node: ['*'] # specify type of element, or particular ids
         link: [['flow',3600,]]
     }
}
```

## Simulation (Worker) Nodes
The worker nodes will execute the following operations:

- download your `env.zip` payload,
- extract it,
- install any dependencies,
- `pipenv run rq worker -u tcp://REDIS_HOST:6379`

This means that the worker nodes can use a very simple base docker image, since they will download their own dependencies on-the-fly, as specified in your `env.zip` package.
