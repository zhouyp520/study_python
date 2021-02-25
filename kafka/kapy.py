# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 15:59:05 2021

@author: Administrator
"""

from kafka import KafkaConsumer
from kafka import KafkaProducer
import json,time
consumer = KafkaConsumer('test',bootstrap_servers='10.241.22.23:9092')
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'), bootstrap_servers='10.241.22.23:9092')

msg_dict= {
        "time": time.strftime('%Y%m%d%H%M%S'),
        "db_config": {
                "database": "test",
                "host":"localhost",
                "user":"root",
                "password":"password"
                },
                "table":"msg",
                "msg":"Hello Worlk"
                }

msg=json.dumps(msg_dict)

#future = producer.send('test', {'foo': 'bar'})
future = producer.send('test', msg)
result = future.get(timeout=60)

for msg in consumer:
    print(msg)

producer.close()
consumer.close()