import os

import pika


#amqp uri to initiate connections
amqp_uri = os.environ.get('AMQP_URI')

#queue names to be used
input_queue = os.environ.get('INPUT_QUEUE')
output_queue = os.environ.get('OUTPUT_QUEUE')
logs_queue = os.environ.get('LOGS_QUEUE')

#By default process one url at a time
prefetch_count = int(os.environ.get('PREFETCH_COUNT', 1))


#Assert that AMQP URI and all Queues are provided
try:
    assert amqp_uri, 'AMQP URI is not set!'
    assert input_queue and output_queue and logs_queue, 'Queue names are not provided!'
except AssertionError as e:
    raise RuntimeError(e)

#Open 4 connections to RabbitMQ for different processes
try:
    input_consumer_conn = pika.BlockingConnection(
        pika.URLParameters(amqp_uri)
    )

    input_producer_conn = pika.BlockingConnection(
        pika.URLParameters(amqp_uri)
    )

    output_producer_conn = pika.BlockingConnection(
        pika.URLParameters(amqp_uri)
    )

    logs_producer_conn = pika.BlockingConnection(
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

#Instantiate channels
try:
    input_consumer_channel = input_consumer_conn.channel()
    input_producer_channel = input_producer_conn.channel()
    output_producer_channel = output_producer_conn.channel()
    logs_producer_channel = logs_producer_conn.channel()
except pika.exceptions.ChannelError as e:
    raise RuntimeError(e)
except Exception as e:
    raise RuntimeError(e)

#Queue declaration
try:
    input_consumer_channel.queue_declare(queue=input_queue, durable=True, arguments={'x-queue-mode': 'lazy'})
    input_consumer_channel.basic_qos(prefetch_count=prefetch_count)

    output_producer_channel.queue_declare(queue=output_queue, durable=True, arguments={'x-queue-mode': 'lazy'})
    logs_producer_channel.queue_declare(queue=logs_queue, durable=True, arguments={'x-queue-mode': 'lazy'})
except Exception as e:
    raise RuntimeError(e)


print('Connected Succesfully to RabbitMQ!')