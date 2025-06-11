import pika
import random
import time

# Funcionalidade 5
def publish_sale(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='promocoes', exchange_type='fanout')
    channel.basic_publish(exchange='promocoes', routing_key='', body=message)
    connection.close()

if __name__ == "__main__":

    while True:
        mensagem = input("Digite a mensagem de promocao: ")
        publish_sale(mensagem)
        print(f"Mensagem publicada: {mensagem}")
