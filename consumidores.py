#aqui o receive vai ser aplicado, vai receber as mensagens e printa-la na tela
import os
from uuid import main
import sys
import pika
import time

def main():

#devo conectar com o RABBITMQ assim como no clientes do sent
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

#que nem antes, ter certeza que a fila existe
    channel.queue_declare(queue='produtores', durable=True, arguments={'x-queue-type': 'quorum'})  #a imagem é o ultimo
    print(' [*] Waiting for messages. To exit press CTRL+C')
#PARA VER AS LISTAS RABBITMQ E QUANTAS MENSAGEM TEM NELAS, posso fazer com uma ferramenta de privilegio
# sudo rabbitmqctl list_queues

#funcao de callback para receber as mensagens, no caso via printar os conteudos da mensagem
#fake a second worker for every dot in the message body, it will pop the messages from the queue and perform the task
    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}") #saber oq a funcao decode faz
        time.sleep(body.count(b'.'))
        print("[x] Done")
        ch.basic_ack(delivery_tag = method.delivery_tag) #o ack manual, nao perco a mensagem mesmo se eu der um CONTROL C enquanto ela estiver sendo enviada, quando o worker terminar a mensagem sera reenviada
    #o ack deve ser enviado no mesmo canal que se recebe a mensagem
#um erro facil porem terrivel é esquecer o basic_ack
#para debugar essse tipo de erro se usa:sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged, ele printa o ack

#E se o server RABBITMQ parar? A mensagem ainda pode ser perdida, para nao perder devo omarcar as listas e as mensagens como durable
    channel.basic_qos(prefetch_count=1)#nao despache uma nova mensagem a um produtor que ainda estiver processando e ack the previous one
#Vai ser despachado para oq nao tiver ocupado
#depois, preciso falar que RABBITMQ que essa funcao de callbacj particular deve receber mensagens a minha queue
    channel.basic_consume(queue='produtores', on_message_callback=callback) #no meu caso o ack deve ser manual e nao automatico
    channel.start_consuming()

#Coloco um  loop sem fim que espera dados e roda o callback quando necessario,quando fecha da um Keyboard interruption
if __name__ == '__main__': #resolver isso
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
