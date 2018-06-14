#!/usr/bin/env python

import yaml

server = {'host':'0.0.0.0', 'port':'80'}
redis = [
    {'host':'172.31.23.16', 'port':6390, 'db':0},
    {'host':'172.31.23.16', 'port':6390, 'db':1}
]

queue = {"redis":{'host':'172.28.1.118', 'port':6379, 'db':0}, "key":"EMoney.Tongji:Page_OnlineTime"}

def initByYaml(file_path):
    with open(file_path, 'r') as f:
        global server, redis, queue
        conf = yaml.load(f)
        server = conf['server']
        redis = conf['redis']
        queue = conf['queue']
