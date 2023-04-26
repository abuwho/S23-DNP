# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
from datetime import datetime
import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'co2.sensor'

def send_sensor_data(co2_level):
    # Create a connection and channel to RabbitMQ
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the exchange and queue
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.topic)
    channel.queue_declare(queue='co2', durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue='co2', routing_key='co2.*')

    # Create a JSON payload
    data = {
        'time': str(datetime.now()),
        'value': co2_level,
    }
    payload = json.dumps(data)

    # Publish the payload to the queue
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY, body=payload)

    # Close the connection
    connection.close()

if __name__ == '__main__':
    while True:
        try:
            co2_level = int(input('Enter CO2 level: '))
            send_sensor_data(co2_level)
        except ValueError:
            print('Invalid input, please enter an integer.')
