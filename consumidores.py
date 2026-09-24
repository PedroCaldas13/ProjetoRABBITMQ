#aqui o receive vai ser aplicado, vai receber as mensagens e printa-la na tela
import base64
import io
import os

import sys
import pika
import json
from PIL import Image


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

# criando exchange,deve ser fora
    channel.exchange_declare(exchange='imagens_convertidas',durable=True,exchange_type='fanout')

    def callback(ch, method, properties, body):
        #tenho que pegar o json
        mensagem  = json.loads(body)
        #pegar o dicionario da mensagem passando as chaves
        imagens_dados = mensagem['content']
        imagens_nomes = mensagem['filename']
        #convertendo para byte
        imagem_bytes = base64.b64decode(imagens_dados)
        #ler a imagem em bytes com o pillow
        im = Image.open(io.BytesIO(imagem_bytes))
        #agora converto para a escala de cinza
        im_cinza = im.convert('L') #nao ta mais em bytes

        print(f" [x] Received {imagens_nomes}") #saber oq a funcao decode faz
        print("[x] Done")

        #preciso converter de volta para bytes para enviar com o publish(etapa 3)
        buffer = io.BytesIO()
        im_cinza.save(buffer, format="PNG") #salvo no buffer
        dados = buffer.getvalue() #pego os dados
        dados_finais = base64.b64encode(dados).decode('utf-8')  #transformo em str
        dic = {"filename": imagens_nomes,"content": dados_finais}
        #agora faco o publish no exchange
        ch.basic_publish(exchange='imagens_convertidas', routing_key='', body=json.dumps(dic),
                              properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        #nao precisa de routing_key aqui pois o fanout ja manda para todas

        #vou enviar a mensagem para o exchange, vou utilizar de um exchange fanout
        #o fanout simplesmente broadcast todas as mensagens para todas as queues que ele conhece

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
