import pika

# Função responsável por publicar mensagens ao destino (destiny=promocoes_destiny) no RabbitMQ
def publish_sale(destiny, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
    channel.basic_publish(
        exchange='direct_logs', routing_key=destiny, body=message)
    connection.close()