# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 16:38:17 2020

@author: cradmin
"""
import pandas as pd
import time,paramiko

filen=time.strftime('%Y%m%d%H%M%S')
g_dirPath='./output/'
se_ip='10.200.210.51'
se_user='monitor'
se_pwd='123456'
lst=[]
netapp_dev={'56.18.246.115':'zh_8060',\
            '10.200.219.245':'zh_A700',\
            '56.18.246.95':'ss_A700',\
            '56.18.246.105':'ss_8200_ods'
            }


vmax_dev={'000297800787':'zh_VMAX250_A', \
          '000297800788':'zh_VMAX250_B', \
          '000297800786':'ss_VMAX250_A', \
          '000297800791':'ss_VMAX250_B', \
          '000492600457':'zh_VMAX20k', \
          '000492600458':'yh_VMAX20k', \
          }

vmax_cmd=["symaccess -sid 0787 list view |awk 'NR>5 {print$1}' |xargs -n1 symaccess -sid 0787 show view \n",
          "symaccess -sid 0788 list view |awk 'NR>5 {print$1}' |xargs -n1 symaccess -sid 0788 show view \n",
          "symaccess -sid 0791 list view |awk 'NR>5 {print$1}' |xargs -n1 symaccess -sid 0791 show view \n",
          "symaccess -sid 0786 list view |awk 'NR>5 {print$1}' |xargs -n1 symaccess -sid 0786 show view \n",
          "symaccess -sid 0457 list view |awk 'NR>5 {print$1}' |xargs -n1 symaccess -sid 0457 show view \n",
          ]

netapp_cmd=['system controller show',\
          'system chassis show',\
          'lun show',\
          'lun mapping show',\
          'lun igroup show'
          ]

def writeFile(result,filename):
    global filen
    f = open(g_dirPath+filen+'_'+filename,'a')
    f.write(result)
    f.close()


def get_vmax(filename):
    global lst,vmax_dev
    file = open(filename, 'r')  # 读取文件
    strline = file.readlines()  # 转成列表
    file.close()   
    for str in strline:
        if 'Symmetrix ID ' in str:
            dec={}
            stor=str.split(':')[1].replace('\n','').strip()
            dec['stor_sn']=stor
            dec['stor_name']=vmax_dev[stor]
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
            
def get_netapp(filename,storname):
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
            stor=strline[strline.index(i)+6].split()[2]
        ##elif '/vol/'in i and 'fcp' in i:
            #dec_lun[i.split()[1]]=i.split()[2]
        elif 'mapped' in i:
            if 'TB' in i:
                cap=i.split()[5][:-2]
                cap1=float(cap)
                dec_cap[i.split()[1]]= int(cap1)*1000
            else:
                cap=i.split()[5][:-2]
                cap1=float(cap)
                dec_cap[i.split()[1]]= int(cap1)
        elif i.count(':') == 7:
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
        dec['stor_name']=storname
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

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

def get_log(hostn,usern,pwdn,cmdn,devn):
    ssh.connect(hostname=hostn,username=usern,password=pwdn,allow_agent=False,look_for_keys=False)
    remote_conn=ssh.invoke_shell()
    remote_conn.send(cmdn)
    print(cmdn+'----------has run')
    time.sleep(10)
    output=remote_conn.recv(5000000)
    writeFile(output.decode(),devn)
    ssh.close()

def get_storagelog():
    global netapp_cmd,netapp_dev,vmax_cmd,se_ip,se_pwd,se_user
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh.connect(hostname=se_ip,username=se_user,password=se_pwd,allow_agent=False,look_for_keys=False)
    remote_conn=ssh.invoke_shell()
    print('----------start get vmax\'s log----------')
    for i in vmax_cmd:
        remote_conn.send(i)
        print(i+'----------has run')
        time.sleep(60)
    output=remote_conn.recv(5000000)
    writeFile(output.decode(),'vmax.log')
    ssh.close()
    ssh.connect(hostname=se_ip,username=se_user,password=se_pwd,allow_agent=False,look_for_keys=False)
    remote_conn=ssh.invoke_shell()
    print('----------start get netapp\'s log----------')    
    for i in netapp_dev.keys():
        for j in netapp_cmd:
            cmdn='ssh monitor@'+i+' \"'+j+'\" \n'
            remote_conn.send(cmdn)
            print(cmdn+'----------has run')
            time.sleep(10)
        output=remote_conn.recv(5000000)
        writeFile(output.decode(),netapp_dev[i]+'.log')
        output=''
    ssh.close()

def get_vmaxlog():
    global se_ip,se_user,se_pwd,vmax_cmd
    for cmd in vmax_cmd:
        get_log(se_ip,se_user,se_pwd,cmd,'vmax.log')

def get_netapplog():
    global se_ip,se_user,se_pwd,netapp_cmd,netapp_dev
    for i in netapp_dev.keys():
        for j in netapp_cmd:
           cmdn='ssh monitor@'+i+' \"'+j+'\" \n'
           get_log(se_ip,se_user,se_pwd,cmdn,netapp_dev[i]+'.log')
    
        
def get_storage():
    global lst,filen,g_dirPath,stor_df
    lst=[]
    get_vmax(g_dirPath+filen+'_vmax.log')
    for i1 in netapp_dev.keys():
        get_netapp(g_dirPath+filen+'_'+netapp_dev[i1]+'.log',netapp_dev[i1])
    stor_df=pd.DataFrame(lst)
    xlsname=g_dirPath+'storage_'+filen+'.xls'
    stor_df.to_excel(xlsname,index = False )

get_storagelog()
get_storage()