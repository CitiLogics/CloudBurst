import urllib
from wntr import network
from wntr import sim
import os
import requests
import pandas as pd
from influxdb import DataFrameClient
import random


def rptHook(count, blockSize, totalSize):
    print("#: {} blockSize: {} tot: {}".format(count,blockSize,totalSize))


def work(params):
    startTime = params['input']['startTimeUtc']
    outOpts = params['output']

    # log to console:
    print("executing simulation with options:")
    print(params['input'])
    print(outOpts)

    # set up connection to results db
    client = DataFrameClient(host=outOpts['host'], database=outOpts['db'])

    # download the referenced inp_file and run simulation
    fn = ''
    if 'url' in params['input']:
        fn, headers = urllib.request.urlretrieve(url=params['input']['url'], reporthook=rptHook)
    elif 'filepath' in params['input']:
        fn = params['input']['filepath']



    wn = network.WaterNetworkModel(fn)

    # adjust based on work description
    # 'options': {
    #     'adjust': 'diameter',
    #     'distribution': 'uniform',
    #     'seed': 3,
    #     'parameters': {
    #         'min': 0.6,
    #         'max': 1.5
    #     }
    # }

    multRange = params['options']['parameters']
    random.seed(params['options']['seed'])
    for pipename, p in wn.pipes():
        d = p.diameter
        d = d * random.uniform(multRange['min'], multRange['max'])
        p.diameter = d


    my_sim = sim.EpanetSimulator(wn)
    results = my_sim.run_sim()

    for eType, elementResults in {'node': results.node, 'link': results.link}.items():
        for s in outOpts[eType]:
            print('fetching results for {} {} {}'.format(eType, s[1], s[0]))
            d = elementResults[s[0]].loc[:, s[1]]
            # convert from seconds-from-zero into a real DateTime.
            d.index = pd.to_datetime(d.index, unit='s', origin=startTime)
            d = d.to_frame()
            d.columns = ['value']
            # send the data off to the db.
            print('sending results to db...')
            client.write_points(
                d,
                measurement=s[0],
                tags={
                    eType: s[1],
                    outOpts['dbTag']: outOpts['dbTagValue']
                },
                protocol='json',
                batch_size=10000
            )
