import pika, os, base64
import pandas

def escutar_reservas():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva_criada')
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva_cancelada')

    print('[MS Itinerarios] Aguardando mensagens de pagamento...')

    def callback(ch, method, properties, body):
        mensagem = body.decode()
        try:
            reserva_id = mensagem.split('=')[1]
        except ValueError:
            print("[MS Itinerarios] Erro no formato da mensagem recebida.")
            return

        # precisa somente a reserva id
        if method.routing_key == 'reserva-criada':
            # TODO: altera quantidade de cabines
            pass
        elif method.routing_key == 'reserva-cancelada':
            # TODO: aumenta quantidade de cabiens
            # TODO: deletar reserva -> no ms reserva a gente só "desativa"
            pass

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    escutar_reservas()
