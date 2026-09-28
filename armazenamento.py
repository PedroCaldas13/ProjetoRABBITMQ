#as filas aqui devem ser fixas e nao temporarias
import base64
import io
import os
from pathlib import Path
import sys
import pika
import json
import re

def main():

    #abrir o arquivo
    numero = sys.argv[1]
    if len(sys.argv) < 2:
        print("Deve conter um numero de identificacao apos o armazenamento.py")
        sys.exit(1)
    pasta = "imagens_servidores/servidor" + numero

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='imagens_convertidas',durable=True,exchange_type='fanout')

    Path(pasta).mkdir(parents=True, exist_ok=True)

    result = channel.queue_declare(queue='armazenamento' + numero, durable=True, arguments={'x-queue-type': 'quorum'})
    queue_name = result.method.queue

    channel.queue_bind(exchange='imagens_convertidas', queue=queue_name)

    print(' [*] Waiting for Images. To exit press CTRL+C')



    def callback(ch,method, properties, body):
        conteudo = json.loads(body) #pego o filename e o conteudo
        imagem_bytes = base64.b64decode(conteudo['content'])

        (Path(pasta)/conteudo["filename"]).write_bytes(imagem_bytes)

        print(' [*] Received '+conteudo['filename'])
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
