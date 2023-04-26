# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exchange_type import ExchangeType

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'co2.*'


def callback(channel, method, properties, body):
    message = json.loads(body)
    print('Received message:')
    print(message)


if __name__ == '__main__':
    credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.TOPIC)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY)

    print('Waiting for messages...')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()
