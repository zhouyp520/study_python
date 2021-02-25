# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 10:31:08 2020

@author: Administrator
"""

import paramiko,time

g_ip = '10.241.64.4'
g_user = 'admin'
g_password = 'password'
g_dirPath = './output'
cmd = 'switchshow'
cmds = ['switchshow', 
        'fabricshow', 
        'cfgshow', 
        'psshow', 
        'chassisshow', 
        'firmwareshow', 
        'islshow']
clilog=g_dirPath+'/'+time.strftime('%Y%m%d%H%M%S')+'.log'

def writeFile(result):
    f = open(clilog, 'a')
    f.write(result)
    f.close()
    
def writeLog(result):
    f = open(clilog, 'a')
    f.write(result + '\r\n')
    f.close()
    print(result)

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
ssh.connect(hostname=g_ip,username=g_user,password=g_password) 
for cmd in cmds:
    stdin,stdout,stderr=ssh.exec_command(cmd)
    a=stdout.read()
    writeFile(a.decode())
ssh.close()
