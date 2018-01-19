# CloudBurst
A docker-based ensemble water distribution system simulation framework

# Work in progress
This is a work in progress. The goal is to have a docker-compose file that can be quickly and easily deployed to a properly configured swarm. All you have to bring is your analysis script.

# Containers
This project uses a few different container types, to be run on 2 different node types:

Master Node:
- Redis for job-queueing
- InfluxDB for collecting results
- Grafana for visualization
- Redis Queue Dashboard for visualizing worker node activity

Swarm Nodes:
- rq worker -> runs epanet simulation


The project also uses a script for generating EPANET input files and sending the job descriptions to Redis. This script can be run from anywhere you have a Python interpreter.

```

+---------------+
| INP Generator +--> job descriptions
+------+--------+          +
       |                   |
       |                   |
       |                   |
+------v------+        +---v---+
| input files |        | Redis |
+--+----------+        +---+---+
   |                       |
   |                       |
   |                       |
   |     +-----------+     |
   |     |Worker Node|     |
   |     +-----------+     |
   +---> |Worker Node| <---+
         +-----------+
         |Worker Node|
         +----+------+
              |
              |
         +----v-----+       +---------+
         | InfluxDB | ----->| Grafana |
         +----------+       +---------+



```

## Job Queue
The requirement for this service is that it receive a collection of job descriptions. Each job description appears similar to:

```
{
  input: {
    url: 'http://file-server:port/path/to/model_123.inp',
    startTimeUtc: '2017-01-01T00:00:00Z'
  },
  output: {
    host: 'influx',
    db: 'influx_database_name',
    dbTag: 'simulation_id', // this tag will be appended to every series produced in this sim
    tag: 'sim-123', // unique identifier for this simulation
    elements: ['*'] // specify type of element, or particular ids
  },
}
```

The Redis server receives jobs, and makes them available to worker nodes. Worker nodes "check out" a job, with some reasonable expiration time.

## Simulation (Worker) Nodes
A worker node runs a simple python script:

```
connect to job queue
get next job description
if no description:
  wait a bit, try again.
parse description
execute EPANET simulation on model file specified
upload results to InfluxDB:
  appending the 'dbTag' tag to result series
notify job queue of success
clean up
```
