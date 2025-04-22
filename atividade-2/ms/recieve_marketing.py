import pika, sys, os

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Coloquei esses 3 destinos para o exemplo, mas o nome da routing_key vai ter que ser promocoes_destinoX
    destinies = sys.argv[1:]
    if not destinies:
        sys.stderr.write("Usage: %s [brasil] [paraguay] [colombia]\n" % sys.argv[0])
        sys.exit(1)

    for destiny in destinies:
        channel.queue_bind(
            exchange='direct_logs', queue=queue_name, routing_key=destiny)
        
    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" [x] {method.routing_key}:{body}")


    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    # TODO: Fazer o envio de emails aqui provavelmente

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)