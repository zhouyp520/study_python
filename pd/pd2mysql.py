# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:55:34 2019

@author: zhouyuanping6
"""

import pymysql.cursors
from sqlalchemy import create_engine
import pandas as pd
import mysql.connector
import re

connect=pymysql.connect(host='10.241.21.23',user='cradmin',password='CR@zh123',db='mydb',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
sql="DROP TABLE `mydb`.`new_table2`;"
cursor=connect.cursor()
cursor.execute(sql)
cursor.close()

engine=create_engine('mysql+pymysql://cradmin:CR@zh123@10.241.21.23:3306/mydb')
sql="SELECT * FROM mydb.new_table;"
df = pd.read_sql_query(sql, engine)

df2=df[['hostname','host','ip']]
df2.to_sql('new_table2', engine, index= False)

sql="DROP TABLE `mydb`.`new_table2`;"
df1=pd.read_excel('E:\python\测试环境清单20180929.xlsx')
df1.to_sql('hostlst_ceshi', engine, index= False)

filename='E:\python\sznas1.log'
filename='E:\python\svmax.log'

lst=[]   

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
               
get_nasinfo()
df=pd.DataFrame(lst)
order=['名称','主机','IP 地址']
df3=df[order]
df3.rename(columns={"名称":"host","主机":"hostname","IP 地址":"ip"})
df4=pd.read_excel('E:\python\input\华润银行已上线业务统计.xlsx')
df6=pd.read_excel('E:\python\input\华润银行已上线业务统计.xlsx')
df5=df4.rename(columns={'系统名称/主机角色':'host','主机名':'hostname','IP地址':'ip','浮动IP/VIP':'vip','高可用':'ha','刀槽/VC':'vc','OS版本':'os','主机型号':'pn','主机序列号':'sn','所在机房':'addr','带外管理IP':'dwip','部署时间':'date'})
df7=df6.rename(columns={'系统名称/角色':'host','主机名':'hostname','业务IP':'ip','VIP':'vip','高可用':'ha','刀槽/VC':'vc','OS版本':'os','主机型号':'pn','主机序列号':'sn','所在机房':'addr','带外IP':'dwip','部署时间':'date'})
#df5=df4.rename(columns={'系统名称/角色':'host','主机名':'hostname','业务IP':'ip','VIP':'vip','带内IP':'dnip','高可用':'ha','位置':'addr','所在esxi':'esxi','OS版本':'os','主机型号':'pn','主机序列号':'sn','带外IP':'dwip','部署时间':'date'})
df5.dropna(axis=0,how='all',inplace=True) #去除空行
df7.dropna(axis=0,how='all',inplace=True) #去除空行
#df5.to_sql('host_sw', engine, index= False)
df50=df5[['host','hostname','ip','os','ha','dwip','vip']]
df51=df7[['host','hostname','ip','os','ha','dwip','vip']]
host_df=pd.concat([df50,df51])
host_df.to_sql('host', engine, index= False)

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
                
def get_szinfo(filehome,nas_dev):
    global lst
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()  
    for i in strline:
         path=i.split()[0]
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

get_nasinfo('E:\python\input\ZH_VNX7500.log','vnx7500')
get_nasinfo('E:\python\input\zh_vnx5800.log','vnx5800')
get_isiinfo('E:\python\input\SS_Isilon.log','isi_ss')
get_isiinfo('E:\python\input\ZH_Isilon.log','isi_zh')
nas_pd=pd.DataFrame(lst)
nas_pd.to_sql('nas', engine, index= False)

def get_stor2host(filename):
    global lst
    lst=[]
    file = open(filename, 'r',encoding='utf-8')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()  
    for i in strline:
        dec={}
        i=i.replace('\t',' ') 
        stor_sn='000'+i.split()[2]
        ig=i.split()[0]
        ip=i.split()[1]
        dec['stor_sn']=stor_sn
        dec['ig']=ig
        dec['ip']=ip
        lst.append(dec)

def get_storsn(filename):
    global lst
    file = open(filename, 'r',encoding='utf-8')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()  
    for i in strline:
        dec={}
        i=i.replace('\n',' ') 
        stor_sn=+i.split()[0]
        stor_name=i.split()[1]
        dec['stor_sn']=stor_sn
        dec['stor_name']=stor_name
        lst.append(dec)        
get_stor2host('E:\python\input\stor2host.txt')
stor2host_pd=pd.DataFrame(lst)
stor2host_pd.to_sql('stor2host', engine, index= False)
get_storsn('E:\python\input\storsn.log')
lst=[]
get_vmax('E:\python\mtp\svmax.log')
df.to_sql('vmax', engine, index= False)
get_storsn('E:\python\mtp\svmax.log')
vmax_df=pd.DataFrame(lst)
vmax_df.to_sql('vmax', engine, index= False)
df=pd.read_excel('E:\python\mtp\out.xlsx')
df.to_sql('stor2host', engine, index= False)

def get_netapp(filename):
    global lst
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()   
   # dec_lun={}
    dec_cap={}
    dec_ig={}
    iglst=[]
    dec_dev={}
    ig_cap={}
    for i in strline:
        if 'Controller Name' in i:
            stor=strline[strline.index(i)+3].split()[2]
        ##elif '/vol/'in i and 'fcp' in i:
            #dec_lun[i.split()[1]]=i.split()[2]
        elif 'mapped' in i:
            dec_cap[i.split()[1]]= i.split()[5][:-2]
        elif ':' in i:
            if len(i.split()) == 5:
                ig=i.split()[1]
                wwn=i.split()[4]
                dec_ig[ig]=wwn
                iglst.append(ig)
            else:
                wwn=wwn+'\n'+i.split()[0]
                dec_ig[ig]=wwn
    for i in iglst:
        dev=''
        for str in strline:
            if i in str and '/vol' in str and 'fcp' in str:
                dev=dev+'\n'+str.split()[1]
                #print(str)
        dec_dev[i]=dev[1:]
    for i in iglst:
        cap=0
        for j in dec_dev[i].split('\n'):
            if dec_cap.get(j):
                #cap=cap+int(float(dec_cap.ge(j))
                n=float(dec_cap.get(j))
                cap=cap+int(n)
                ig_cap[i]=cap
            else:
                ig_cap[i]=cap
    
    for i in iglst:
        dec={}
        dec['stor_sn']=stor
        dec['ig']=i
        dec['mv']=''
        dec['dev']=dec_dev.get(i)
        dec['pg']=''      
        dec['sg']=''
        if ig_cap.get(i):
            dec['total_gb']=ig_cap.get(i)
        else:
            dec['total_gb']=0
        dec['wwn']=dec_ig[i].replace(',','')    
        lst.append(dec) 

lst=[]        
get_netapp('E:\python\input\ss_700.log')
get_netapp('E:\python\input\ss_8200.log')
get_netapp('E:\python\input\zh_8060.log')
get_netapp('E:\python\input\zh_700.log')
get_vmax('E:\python\input\svmax.log')
stor_df=pd.DataFrame(lst)
engine=create_engine('mysql+pymysql://cradmin:CR@zh123@10.241.21.23:3306/mydb')
stor_df.to_sql('stor_cfg', engine, index= False)
df.to_excel('E:\python\output\out_nas.xls',index = False )

