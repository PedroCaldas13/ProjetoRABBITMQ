# Conversão Distribuída de Imagens com RabbitMQ

Sistema distribuído que converte imagens para escala de cinza, reduzindo o espaço ocupado por elas. A comunicação entre as partes é feita exclusivamente por filas de mensagens no RabbitMQ, e cada parte roda em seu próprio container Docker.

Atividade 01 da disciplina de Sistemas Distribuídos (COMP0470), Universidade Federal de Sergipe.

## Arquitetura

```
Clientes ──► fila "produtores" ──► Conversores ──► exchange fanout ──► fila "armazenamento1" ──► Servidor 1
            (work queue)                        "imagens_convertidas"
                                                                   └─► fila "armazenamento2" ──► Servidor 2
```

1. **Clientes (produtores):** leem as imagens de uma pasta e as enviam para a fila de imagens `produtores`. Nesse caso foi utilizada uma *work queue*.
2. **Conversores (consumidores):** pegam as imagens da fila e fazem a conversão para a escala de cinza. Eles podem ser escalados com `--scale`: vários conversores dividem o trabalho da mesma fila, cada imagem sendo processada por apenas um deles.
3. **Exchange fanout:** os conversores enviam as imagens já convertidas para o exchange `imagens_convertidas`, que envia uma cópia de cada imagem para a fila de cada servidor de armazenamento.
4. **Servidores de armazenamento:** cada servidor tem a sua própria fila e a sua própria pasta. Ambos os servidores armazenam todas as imagens, para evitar perda. Foram criados apenas dois, mas podem ser mais (veja [Adicionando mais servidores](#adicionando-mais-servidores)).

As imagens convertidas e armazenadas mantêm o mesmo nome das imagens originais.

## Tecnologias

- **Python 3.13**
- **pika**: cliente do RabbitMQ para Python
- **Pillow**: conversão das imagens para escala de cinza
- **RabbitMQ 4** (imagem oficial `rabbitmq:4-management`)
- **Docker e Docker Compose**

## Estrutura do projeto

```
.
├── clientes.py             # Produtor: lê as imagens e envia para a fila
├── consumidores.py         # Conversor: converte para escala de cinza e publica no exchange
├── armazenamento.py        # Servidor de armazenamento: salva as imagens convertidas
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── imagensClientes/
│   └── cliente1/           # Imagens de entrada do cliente 1
└── imagens_servidores/     # Criada ao rodar: uma pasta por servidor
    ├── servidor1/
    └── servidor2/
```

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e aberto.

> **Atenção:** se houver outro RabbitMQ rodando na máquina fora do compose, pare-o antes (`docker stop rabbitmq`). Caso contrário, as portas 5672 e 15672 estarão ocupadas e o compose não conseguirá subir.

## Como executar

1. Suba o RabbitMQ, os conversores e os servidores de armazenamento:

   ```bash
   docker compose up --build -d
   ```

2. Aguarde alguns segundos até os servidores de armazenamento estarem prontos. Para acompanhar:

   ```bash
   docker compose logs -f armazenamento1 armazenamento2
   ```

   Quando aparecer `Waiting for Imagens`, os servidores estão prontos. Saia dos logs com `Ctrl+C` (os containers continuam rodando).

3. Envie as imagens:

   ```bash
   docker compose run --rm clientes
   ```

   O cliente envia todas as imagens `.png` de `imagensClientes/cliente1` e encerra. O comando pode ser repetido quantas vezes for necessário.

## Como verificar

- **Imagens convertidas:** aparecem em `imagens_servidores/servidor1` e `imagens_servidores/servidor2`, em escala de cinza e com o mesmo nome das originais. As duas pastas devem ter as mesmas imagens.
- **Logs de cada parte:**

  ```bash
  docker compose logs -f
  ```

- **Painel do RabbitMQ:** http://localhost:15672 (usuário e senha: `guest`). Na aba *Queues and Streams* ficam as filas `produtores`, `armazenamento1` e `armazenamento2`. Na aba *Exchanges*, o exchange `imagens_convertidas` deve estar ligado às duas filas de armazenamento.

## Testes opcionais

**Escalabilidade (work queue):** suba mais de um conversor e envie as imagens de novo. Nos logs, os conversores se revezam nas imagens em vez de um só pegar todas.

```bash
docker compose up -d --scale consumidores=2
docker compose run --rm clientes
docker compose logs -f consumidores
```

**Redundância e durabilidade:** pare um servidor de armazenamento, envie imagens e suba-o de novo. Ele recebe as imagens enviadas enquanto estava fora, porque a fila dele é durável e guarda as mensagens.

```bash
docker compose stop armazenamento2
docker compose run --rm clientes
docker compose start armazenamento2
```

## Como encerrar

```bash
docker compose down
```

## Por que a ordem de inicialização importa?

Os servidores de armazenamento devem estar no ar antes de as imagens serem enviadas. Isso acontece porque o exchange fanout descarta as mensagens quando não há filas ligadas a ele: se um servidor de armazenamento ainda não tiver iniciado e criado a sua fila, as imagens convertidas se perdem.

Os conversores e a fila de entrada não têm esse problema, porque a fila `produtores` é durável e guarda as mensagens até algum conversor consumi-las.

No compose, essa ordem é garantida de duas formas:

- o `depends_on` faz os conversores e o cliente esperarem o RabbitMQ estar pronto (via *healthcheck*) e os servidores de armazenamento terem iniciado;
- o cliente é executado separadamente (`docker compose run`), depois que os servidores já estão prontos.

## Adicionando mais servidores

O mesmo `armazenamento.py` funciona para qualquer número de servidores: o número passado como argumento define a fila e a pasta de cada um. Para criar um terceiro servidor, basta adicionar um serviço `armazenamento3` no `compose.yaml`, copiado do `armazenamento2`, trocando o `2` por `3` no `command` e no volume.

Diferente dos conversores, os servidores de armazenamento não podem ser escalados com `--scale`: réplicas do mesmo serviço usariam a mesma fila e dividiriam as imagens entre si, em vez de cada uma guardar todas.

Um servidor novo só recebe as imagens enviadas depois que a fila dele é criada; as imagens anteriores não são reenviadas para ele.

## Execução sem Docker (opcional)

Também é possível rodar os scripts direto na máquina, com apenas o RabbitMQ em container:

```bash
docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
pip install -r requirements.txt
```

Depois, cada comando em um terminal separado, nesta ordem:

```bash
python armazenamento.py 1
python armazenamento.py 2
python consumidores.py
python clientes.py
```

## Autor

Pedro Caldas, Ciência da Computação, Universidade Federal de Sergipe.
Disciplina de Sistemas Distribuídos (COMP0470), Prof. Rafael Oliveira Vasconcelos.