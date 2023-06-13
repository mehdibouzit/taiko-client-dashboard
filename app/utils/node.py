import param
import redis
import json
import datetime.datetime
import requests
import holoviews as hv 
import pandas as pd, numpy as np
from holoviews.streams import Buffer

from tornado.ioloop import PeriodicCallback
from tornado import gen

class Node(param.Parameterized):

    mock_param = param.Number(0.0, precedence=0)

    df = pd.DataFrame({
                       'timestamp': np.array([]),
                       'system': np.array([]),
                       'iowait': np.array([]),
                       'geth': np.array([]),
                       'alloc': np.array([]),
                       'used': np.array([]),
                       'held': np.array([]),
                       'read': np.array([]),
                       'write': np.array([]),
                       'ingress': np.array([]),
                       'egress': np.array([]),
                       'peers': np.array([]),
                       'dials': np.array([]),
                       'serves': np.array([])})
    df.set_index('timestamp', inplace=True)

    buffer = Buffer(data=df, length=1000)
    
    @param.depends('mock_param')
    def get_curves(self,data):
        return ( 
            (
                hv.Curve(data[["timestamp","system"]], label='system') *
                hv.Curve(data[["timestamp","iowait"]], label='iowait') *
                hv.Curve(data[["timestamp","geth"]], label='geth') 
            ) +
            (
                hv.Curve(data[["timestamp","alloc"]], label='alloc') *
                hv.Curve(data[["timestamp","used"]], label='used') *
                hv.Curve(data[["timestamp","held"]], label='held') 
            ) +
            (
                hv.Curve(data[["timestamp","read"]], label='read') *
                hv.Curve(data[["timestamp","write"]], label='write') 
            ) +
            (
                hv.Curve(data[["timestamp","ingress"]], label='ingress') *
                hv.Curve(data[["timestamp","egress"]], label='egress') 
            ) +
            (
                hv.Curve(data[["timestamp","peers"]], label='peers') *
                hv.Curve(data[["timestamp","dials"]], label='dials') *
                hv.Curve(data[["timestamp","serves"]], label='serves') 
            )
        )

    @gen.coroutine
    def get_data(self):
        r = requests.get('http://host.docker.internal:6060/debug/metrics') 
        # Parse data to json
        data = r.json()
        # Get the tags
        self.buffer.send(pd.DataFrame({
            'timestamp': [datetime.now()],
            'alloc': [data['system/memory/allocs.mean']],
            'used': [data['system/memory/used']],
            'held': [data['system/memory/held']],
            'system': [data["system/cpu/sysload"]],
            'iowait': [data["system/cpu/syswait"]],
            'geth': [data["system/disk/readbytes"]],
            'write': [data["system/disk/writebytes"]],
            'ingress': [data["p2p/ingress.count"]],
            'egress': [data["p2p/ingress.count"]],
            'peers': [data["p2p/peers"]],
            'dials': [data["p2p/dials.count"]],
            'serves': [data["p2p/serves.count"]]})
        )
    
    def view(self):
        PeriodicCallback(self.get_data, 1000*10).start()
        return hv.DynamicMap(self.get_curves ,streams=[self.buffer]).opts(
             width=1200, 
             height=600,
             title='Node',
             tools=['hover']
        )