import base64
import pika, random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

# Funcionalidade (4a)
def gerenciar_reserva():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva-criada')
        
    print('Esperando reservas serem feitas...')

    def callback(ch, method, properties, body):
        reserva_id = body.decode().split('=')[1]
        print(f"Reserva recebida: {reserva_id}")
        processar_pagamento(reserva_id)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    channel.start_consuming()

# Funcionalidade (4b)
def processar_pagamento(reserva_id):
    # Simula aprovação ou recusa aleatória
    aprovado = random.choice([True, False])
    status = 'pagamento-aprovado' if aprovado else 'pagamento-recusado'

    # Mensagem a ser enviada
    mensagem = reserva_id

    #Assinatura
    key = RSA.import_key(open('keys/private_key.der').read())
    h = SHA256.new(mensagem.encode('utf-8'))
    assinatura = pkcs1_15.new(key).sign(h)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    mensagem_envio = f"{reserva_id}:{base64.b64encode(assinatura).decode('utf-8')}"
    channel.basic_publish(exchange='cruzeiros', routing_key=status, body=mensagem_envio)
    connection.close()

    if aprovado:
        print(f"[MS Pagamento] Pagamento APROVADO para reserva {reserva_id}")
    else:
        print(f"[MS Pagamento] Pagamento RECUSADO para reserva {reserva_id}")
    print(f"[MS Pagamento] Mensagem enviada na fila '{status}' com assinatura.")

if __name__ == "__main__":
    gerenciar_reserva()