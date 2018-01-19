from epanet_worker import work


job = {
    input: {
        url: 'http://fs/model.inp',
        startTimeUtc: '2017-01-01T00:00:00Z'
    },
    output: {
        host: 'influx',
        db: 'influx_database_name',
        dbTag: 'simulation_id', # this tag will be appended to every series produced in this sim
        tag: 'sim-123', # unique identifier for this simulation
        elements: ['*'] # specify type of element, or particular ids
    }
}


work(job)
