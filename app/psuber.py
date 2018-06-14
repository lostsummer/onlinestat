#!/usr/bin/env python

import asyncio
from app.redisutil import getPSubers, listenPSub

def run():
    loop = asyncio.get_event_loop()
    tasks = [listenPSub(p) for p in getPSubers()]
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == '__main__':
    run()
