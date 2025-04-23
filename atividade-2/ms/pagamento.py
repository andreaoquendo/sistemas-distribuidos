import pika, random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def processar_pagamento(reserva_id):
    # Simula aprovação ou recusa aleatória
    aprovado = random.choice([True, False])
    status = 'pagamento-aprovado' if aprovado else 'pagamento-recusado'

    # Mensagem a ser enviada
    mensagem = status

    #Assinatura
    key = RSA.import_key(open('private_key.der').read())
    h = SHA256.new(messagem)
    assinatura = pkcs1_15.new(key).sign(h)

    # Envio para RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=status)
    channel.basic_publish(exchange='', routing_key=status, body=json.dumps(mensagem))
    connection.close()

    return (assinatura)