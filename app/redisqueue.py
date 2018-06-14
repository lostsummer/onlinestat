#!/usr/bin/env python

import redis
import app.config

qConf = app.config.queue
redisInfo = qConf["redis"]
key = qConf["key"]
host = redisInfo["host"]
port = redisInfo["port"]
db = redisInfo["db"]
cli = redis.StrictRedis(host, port, db)

def pushQueue(val):
    cli.lpush(key, val)

