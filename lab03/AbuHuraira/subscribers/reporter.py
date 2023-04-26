# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
import logging
import sys
import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEYS = ['rep.current', 'rep.average']
RECEIVER_QUEUE = 'receiver_queue'

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def on_message(channel, method, properties, body):
    logging.info(f"Received message with routing key: {method.routing_key}")
    if method.routing_key == 'rep.current':
        with open('receiver.log', 'r') as f:
            lines = f.readlines()
            last_line = lines[-1] if len(lines) > 0 else "No data received yet"
        response = f"Latest CO2 level is {json.loads(last_line)['value']}"
    elif method.routing_key == 'rep.average':
        with open('receiver.log', 'r') as f:
            lines = f.readlines()
            values = [json.loads(line)['value'] for line in lines]
            avg = sum(values) / len(values) if len(values) > 0 else 0
        response = f"Average CO2 level is {avg}"
    else:
        response = "Invalid query"
    channel.basic_publish(exchange=EXCHANGE_NAME,
                          routing_key=properties.reply_to,
                          body=response)

if __name__ == '__main__':
    credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.TOPIC)

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    for routing_key in ROUTING_KEYS:
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)

    print('[*] Waiting for queries from the control tower. Press CTRL+C to exit')
    channel.start_consuming()
