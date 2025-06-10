import pika

def consultar_disponibilidade(cruzeiro_id):
    pass

def atualizar_disponibilidade(reserva_id, status):
    pass

def escutar_reservas():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Escuta pagamento-aprovado
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva-criada')
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva-cancelada')

    print('[MS Itinerarios] Aguardando mensagens de reservas...')

    def callback(ch, method, properties, body):
        mensagem = body.decode()
        try:
            reserva_id = mensagem
        except ValueError:
            print("[MS Itinerarios] Erro no formato da mensagem recebida.")
            return
        
        if method.routing_key == 'reserva-criada':
            # atualizar disponibilidade...
            pass
        elif method.routing_key == 'reserva-cancelada':
            # atualizar disponibilidade...
            pass

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()