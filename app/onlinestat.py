#!/usr/bin/env python

"""docstring
"""

__author__ = 'wangyuxin'
__revision__ = '0.1'

import multiprocessing
import app.config
app.config.initByYaml('/etc/onlinestat.yml')

import app.server, app.psuber
def run():
    pool = multiprocessing.Pool(processes=4)
    pool.apply_async(app.server.run, ())
    pool.apply_async(app.psuber.run, ())
    pool.close()
    pool.join()


if __name__ == '__main__':
    run()
