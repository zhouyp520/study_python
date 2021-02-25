from prometheus_client import start_http_server,Gauge
import os
g = Gauge('net_ip_ms','net_ip_ms')
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
if __name__ == '__main__':
    start_http_server(8000)
    while True:
       ipms=execCmd('ping 10.241.120.32 -c 1')
       g.set(ipms)
