#!/usr/bin/env python

import asyncio, redis, json
from hashlib import md5
import app.config
from app.redisqueue import pushQueue

qConf = app.config.queue
pre_prefix = qConf["key"] + ":"
ex_key_prefix = pre_prefix + "Ex:"
msg_key_prefix = pre_prefix + "Msg:"
psub_pattern = '__keyevent@{0}__:expired'

update_lua_script = """
local ex_key = KEYS[1]
local msg_key = KEYS[2]
local in_val = ARGV[1]
local msg_val = ''
local expire_sec = 180

local in_data = cjson.decode(in_val)
local in_time = in_data['time']
local msg_data = {}
local result = {}

local ex_exist = redis.call('exists', ex_key)
if ex_exist < 1 then
    local msg_exist = redis.call('exists', msg_key)
    if msg_exist < 1 then
        msg_data = in_data
        msg_data['begin'], msg_data['end'] = in_time, in_time
        msg_data['time'] = nil
        msg_val = cjson.encode(msg_data)
        redis.call('set', msg_key, msg_val)
        result = {0, ''}
    else
        msg_val = redis.call('get', msg_key)
        result = {1, msg_val}
        redis.call('del', msg_key)
    end
    redis.call('set', ex_key, '')
else
    local msg_exist = redis.call('exists', msg_key)
    if msg_exist < 1 then
        msg_data = in_data
        msg_data['begin'], msg_data['end'] = in_time, in_time
        msg_data['time'] = nil
        msg_val = cjson.encode(msg_data)
        redis.call('set', msg_key, msg_val)
        result = {0, ''}
    else
        msg_val = redis.call('get', msg_key)
        msg_data = cjson.decode(msg_val)
        if in_time - tonumber(msg_data['end']) >  expire_sec * 1000 then
            redis.call('del', msg_key)
            result = {1,msg_val}
        else
            if in_time - tonumber(msg_data['end']) > 1000 then
                msg_data['end'] = in_time
            end
            msg_val = cjson.encode(msg_data)
            redis.call('set', msg_key, msg_val)
            result = {0, ''}
            msg_val = cjson.encode(msg_data)
            redis.call('set', msg_key, msg_val)
        end
    end
end
redis.call('expire', ex_key, expire_sec)

return result"""
redisConf = app.config.redis
clis = [redis.StrictRedis(i['host'], i['port'], i['db']) for i in redisConf]
upLuas = [cli.register_script(update_lua_script) for cli in clis]

def myHash(strin):
    m = md5()
    m.update(bytes(strin, encoding='utf-8'))
    return int(m.hexdigest(), 16)

def getClient(keyhash):
    mod = len(clis)
    return clis[keyhash % mod]

def getUpLua(keyhash):
    return upLuas[keyhash % len(upLuas)]

def webData2Redis(data):
    key_postfix = data['globalid'] + ':' + data['code']
    lua = getUpLua(myHash(key_postfix))
    ex_key = ex_key_prefix + key_postfix
    msg_key = msg_key_prefix + key_postfix
    msg_val = json.dumps(data)
    return lua([ex_key, msg_key], [msg_val])

def getPSubers():
    psubers = []
    for i, r in enumerate(redisConf):
        pattern = psub_pattern.format(r["db"])
        cli = clis[i]
        psuber = cli.pubsub()
        psuber.psubscribe(pattern)
        print(pattern)
        psubers.append(psuber)
    return psubers


async def listenPSub(p):
    while True:
        msg = p.get_message()
        if msg and msg['type'] == 'pmessage':
            ex_key = msg['data'].decode('utf-8')
            msg_key = ex_key.replace(ex_key_prefix, msg_key_prefix)
            postfix = ex_key.replace(ex_key_prefix, '')
            r = getClient(myHash(postfix))
            msg_val = r.get(msg_key)
            if msg_val:
                if r.delete(msg_key) > 0:
                    pushQueue(msg_val)
        await asyncio.sleep(0.001)

