import pika
import random
import time

# Funcionalidade 5
def publish_sale(destiny, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='promocoes', exchange_type='direct')
    channel.basic_publish(
        exchange='promocoes', routing_key=destiny, body=message)
    connection.close()

if __name__ == "__main__":
    destinos = ['Bahamas', 'Alaska', 'Roma']

    while True:
        destino = random.choice(destinos)
        valor_promocao = random.randint(0, 100)
        mensagem = f"Promoção de {valor_promocao}% para {destino}."
        publish_sale(destino, mensagem)
        print(f"Mensagem publicada: {mensagem}")
        time.sleep(30)