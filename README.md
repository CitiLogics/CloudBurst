# CloudBurst
A docker-based ensemble water distribution system simulation framework

# Containers
This project uses a few different container types:

- Redis for job-queueing
- SimulatorNode (EPANET) for running simulations
- InfluxDB for collecting results
- Grafana for visualization

The project also uses a script for generating EPANET input files and sending the job descriptions to Redis.

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
  input: '/path/to/model_123.inp',
  output: {
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
