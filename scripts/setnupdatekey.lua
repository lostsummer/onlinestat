local ex_key = KEYS[1]
local msg_key = KEYS[2]
local in_val = ARGV[1]
local msg_val = ''
local expire_sec = 30

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
        if in_time - msg_data['end'] > 2 * expire_sec * 1000 then
            redis.call('del', msg_key)
            result = {1,msg_val}
        else
            if in_time - msg_data['end'] > 1000 then
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

return result

