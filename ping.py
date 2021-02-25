# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 11:03:07 2020

@author: zhouyuanping6
"""

import os,sys,time

ip = '192.168.56.101'

def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()
    str=text.split('\n')
    for i in str:
        if 'Unreachable' in i:
            time=0
        elif 'time=' in i:
            time=str[1].split('=')[3].split()[0]
    return time

def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()
    return text

cmd = 'ping 192.168.56.1 -c 1'
 
aa=execCmd('ping 192.168.56.1 -c 1')

time.clock()