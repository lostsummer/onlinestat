#!/usr/bin/env python

import asyncio
import app.config
from app.redisutil import webData2Redis
from app.redisqueue import pushQueue
from sanic import Sanic
from sanic import response

sapp = Sanic()

@sapp.get("/")
async def index(request):
    return response.text("你好, 世界")

@sapp.get("/page/onlinetime")
async def oneline(request):
    hb_data = request.raw_args
    if not ('globalid' in hb_data and
            'code' in hb_data and
            'time' in hb_data):
        return response.json(
                {'message': 'Less args!'},
                headers={'Access-Control-Allow-Origin':'*'},
                status=200
        )
    else:
        push, msg = webData2Redis(hb_data)
        if push:
            pushQueue(msg)
            webData2Redis(hb_data)
        return response.json(
                {'message': 'Success'},
                headers={'Access-Control-Allow-Origin':'*'},
                status=200
        )

def run():
    srvConf = app.config.server
    sapp.run(srvConf['host'], srvConf['port'])

if __name__ == "__main__":
    run()
