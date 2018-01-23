from wntr import network
from wntr import sim
import os
import requests
from influxdb import DataFrameClient

localFile = 'job.inp'

def work(params):

    # download the referenced inp_file
    urllib.request.urlretrieve(params.inputUrl, localFile)

    wn = network.WaterNetworkModel(localFile)
    sim = sim.EpanetSimulator(wn)
    results = sim.run_sim()

    # set up connection to results db
    resultsClient = DataFrameClient(host=params.output.host, database=params.output.db)
