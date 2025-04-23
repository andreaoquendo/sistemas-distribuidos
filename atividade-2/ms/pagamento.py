import pika, json, random
from utils_crypto import assinar_mensagem
from flask import jsonify

def processar_pagamento(reserva_id):
    # Simula aprovação ou recusa aleatória
    aprovado = random.choice([True, False])
    status = 'pagamento-aprovado' if aprovado else 'pagamento-recusado'

    # Mensagem a ser enviada
    mensagem = {
        "id": reserva_id,
        "status": status
    }
    # Assinatura digital
    assinatura = assinar_mensagem(json.dumps(mensagem, sort_keys=True))
    mensagem["assinatura"] = assinatura

    # Envio para RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=status)
    channel.basic_publish(exchange='', routing_key=status, body=json.dumps(mensagem))
    connection.close()

    return jsonify({"status": status, "reserva_id": reserva_id})