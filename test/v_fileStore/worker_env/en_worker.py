import urllib
from wntr import network
from wntr import sim
import os
import requests
import pandas as pd
from influxdb import DataFrameClient

def rptHook(count, blockSize, totalSize):
    print("#: {} blockSize: {} tot: {}".format(count,blockSize,totalSize))

def work(params):
    startTime = params['input']['startTimeUtc']
    inputUrl = params['input']['url']
    outOpts = params['output']

    # log to console:
    print("executing simulation with options:")
    print(params['input'])
    print(outOpts)

    # set up connection to results db
    client = DataFrameClient(host=outOpts['host'], database=outOpts['db'])

    # download the referenced inp_file and run simulation
    fn, headers = urllib.request.urlretrieve(url=inputUrl, reporthook=rptHook)
    wn = network.WaterNetworkModel(fn)
    my_sim = sim.EpanetSimulator(wn)
    results = my_sim.run_sim()

    for eType, panel in {'node':results.node, 'link':results.link}.items():
        for s in outOpts[eType]:
            d = panel.loc[s[0],:,s[1]]
            # convert from seconds-from-zero into a real DateTime.
            d.index = pd.to_datetime(d.index, unit='s', origin=startTime)
            d = d.to_frame()
            d.columns = ['value']
            # send the data off to the db.
            client.write_points(
                d,
                measurement = s[0],
                tags = {
                    eType: s[1],
                    outOpts['dbTag']: outOpts['dbTagValue']
                },
                protocol='json',
                batch_size=10000
            )
