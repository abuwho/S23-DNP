# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exchange_type import ExchangeType

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'

if __name__ == '__main__':
    credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.TOPIC)

    message = {
        'sensor_id': 'co2_sensor_1',
        'co2_level': 1000,
        'status': 'warning'
    }

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key='co2.sensor_1',
        body=json.dumps(message)
    )

    connection.close()
