import threading
import pika, os, base64
import pandas as pd
from enum import Enum
from flask import Flask
from flask import request, jsonify


class TipoReserva(Enum):
    CANCELAMENTO = "reserva-cancelada"
    AGENDAMENTO = "reserva-criada"

def consultar_cruzeiro(destino, data_embarque, porto_embarque):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir , 'cruise_data.xlsx')
    file_path = os.path.abspath(file_path)

    df = pd.read_excel(file_path)

    # Filtra os cruzeiros com base nos critérios fornecidos
    cruzeiros_filtrados = df

    if destino is not None:
        cruzeiros_filtrados = cruzeiros_filtrados[cruzeiros_filtrados['destino'] == destino]
    if data_embarque is not None:
        cruzeiros_filtrados = cruzeiros_filtrados[cruzeiros_filtrados['data_embarque'] == data_embarque]
    if porto_embarque is not None:
        cruzeiros_filtrados = cruzeiros_filtrados[cruzeiros_filtrados['porto_embarque'] == porto_embarque]

    if cruzeiros_filtrados.empty:
        print("[MS Itinerarios] Nenhum cruzeiro encontrado com os critérios fornecidos.")
        return []

    return cruzeiros_filtrados['id'].tolist()

def procurar_info_cabines(reserva_id):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    reservas_file_path = os.path.join(base_dir, 'reservas.csv')
    reservas_file_path = os.path.abspath(reservas_file_path)
    reservas_df = pd.read_csv(reservas_file_path, on_bad_lines='skip')

    reserva = reservas_df[reservas_df['reserva_id'] == reserva_id]

    if reserva.empty:
        print(f"[MS Itinerarios] Reserva com ID {reserva_id} não encontrada.")
        return
    num_cabines = int(reserva['quantidade_cabines'])
    cruzeiro_id = reserva['cruzeiro_id']

    return {
        'num_cabines': num_cabines,
        'cruzeiro_id': cruzeiro_id
    }

def alterar_quantidade_cabines(cruzeiro_id, num_cabines, motivo):
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, 'cruise_data.xlsx')
    file_path = os.path.abspath(file_path)

    df = pd.read_excel(file_path)
    cruzeiro = df[df['id'] == cruzeiro_id]

    if cruzeiro.empty:
        print(f"[MS Itinerarios] Cruzeiro com ID {cruzeiro_id} não encontrado.")
        return

    # Atualiza a quantidade de cabines
    index = cruzeiro.index[0]
    if motivo == TipoReserva.AGENDAMENTO.value:
        df.at[index, 'numero_cabines'] -= num_cabines
    elif motivo == TipoReserva.CANCELAMENTO.value:
        print("cancelandoooo")
        print(cruzeiro.info())    
        print(df.at[index, 'numero_cabines'])
        df.at[index, 'numero_cabines'] += num_cabines


    # Salva as alterações no arquivo
    df.to_excel(file_path, index=False)
    print(f"[MS Itinerarios] Quantidade de cabines atualizada para o cruzeiro {cruzeiro_id}.")

def escutar_reservas():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva-criada')
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='reserva-cancelada')

    print('[MS Itinerarios] Aguardando mensagens de reserva...')

    def callback(ch, method, properties, body):
        mensagem = body.decode()
        print(f"[MS Itinerarios] Mensagem recebida: {mensagem}")
        try:
            reserva_id = mensagem.split('=')[1]
            print(f"[MS Itinerarios] ID da reserva: {reserva_id}")
            base_dir = os.path.abspath(os.path.dirname(__file__))
            reservas_file_path = os.path.join(base_dir, 'reservas.csv')
            reservas_file_path = os.path.abspath(reservas_file_path)
            print(reservas_file_path)
            reservas_df = pd.read_csv(reservas_file_path, on_bad_lines='skip', index_col=False)
            reserva = reservas_df[reservas_df['id'] == reserva_id]
            reserva_dict = reserva.iloc[0].to_dict() if not reserva.empty else {}
            print(reserva_dict)
            
            print(5)

        except Exception as e:
            print(f"[MS Itinerarios] Erro ao processar a mensagem: {e}")
            return
        # 1. Ve o que tem na reserva, ve o id do cruzeiro e a quantidade de cabines

        if method.routing_key == 'reserva-criada':
            alterar_quantidade_cabines(cruzeiro_id=int(reserva_dict['cruzeiro_id']), num_cabines=reserva_dict['quantidade_cabines'], motivo=TipoReserva.AGENDAMENTO.value)
            pass
        elif method.routing_key == 'reserva-cancelada':
            print(f"cruzeiro_id na reserva: {int(reserva_dict['cruzeiro_id'])}, tipo: {type(reserva['cruzeiro_id'])}")
            print(f"[MS Itinerarios] Cancelando reserva com ID {reserva_id}.")
            alterar_quantidade_cabines(cruzeiro_id=int(reserva_dict['cruzeiro_id']), num_cabines=reserva_dict['quantidade_cabines'], motivo=TipoReserva.CANCELAMENTO.value)
            reservas_df = reservas_df[reservas_df['id'] != reserva_id]
            reservas_df.to_csv(reservas_file_path, index=False)

        # numero_cabines = reserva.iloc[0]['numero_cabines']

        # base_dir = os.path.abspath(os.path.dirname(__file__))
        # file_path = os.path.join(base_dir, '..', 'cruise_data.xlsx')
        # file_path = os.path.abspath(file_path)
        # df = pd.read_excel(file_path)

        # # precisa somente a reserva id
        # cruzeiro_id, num_cabines = procurar_info_cabines(reserva_id)
        # if method.routing_key == 'reserva-criada':
        #     alterar_quantidade_cabines(cruzeiro_id, num_cabines, TipoReserva.AGENDAMENTO)           
        # elif method.routing_key == 'reserva-cancelada':
        #     alterar_quantidade_cabines(cruzeiro_id, num_cabines, TipoReserva.CANCELAMENTO)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/consultar-itinerarios", methods=["GET"])
    def consultar_itinerarios():
        print(request.args)
        destino = request.args.get('destino') or None
        data_embarque = request.args.get('data_embarque') or None
        porto_embarque = request.args.get('porto_embarque') or None 
        
        cruzeiros = consultar_cruzeiro(destino, data_embarque, porto_embarque)
        return jsonify({'cruzeiros': cruzeiros})

    thread_reservas = threading.Thread(target=escutar_reservas, daemon=True)
    thread_reservas.start()

    app.run(debug=True, port=5001)

