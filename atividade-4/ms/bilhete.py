import pika, os, base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

bilhetes_dir = "bilhetes"
os.makedirs(bilhetes_dir, exist_ok=True)

def gerar_bilhete(reserva_id):
    caminho = os.path.join(bilhetes_dir, f"bilhete_{reserva_id}.txt")
    with open(caminho, "w") as f:
        f.write(f"Bilhete gerado para reserva {reserva_id}\n")
    print(f"[MS Bilhete] Bilhete salvo em: {caminho}")

def escutar_pagamentos():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Escuta pagamento-aprovado
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='pagamento-aprovado')

    print('[MS Bilhete] Aguardando mensagens de pagamento...')

    def callback(ch, method, properties, body):
        reserva_id = body.decode()
        gerar_bilhete(reserva_id)
        
        channel.queue_declare(queue='bilhete-gerado')
        channel.basic_publish(exchange='cruzeiros', routing_key='bilhete-gerado', body=reserva_id)
        print(f"[MS Bilhete] Confirmação publicada na fila 'bilhete-gerado'.")


    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    escutar_pagamentos()
