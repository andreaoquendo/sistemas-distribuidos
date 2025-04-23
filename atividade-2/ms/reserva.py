import pika
import uuid
import pandas as pd
import os

def calcular_valor(data_embarque, destino, quantidade_cabines):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, '..', 'path/to/cruise_data.xlsx')
    file_path = os.path.abspath(file_path)

    df = pd.read_excel(file_path)
    df['data_embarque'] = pd.to_datetime(df['data_embarque'], format='%d/%m/%Y')
    data_embarque = pd.to_datetime(data_embarque, format='%d/%m/%Y')
    filtered_data = df[(df['destino'] == destino) & (df['data_embarque'] == data_embarque)]

    if not filtered_data.empty:
        valor_pessoa = filtered_data.iloc[0]['valor_pessoa']
        return valor_pessoa * quantidade_cabines
    else:
        raise ValueError("Destino ou data de embarque não encontrados na planilha.")

def realizar_reserva(destino, data_embarque, quantidade_passageiros, quantidade_cabines):
    # TODO: Criar um link para o pagamento

    file_path = 'reservas.csv'

    reserva_data = {
        'id': [str(uuid.uuid4())],
        'destino': [destino],
        'data_embarque': [data_embarque],
        'quantidade_passageiros': [quantidade_passageiros],
        'quantidade_cabines': [quantidade_cabines],
        'valor_total': [calcular_valor(data_embarque, destino, quantidade_passageiros)]
    }
    df = pd.DataFrame(reserva_data)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    # DONE: Publicar uma mensagem na fila reserva-criada
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='reserva-criada', durable=True)
    reserva_id = str(uuid.uuid4())  

    message = f"id={reserva_id}, destino={destino}, data_embarque={data_embarque}, quantidade_passageiros={quantidade_passageiros}, quantidade_cabines={quantidade_cabines}, valor_total={calcular_valor(data_embarque, destino, quantidade_passageiros)}"

    channel.basic_publish(
        exchange='', 
        routing_key='reserva-criada', 
        body=message, 
        properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent)
    )

    connection.close()
