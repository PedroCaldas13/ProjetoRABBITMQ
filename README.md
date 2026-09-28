Primeiramente a arquitetura funciona da seguinte maneira: os produtores(clientes) enviam
as imagens para uma fila de imagens, nesse caso foi utilizado uma work queue, após isso
os consumidores(esses que podem ser escalados com scale--) pegam as imagens e fazem a 
conversao das imagens para a escala de cinza, logo depois os consumidores enviam as 
imagens mais convertidas para um exchange que envia para os 2 servidores(criei apenas dois
podem ser mais) de armazenamento, ambos os servidores armazenam todas as imagens para evitar
perda.
Guia de uso:
Os armazenamento.py X (sendo X 1 ou 2) devem ser inicalizados primeiro,
depois os consumidores e por ultimo os clientes, porque fazer assim?
Os clientes é que mandam as imagens, ou seja, os servidores que devem estar "on-line"
para nao ter problema.
