import pika
import uuid
import pandas as pd
import os

def calcular_valor(destino, quantidade_passageiros):
    return 200

def realizar_reserva(destino, data_embarque, quantidade_passageiros, quantidade_cabines):
    # TODO: Criar um link para o pagamento

    # TODO: Criar a reserva
    file_path = 'ms/reservas.csv'

    reserva_data = {
        'id': [str(uuid.uuid4())],
        'destino': [destino],
        'data_embarque': [data_embarque],
        'quantidade_passageiros': [quantidade_passageiros],
        'quantidade_cabines': [quantidade_cabines],
        'valor_total': [calcular_valor(destino, quantidade_passageiros)]
    }
    df = pd.DataFrame(reserva_data)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    # TODO: Publica uma mensagem na fila reserva-criada
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='reserva-criada', durable=True)
    reserva_id = str(uuid.uuid4())  

    message = f"id={reserva_id}, destino={destino}, data_embarque={data_embarque}, quantidade_passageiros={quantidade_passageiros}, quantidade_cabines={quantidade_cabines}, valor_total={calcular_valor(destino, quantidade_passageiros)}"

    channel.basic_publish(
        exchange='', 
        routing_key='reserva-criada', 
        body=message, 
        properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent)
    )

    connection.close()
