# 概述

__功能__： 根据web端连续发送的心跳起止点，统计用户连续在线的时间段，并携带其他页面信息，推送到业务处理下游供业务数据分析

__依赖__：Redis 缓存， 配置中打开
```
notify-keyspace-events Ex
```

# 部署结构

![arch](http://ooyi4zkat.bkt.clouddn.com/onlinestat.png)

# 数据接口

## 上游 

Web端心跳数据：http get 请求参数， 例如
```URL
http://online.tongji.emoney.cn/page/onlinetime?globalid=E96E6A8E-EBC4-03D0-E9FB-C8FBD6B9FE07&code=1CC378329905FF776C4E6BB384743762&appid=10094&clientid=0&pid=200000303&tid=184&sid=1239144&uid=2015812254&time=1528682099498
```
数据说明：

| 参数  |  说明   |
| ---- | ---- |
|globalid|全局ID|
|code |系统Code|
|time|时间戳（unix毫秒数）|
|appid|应用id|
|clientid|客户端ID|
|pid|金融平台PID|
|sid|金融平台SID |
|tid|金融平台TID|
|uid|金融平台UID/系统用户ID|

每一条记录表示 web端发送的一次心跳数据，告知服务器用户尚在页面停留

## 下游

Redis 队列元素， json 格式， 例如
```json
{
  "pid": "200000303",
  "code": "1CC378329905FF776C4E6BB384743762",
  "uid": "2015812254",
  "begin": "1528682099498",
  "appid": "10094",
  "end": "1528682099498",
  "tid": "184",
  "clientid": "0",
  "globalid": "E96E6A8E-EBC4-03D0-E9FB-C8FBD6B9FE07",
  "sid": "1239144"
}
```
数据说明：

| key  |  说明   |
| ---- | ---- |
|globalid|全局ID|
|code |系统Code|
|begin|开始时间|
|end|结束时间|
|appid|应用id|
|clientid|客户端ID|
|pid|金融平台PID|
|sid|金融平台SID |
|tid|金融平台TID|
|uid|金融平台UID/系统用户ID|

每一条数据表明用户在页面驻留的连续时段

# 部署

## 环境

linux
python3.6
```
pip install redis
pip install sanic
pip install pyyaml
```

## 运行

```
# 配置文件 app/onlinestat.yml, 不详述
python -m app.onlinestat
```

## docker 打包

正式环境
```
./build.sh
```
测试镜像
```
./build.sh test
```

# 附注

## 参考文档

- [Redis Keyspace Notifications](https://redis.io/topics/notifications)
