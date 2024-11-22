import time
from datetime import datetime

from confluent_kafka import Producer

'''
Kafka Producer: https://docs.confluent.io/kafka-clients/python/current/overview.html#ak-producer
Kafka Consumer: https://kafka.apache.org/quickstart#quickstart_consume
'''

# connect to redis database #0
producer = Producer({'bootstrap.servers': 'localhost:9093'})
topic = 'log-channel'

# produce messages
try:
  while True:
    msg = f'Hello at time = {datetime.now()}'
    producer.produce(topic, msg.encode('utf-8'))
    producer.flush()
    print(msg)
    time.sleep(1)
except KeyboardInterrupt:
  print('\nStopped by keyboard interrupt')
finally:
  producer.flush()
