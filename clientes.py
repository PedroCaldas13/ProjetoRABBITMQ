#envio as imagens para a fila de imagens
# devo criar a fila de imagens
#le as imagens do DOCKER de uma pasta e publica na fila
import base64
import json
import pika
import sys
import os
from pathlib import Path



#sending
#comeco uma comunicacao com o RABBITMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
#se quero conectar a um brocker de outra maquina devo colocar o IP dela

#criar a lista antes de enviar a mensagem
channel.queue_declare(queue='produtores',durable=True,arguments={'x-queue-type':'quorum'})
#procurar saber essas especificacoes internas


#abre o diretorio das imagens no primeiro client
#para ler todas as imagens
for imagens in Path("imagensClientes/cliente1").glob("*.png"):
    dados_imagens = imagens.read_bytes()
    nome_imagens = imagens.name
    #Transformo o dados imagens em uma string de texto
    imagens_str = base64.b64encode(dados_imagens).decode("utf-8")
    #Vou montar um dicionario sobre ela, assim eu consigo juntar com o nome_imagens
    dicionario = {"filename" : nome_imagens, "content" : imagens_str}
    #Transformando para JSON
    json_final = json.dumps(dicionario)
    channel.basic_publish(exchange='',routing_key='produtores', body= json_final,
                      properties=pika.BasicProperties(delivery_mode= pika.DeliveryMode.Persistent)) #deixo a mensagem persistente, tells RABBITMQ to save this message to disk


#aqui eu confirmo que a mensagem chegou ao RABBITMQ
connection.close()

#para abrir dois consumidores devo rodar em dois terminais diferentes
#O RABBITMQ vai enviar em sequencia, ou seja primeiro um consumidor e depois o outro(ROUND-ROBIN)