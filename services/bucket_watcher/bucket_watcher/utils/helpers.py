import json
import os
import tempfile

import pika

from .init_rabbitmq_conn import (
    consumer_conn,
    producer_conn,
    consumer_channel,
    producer_channel,
    queue_name,
    input_queue
)
from .init_minio_conn import mc

def close_all_rabbitmq_conn():
    try:
        consumer_conn.close()
        if producer_conn:
            producer_conn.close()
        return True, ''
    except Exception as e:
        return False, e

def publish(channel, queue, body):
    serialized_body = json.dumps(body)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=serialized_body,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
        )
    )
    print(f" [x] Sent '{body}'")

def callback(ch, method, properties, body):
    event = json.loads(body)
    records = event.get('Records')
    for record in records:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        _, path = tempfile.mkstemp()
        try:
            mc.fget_object(bucket_name, object_key, path)
            with open(path, 'r') as tmp:
                urls = tmp.read()
            urls = urls.strip().split()
            for url in urls:
                if url:
                    to_be_published = {'url': url, 'recursive_level': 0}
                    publish(producer_channel, input_queue, to_be_published)
        finally:
            os.remove(path)
        try:
            mc.remove_object(bucket_name, object_key)
        except Exception as e:
            print(f'{bucket_name}/{object_key} could not be removed: {e}')

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    consumer_channel.basic_consume(on_message_callback=callback, queue=queue_name, auto_ack=False)
    consumer_channel.start_consuming()