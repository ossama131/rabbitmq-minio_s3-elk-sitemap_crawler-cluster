import os

import pika

#AMQP variables
amqp_uri = os.environ.get('AMQP_URI')
exchange = os.environ.get('EXCHANGE')
exchange_type = os.environ.get('EXCHANGE_TYPE')
input_queue = os.environ.get('INPUT_QUEUE')
prefetch_count = int(os.environ.get('PREFETCH_COUNT', 1))

#Assert all variables are there
try:
    assert amqp_uri and exchange and exchange_type and input_queue, 'AMQP variables missing!'
except AssertionError as e:
    raise RuntimeError(e)

#Establish 2 connections to rabbitmq 
try:
    consumer_conn = pika.BlockingConnection(
        pika.URLParameters(amqp_uri)
    )
    producer_conn = pika.BlockingConnection(
        pika.URLParameters(amqp_uri)
    )
except pika.exceptions.AMQPConnectionError as e:
    raise RuntimeError(e)
except pika.exceptions.AMQPError as e:
    raise RuntimeError(e)
except pika.exceptions.AuthenticationError as e:
    raise RuntimeError(e)
except Exception as e:
    raise RuntimeError(e)


#Instantiate channel
try:
    consumer_channel = consumer_conn.channel()
    producer_channel = producer_conn.channel()
except pika.exceptions.ChannelError as e:
    raise RuntimeError(e)
except Exception as e:
    raise RuntimeError(e)


try:
    consumer_channel.exchange_declare(exchange=exchange,
                            exchange_type=exchange_type)
    result = consumer_channel.queue_declare(queue='bucket_watcher', exclusive=False)
    queue_name = result.method.queue

    consumer_channel.queue_bind(exchange=exchange,
                    queue=queue_name)
    consumer_channel.basic_qos(prefetch_count=prefetch_count)

    producer_channel.queue_declare(queue=input_queue, durable=True, arguments={'x-queue-mode': 'lazy'})

except Exception as e:
    raise RuntimeError(e)


print('Connected Succesfully to RabbitMQ!')