# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import redis
from rediscluster import RedisCluster
import time
import base64
#import os
from mimesis import Person
from pprint import pprint
import pystorage
import pexpect

g_ip = '10.241.64.4'
g_user = 'admin'
g_password = 'password'
person=Person('ja')
pprint(vars(person))
pool = redis.ConnectionPool(host='10.241.117.40', 
                            port=6379, 
                            decode_responses=True)
r = redis.Redis(host='10.241.117.40', 
                port=30001, 
                decode_responses=True,)
r.set('foo','bar')
r.get('foo')

startup_nodes = [{"host":"10.241.117.40", "port":"7001"},
                 {"host":"10.241.117.40", "port":"7002"},
                 {"host":"10.241.117.40", "port":"7003"}]

rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

def rediscluster_testset(n):
    for a in range(n):
        person=Person('zh')
        name=person.email()
        age=person.password()
#        t=time.asctime(time.localtime(time.time()))
        rc.set(name,age)
        print(rc.get(name))
        time.sleep(1)
        
rc.flushdb()
        
rc.cluster_keyslot(102)

def redis_testset(n):
    global r
    pipe=r.pipeline()
    for a in range(n):
        t=time.asctime(time.localtime(time.time()))
        pipe.set(a,t)
    pipe.execute()
    
def redis_wtest():
    a=0
    n=0
    while a==0:
        t=time.asctime(time.localtime(time.time()))
        r.set(n,t)
        n=n+1

r.flushdb()
r.shutdown()

with open("D:\python\Koala.jpg","rb") as f:
    base64_data=base64.b64encode(f.read())
    file=open('D:\python\Koala.txt','wt')
    file.write(base64_data)
    file.close
    
vnx=pystorage.VNX('file:///C:/Program Files (x86)/EMC/Navisphere CLI/NaviSECCli.exe','10.241.11.52')
vnx=pystorage.VNX()

child = pexpect.spawn('ssh '+ g_user + '@' + g_ip)

def connect():
    t1 = initTime()
    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh ' + g_user + '@' + g_ip)
    res = child.expect([pexpect.TIMEOUT, ssh_newkey, '[P|p]assword:', 'proceed.\r\n'])
    if res == 0:     # Timeout
        writeLog('连接超时：' + child.before + child.after + usedTime(t1))
        child.close(force=True)
        exit(-1)
    elif res == 1:   # new key
        child.sendline('yes')
        res = child.expect([pexpect.TIMEOUT, '[P|p]assword:'])
        if res == 0:    # Timeout
            writeLog('连接超时：' + child.before + child.after + usedTime(t1))
            child.close(force=True)
            exit(-1)
    child.sendline(g_password)
    #res = child.expect([g_user + '>',  '[P|p]assword:'])
    res = child.expect([g_user + '>',  '[P|p]assword:',  'proceed.\r\n'])
    if res == 0:
        writeLog('远程连接成功' + usedTime(t1))
        return child
    elif res == 1:
        writeLog('权限认证失败！')
        child.close(force=True)
        exit(-2)
    elif res == 2:
        child.sendcontrol('c')
	res = child.expect([g_user + '>', ])
        if res == 0:
                writeLog('远程连接成功' + usedTime(t1))
                return child
    else:
        writeLog('连接失败，没有正常返回！')
        child.close(force=True)
        exit(-3)
        

connStr = 'ssh '+ g_user + '@' + g_ip
child = pexpect.spawn(connStr)    
        