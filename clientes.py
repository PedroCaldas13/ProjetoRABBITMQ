#envio as imagens para a fila de imagens
# devo criar a fila de imagens
#le as imagens do DOCKER de uma pasta e publica na fila
import pika
import sys

#sending
#comeco uma comunicacao com o RABBITMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
#se quero conectar a um brocker de outra maquina devo colocar o IP dela

#criar a lista antes de enviar a mensagem
channel.queue_declare(queue='produtores',durable=True,arguments={'x-queue-reply-to':'quorum'})
#procurar saber essas especificacoes internas

#nunca devo enviar a mensagem diretamente para a lista deve ter uma exchange
#a mensagem agora é arbitraria, pode vir da linha de comando
message = ''.join(sys.argv[1:]) or 'Hello World'
channel.basic_publish(exchange='',routing_key='produtores', body= message,
                      properties=pika.BasicProperties(delivery_mode= pika.DeliveryMode.Persistent)) #deixo a mensagem persistente, tells RABBITMQ to save this message to disk
print(f" [x] Sent {message}")

#aqui eu confirmo que a mensagem chegou ao RABBITMQ
connection.close()

#para abrir dois consumidores devo rodar em dois terminais diferentes
#O RABBITMQ vai enviar em sequencia, ou seja primeiro um consumidor e depois o outro(ROUND-ROBIN)