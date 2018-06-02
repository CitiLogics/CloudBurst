from en_worker import work

params = {
    'input': {
        'filepath': 'net3.inp',
        'startTimeUtc': '2017-01-01T00:00:00'
    },
    'options': {
        'adjust': 'diameter',
        'distribution': 'uniform',
        'seed': 3,
        'parameters': {
            'min': 0.8,
            'max': 1.2
        }
    },
    'output': {
        'host': 'influx',
        'db': 'cloudburst',
        'dbTag': 'sim_id',
        'dbTagValue': 1,
        'node': [['head','1'],['pressure','101']],
        'link': [['flowrate','101']]
    }
    }
print('enqueuing job {}'.format(params))

work(params)
