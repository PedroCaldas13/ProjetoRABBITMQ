#as filas aqui devem ser fixas e nao temporarias
import base64
import io
import os
import pathlib
import sys
import pika
import json

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='imagens_convertidas',durable=True,exchange_type='fanout')

    result = channel.queue_declare(queue='armazenamento1', durable=True, arguments={'x-queue-type': 'quorum'})
    queue_name = result.method.queue

    channel.queue_bind(exchange='armazenamento1', queue=queue_name)

    print(' [*] Waiting for Imagens. To exit press CTRL+C')

    def callback(ch,method, properties, body):
        conteudo = json.loads(body) #pego o filename e o conteudo
        bytes = base64.b64decode(conteudo)
        Path(pasta).mkdir(parents=True, exist_ok=True)
        Path(pasta).write_bytes(bytes)

        print(' [*] Received '+json.loads(body)['filename'])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__': #resolver isso
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
