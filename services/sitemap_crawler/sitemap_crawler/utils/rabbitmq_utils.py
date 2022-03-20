import json

import pika

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
    #print(f" [x] Sent '{body}'")


def start_consuming(channel, queue, callback):
    channel.basic_consume(
        queue=queue,
        on_message_callback=callback
    )
    channel.start_consuming()