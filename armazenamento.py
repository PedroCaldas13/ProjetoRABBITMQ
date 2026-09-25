#as filas aqui devem ser fixas e nao temporarias
import base64
import io
import os

import sys
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='imagens_convertidas',durable=True,exchange_type='fanout')

result = channel.queue_declare(queue='produtores', durable=True, arguments={'x-queue-type': 'quorum'})
queue_name = result.method.queue

channel.queue_bind(exchange='imagens_convertidas', queue=queue_name)

print(' [*] Waiting for Imagens. To exit press CTRL+C')

def callback(ch,method, properties, body):
    print(' [*] Received '+body)

ch.basic_ack(delivery_tag = method.delivery_tag)
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()