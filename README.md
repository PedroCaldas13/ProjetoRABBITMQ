Primeiramente a arquitetura funciona da seguinte maneira: os produtores(clientes) enviam
as imagens para uma fila de imagens, nesse caso foi utilizado uma work queue, após isso
os consumidores(esses que podem ser escalados com --scale) pegam as imagens e fazem a 
conversao das imagens para a escala de cinza, logo depois os consumidores enviam as 
imagens mais convertidas para um exchange que envia para os 2 servidores(criei apenas dois
podem ser mais) de armazenamento, ambos os servidores armazenam todas as imagens para evitar
perda.

Guia de uso:
Para subir o compose: 
docker compose up --build -d;
docker compose run --rm clientes;
onde conferir o resultado (imagens_servidores/servidor1 e servidor2);
a UI em localhost:15672 (guest/guest);
docker compose up -d --scale consumidores=2 pra escalar;
docker compose down pra encerrar. 

Os armazenamento.py X (sendo X 1 ou 2) devem ser inicalizados primeiro,
depois os consumidores e por ultimo os clientes, porque fazer assim?
O exchange fanout descarta mensagens quando nao há filas ligadas a ele. 
Se o armazenamento ainda nao tiver iniciado e criado as suas filas as imagens convertidas
se perdem, conversores e a fila de entrada nao tem esse problema, porque a fila produtores
é duravel e guarda as mensagens ate "alguém" consumir.
