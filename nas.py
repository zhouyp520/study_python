# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:23:01 2020

@author: cradmin
"""

import pandas as pd
import re,time,os,paramiko

g_dirPath='./output/'
vnx7500_ip='10.200.8.60'
vnx5800_ip='10.200.8.14'
vnx_user='nasadmin'
vnx_pwd='nasadmin'
vnx_cmd='server_export ALL -list \n'
isilon_zh_ip='10.200.8.89'
isilon_ss_ip='56.18.246.61'
isilon_user='admin'
isilon_zh_pwd='admin'
isilon_ss_pwd='N4hrdxw!'
isilon_cmd='isi nfs exports list |grep System | awk \'NR>2 {print$1}\'|xargs -n1 isi nfs export view \n'
lst=[]

def writeFile(result,filename):
    if os.path.isfile(g_dirPath+filename):
        os.remove(g_dirPath+filename)
    f = open(g_dirPath+filename,'a')
    f.write(result)
    f.close()

def get_nasinfo(filename,nas_dev):
    global lst
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()  
    for i in strline:
        if 'export "' in i:
            path=i.split('"')[1]
            ipre=re.compile(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}')
            iplst=ipre.findall(i)
            iplst=list(set(iplst))
            for ipstr in iplst:
                if '0.0.0.0' in ipstr:
                    pass
                else:
                    dec={}
                    dec['ip']=ipstr
                    dec['nas_dev']=nas_dev
                    dec['nas_path']=path
                    lst.append(dec)
 
def get_isiinfo(filename,nas_dev):
    global lst
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()   
    for str in strline:
        if 'Paths: ' in str:
            dec={}
            dec['nas_dev']=nas_dev
            path=str.split(':')[1].replace('\n','').strip()
            dec['nas_path']=path
            i=strline.index(str)+2
            str1=strline[i]
            ipre=re.compile(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}')
            iplst1=ipre.findall(str1)
            for ipstr in iplst1:
                dec={}
                dec['nas_dev']=nas_dev
                dec['nas_path']=path
                dec['ip']=ipstr
                lst.append(dec) 

def get_vmax(filename):
    global lst
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()   
    for str in strline:
        if 'Symmetrix ID ' in str:
            dec={}
            stor=str.split(':')[1].replace('\n','').strip()
            dec['stor_sn']=stor
        elif 'Masking View Name ' in str:
            mv=str.split(':')[1].replace('\n','').strip()
            dec['mv']=mv
        elif 'Initiator Group Name ' in str:
            ig=str.split(':')[1].replace('\n','').strip()  
            dec['ig']=ig  
            #wwnlst=[]
            wwn=''
        elif '       WWN' in str:
            #wwnlst.append(str.split()[2]) 
            wwn=wwn+str.split()[2]+'\n'
        elif 'Port Group Name ' in str:
            #dec['wwn']=wwnlst
            dec['wwn']=wwn[:-1]
            pg=str.split(':')[1].replace('\n','').strip() 
            dec['pg']=pg
        elif 'Storage Group Name ' in str:
            sg=str.split(':')[1].replace('\n','').strip()     
            dec['sg']=sg
            #devlst=[]
            dev=''
        elif 'Not Visible' in str:
            if '      ' in str[:6]:
                pass
            else:
                #devlst.append(str[:6])
                dev=dev+str[:6]+'\n'
        elif 'Total Capacity ' in str:
            #dec['dev']=devlst
            dec['dev']=dev[:-1]
            tc=str.split()[2].replace('\n','').strip()  
            dec['total_gb']=int(int(tc)/1024)
            lst.append(dec)   

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

def get_log(hostn,usern,pwdn,cmdn,devn):
    ssh.connect(hostname=hostn,username=usern,password=pwdn,allow_agent=False,look_for_keys=False)
    remote_conn=ssh.invoke_shell()
    remote_conn.send(cmdn)
    time.sleep(10)
    output=remote_conn.recv(500000)
    writeFile(output.decode(),devn)
    ssh.close()

#收集log
get_log(vnx7500_ip,vnx_user,vnx_pwd,vnx_cmd,'vnx7500_zh.log')
get_log(vnx5800_ip,vnx_user,vnx_pwd,vnx_cmd,'vnx5800_zh.log')
get_log(isilon_zh_ip,isilon_user,isilon_zh_pwd,isilon_cmd,'isilon_zh.log')
get_log(isilon_ss_ip,isilon_user,isilon_ss_pwd,isilon_cmd,'isilon_ss.log')
#整理log
get_nasinfo(g_dirPath+'vnx7500_zh.log','vnx7500_zh')    
get_nasinfo(g_dirPath+'vnx5800_zh.log','vnx5800_zh') 
get_isiinfo(g_dirPath+'isilon_zh.log','isilon_zh')
get_isiinfo(g_dirPath+'isilon_ss.log','isilon_ss')                
nas_pd=pd.DataFrame(lst)
xlsname=g_dirPath+'nas_'+time.strftime('%Y%m%d%H%M%S')+'.xls'
nas_pd.to_excel(xlsname,index = False )