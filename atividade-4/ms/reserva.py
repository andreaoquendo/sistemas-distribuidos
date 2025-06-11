import base64
import queue
import threading
import time
from flask_cors import CORS
import pika
import uuid
import pandas as pd
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import requests
from flask import Flask, Response
from flask import request, jsonify

interesses_promocoes = set()
notificacoes_sse = {}
conexoes_status_reserva = {}


#TODO Verificar Itinerario REST com MS_Itinerários
def consultar_itinerarios_rest(destino=None, data_embarque=None, porto_embarque=None):
    url = "http://localhost:5001/consultar-itinerarios"
    params = {}
    if destino:
        params['destino'] = destino
    if data_embarque:
        params['data_embarque'] = data_embarque.strftime('%d/%m/%Y') if hasattr(data_embarque, 'strftime') else data_embarque
    if porto_embarque:
        params['porto_embarque'] = porto_embarque

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['cruzeiros']
    except Exception as e:
        print(f"Erro ao consultar itinerários via REST: {e}")
        return None

#TODO Cancelar reserva
#TODO Reserva escuta promoções
#TODO Requisitar link de pagamento por REST ao MS_Pagamento

# Funcionalidade (3a)
# Função para consultar as opções dos cruzeiros disponíveis na planilha cruise_data, com base no destino
def consultar_opcoes(destino, data_embarque, porto_embarque):
    try:
        dados_df = pd.read_excel('../path/to/cruise_data.xlsx', sheet_name='Página1')

        if dados_df.empty:
            print("Não foi possível consultar os dados.")
        
    except Exception as e:
        print("Não foi possível consultar os dados.")

    if destino:
        filtro = dados_df[
            dados_df['destino'].str.strip().str.lower() == destino.strip().lower()
        ]
    else:
        filtro = dados_df

    if data_embarque:
        filtro = filtro[
            pd.to_datetime(filtro['data_embarque'], format='%d/%m/%Y') == data_embarque
        ]

    if porto_embarque:
        filtro = filtro[
            filtro['porto_embarque'].str.strip().str.lower() == porto_embarque.strip().lower()
        ]

    resultados = filtro.to_dict(orient='records')

    if not resultados:
        print("Nenhum itinerário encontrado com os critérios informados.")
        return
    
    print("-"*100)
    print(filtro.to_string(index=False))
    print("-"*100)


def realizar_reserva(cruzeiro_id, user_id, quantidade_passageiros, quantidade_cabines):
    file_path = 'reservas.csv'

    # Procura na planilha cruise_data o valor do cruzeiro
    def calcular_valor(cruzeiro_id, quantidade_passageiros):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, 'cruise_data.xlsx')
        df = pd.read_excel(file_path)
        filtered_data = df[df['id'] == cruzeiro_id]

        if not filtered_data.empty:
            valor_pessoa = filtered_data.iloc[0]['valor_pessoa']
            return valor_pessoa * quantidade_passageiros
        else:
            raise ValueError("Cruzeiro não encontrado na planilha.")

    # Salva a reserva no arquivo CSV
    reserva_id = str(uuid.uuid4())  
    valor_total = calcular_valor(cruzeiro_id, quantidade_passageiros)
    reserva_data = {
        'id': [reserva_id],
        'user_id': [user_id],
        'cruzeiro_id': [cruzeiro_id],
        'quantidade_passageiros': [quantidade_passageiros],
        'quantidade_cabines': [quantidade_cabines],
        'valor_total': [valor_total],
        'status': ['pendente']
    }

    df = pd.DataFrame(reserva_data)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    # Publica uma mensagem na rota reserva-criada
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')

    message = f"id={reserva_id}"

    channel.basic_publish(
        exchange='cruzeiros', 
        routing_key='reserva-criada', 
        body=message, 
    )

    connection.close()

    return valor_total, reserva_id

    # Começa a mostrar no console o andamento da reserva
    # andamento_reserva()  

# Funcionalidade (3c)
# Acompanhar o status da reserva
def andamento_reserva():
    
    def remover_reserva(reserva_id):
        file_path = 'reservas.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = df[df['id'] != reserva_id]
            df.to_csv(file_path, index=False)
            print(f"Reserva {reserva_id} removida com sucesso.")
        else:
            print("Arquivo de reservas não encontrado.")

    def verificar_assinatura(reserva_id, assinatura_b64):
        chave_publica = RSA.import_key(open('keys/public_key.pem').read())
        hash_msg = SHA256.new(reserva_id.encode('utf-8'))

        try:
            pkcs1_15.new(chave_publica).verify(hash_msg, assinatura_b64)
            return True
        except (ValueError, TypeError):
            return False
    
    print("Faça seu pagamento...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')

    pagamento = channel.queue_declare(queue='', exclusive=True)
    pagamento_queue = pagamento.method.queue

    bilhete = channel.queue_declare(queue='', exclusive=True)
    bilhete_queue = bilhete.method.queue
    
    for status in ['pagamento-aprovado', 'pagamento-recusado']:
        channel.queue_bind(exchange='cruzeiros', queue=pagamento_queue, routing_key=status)
    
    for status_bilhete in ['bilhete-gerado', 'bilhete-nao-gerado']:
        channel.queue_bind(exchange='cruzeiros', queue=bilhete_queue, routing_key=status_bilhete)
        
    print('Aguardando atualização da reserva...')

    def pagamento_callback(ch, method, properties, body):
        routing_key = method.routing_key
        data = body.decode()
        reserva_id, assinatura_b64 = data.split(":", 1)
        assinatura = base64.b64decode(assinatura_b64)

        if routing_key in ['pagamento-aprovado', 'pagamento-recusado']:
            if not verificar_assinatura(reserva_id, assinatura):
                print(f"Assinatura inválida para {reserva_id}")
                print("Removendo reserva...")
                remover_reserva(reserva_id)
                return

        if routing_key == 'pagamento-aprovado':
            print(f"Pagamento aprovado para reserva {reserva_id}")
            print(f"Aguardando bilhete ser gerado...")
        elif routing_key == 'pagamento-recusado':
            print(f"Pagamento recusado para reserva {reserva_id}")
            remover_reserva(reserva_id)
            channel.stop_consuming()
            connection.close()
            return

    def bilhete_callback(ch, method, properties, body):
        routing_key = method.routing_key
        data = body.decode()
        reserva_id = data.split("=")[1]
        
        if routing_key == 'bilhete-gerado':
            print(f"[✔] Bilhete gerado para reserva {reserva_id}")
            channel.stop_consuming()
            connection.close()
        elif routing_key == 'bilhete-nao-gerado':
            print(f"[x] Bilhete NÃO gerado para reserva {reserva_id}")
            channel.stop_consuming()
            connection.close()

    channel.basic_consume(queue=pagamento_queue, on_message_callback=pagamento_callback, auto_ack=True)
    channel.basic_consume(queue=bilhete_queue, on_message_callback=bilhete_callback, auto_ack=True)
    
    channel.start_consuming()

def cancelar_reserva(reserva_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    mensagem = f"reserva={reserva_id}"
    print(f"[CANCELAMENTO] Cancelando reserva {reserva_id}")
    channel.basic_publish(exchange='cruzeiros', routing_key='reserva-cancelada', body=mensagem)
    connection.close()

def escutar_promocoes():

    def promocoes_callback(ch, method, properties, body):
        mensagem = body.decode()
        print(f"[PROMOÇÃO RECEBIDA] {mensagem}")
        for cliente_id in interesses_promocoes:
            print(f" -> Enviando promoção para cliente {cliente_id}")
            if cliente_id in notificacoes_sse:
                notificacoes_sse[cliente_id].put(mensagem)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='promocoes', exchange_type='direct')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='promocoes', queue=queue_name)

    print('[*] Escutando promoções...')
    channel.basic_consume(queue=queue_name, on_message_callback=promocoes_callback, auto_ack=True)
    channel.start_consuming()


def console_consultar():
    print("Faça uma reserva de cruzeiro!")
    opcoes = ['Bahamas', 'Alaska', 'Roma']
    print("Escolha o destino que você gostaria de ir:")
    for i, opcao in enumerate(opcoes, 1):
        print(f"{i} - {opcao}")

    destino = input("Digite o número do destino: (Tecle X para qualquer destino) ")
    if destino.strip().upper() == 'X':
        destino = None
    else:
        try:
            destino = opcoes[int(destino) - 1]
        except ValueError:
            print("Destino inválido.")
            exit(1)

    data = input("Digite a data de embarque desejada (dd/mm/aaaa) - Tecle X para qualquer data: ")

    if data.strip().upper() == 'X':
        data_embarque = None
    else:
        try:
            data_embarque = pd.to_datetime(data, format='%d/%m/%Y')
        except ValueError:
            print("Data inválida.")
            exit(1)

    porto = input("Digite o porto de embarque desejado (Tecle X para qualquer porto): ")
    if porto.strip().upper() == 'X':
        porto_embarque = None
    else:
        portos_existentes = ['Fort Lauderdale', 'Vancouver', 'Barcelona']
        if porto.strip().title() not in portos_existentes:
            print("Porto inválido.")
            exit(1)
        porto_embarque = porto.strip().title()

    consultar_opcoes(destino, data_embarque, porto_embarque)


def solicitar_pagamento(reserva_id, valor, moeda, user_id):
    print(f"[MS Reserva] Solicitando pagamento de {valor} {moeda} para o usuário {user_id}")
    url = "http://localhost:5010/gerar-link-pagamento"
    payload = {
        "reserva_id": reserva_id,
        "valor": float(valor),
        "moeda": str(moeda),
        "user_id": str(user_id)
    }
    try:
        print("oii")
        response = requests.get(url, json=payload)
        print(response.json())
    except Exception as e:
        print(f"Erro ao solicitar pagamento: {e}")
        return None
    
    return response.json().get('link_pagamento', None)

app = Flask(__name__)
CORS(app)

@app.route('/status-reserva')
def stream_status_reserva():
    reserva_id = request.args.get('reserva_id')
    if not reserva_id:
        return Response("reserva_id obrigatório\n", status=400)

    fila = queue.Queue()
    conexoes_status_reserva[reserva_id] = fila

    def eventos():
        try:
            while True:
                mensagem = fila.get()
                yield f"data: {mensagem}\n\n"
        except GeneratorExit:
            del conexoes_status_reserva[reserva_id]

    return Response(eventos(), content_type='text/event-stream')

@app.route("/itinerarios", methods=["GET"])
def consultar_itinerarios():
    destino = request.args.get('destino') or None
    data_embarque = request.args.get('data_embarque') or None
    porto_embarque = request.args.get('porto_embarque') or None

    ids = consultar_itinerarios_rest(destino, data_embarque, porto_embarque)
    if not ids:
        return jsonify({"itinerarios": []})

    # Carrega os dados do arquivo cruise_data.xlsx
    try:
        df = pd.read_excel('cruise_data.xlsx')
    except Exception as e:
        return jsonify({"erro": "Erro ao carregar dados do cruzeiro.", "detalhe": str(e)}), 500

    # Filtra os itinerários pelos ids retornados
    itinerarios = df[df['id'].astype(str).isin([str(i) for i in ids])].to_dict(orient='records')

    return jsonify({"itinerarios": itinerarios})

@app.route("/reservar", methods=["POST"])
def reservar_itinerario():
    data = request.get_json()
    user_id = data.get("user_id")
    cruzeiro_id = data.get("cruzeiro_id")
    num_cabines = data.get("numero_cabines")
    num_pessoas = data.get("numero_pessoas")
    
    if not all([user_id, num_cabines, num_pessoas]):
        return jsonify({"error": "Parâmetros obrigatórios ausentes"}), 400
    valor, reserva_id = realizar_reserva(cruzeiro_id, user_id, num_pessoas, num_cabines)
    link_pagamento= solicitar_pagamento(
        reserva_id=reserva_id,
        valor=valor,  # Exemplo de valor, deve ser calculado corretamente
        moeda="USD",
        user_id=user_id
    )

    return jsonify({
        "reserva_id": reserva_id,
        "link_pagamento": link_pagamento
    }), 200

@app.route("/cancelar-reserva/<reserva_id>", methods=["DELETE"])
def cancelar_reserva_rest(reserva_id):
    cancelar_reserva(reserva_id)
    return  jsonify({
        "mensagem": f"Reserva {reserva_id} cancelada com sucesso!"
    }), 200

@app.route("/promocoes", methods=["POST"])
def registrar_interesse():
    dados = request.get_json()
    user_id = dados.get('user_id') 
    if not user_id:
        return jsonify({'erro': 'user_id é obrigatório'}), 400
    interesses_promocoes.add(user_id)
    return jsonify({
        "mensagem": f"Cadastro de interesse em promoções para {user_id} concluído com sucesso!"
    }), 200

@app.route("/cancelar-promocao/<user_id>", methods=["DELETE"])
def cancelar_interesse(user_id):
    if user_id in interesses_promocoes:
        interesses_promocoes.discard(user_id)
        # sse_subscribers.pop(user_id, None)
        return jsonify({"mensagem": f"Interesse em promoções para {user_id} cancelado com sucesso!"}), 200
    else:
        return jsonify({'erro': 'Cadastro de interesse não encontrado'}), 404
    
@app.route('/promocoes', methods=['GET'])
def stream():
    user_id = request.args.get('user_id')
    
    if user_id not in interesses_promocoes:
        return Response("Acesso não autorizado\n", status=403)


    def gerar_eventos():
        fila = queue.Queue()
        notificacoes_sse[user_id] = fila
        try:
            while True:
                # Se o interesse for removido, encerra o stream
                if user_id not in interesses_promocoes:
                    yield "event: close\ndata: Interesse cancelado\n\n"
                    break
                try:
                    mensagem = fila.get(timeout=30)
                    yield f"data: {mensagem}\n\n"
                except queue.Empty:
                    # Mantém a conexão viva com um comentário SSE
                    yield ": keep-alive\n\n"
        finally:
            notificacoes_sse.pop(user_id, None)

    return Response(gerar_eventos(), content_type='text/event-stream')

def pika_publish(message, exchange, routing_key):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='direct')

    channel.basic_publish(
        exchange=exchange, 
        routing_key=routing_key, 
        body=message, 
    )

    connection.close()

def escutar_filas():

    def notificar_status_reserva(reserva_id, mensagem):
        fila = conexoes_status_reserva.get(reserva_id)
        if fila:
            fila.put(mensagem)
            
    def callback(ch, method, properties, body):
        reserva_id = body.decode()
        if method.routing_key == 'pagamento-recusado':
            print(f"[❌] Pagamento recusado para reserva {reserva_id}")
            message = "id=" + reserva_id
            pika_publish(message=message, exchange='cruzeiros', routing_key='reserva-cancelada')
            notificar_status_reserva(reserva_id, "❌ Pagamento recusado.")
        elif method.routing_key == 'bilhete-gerado':
            print(f"Bilhete gerado{reserva_id}")
            notificar_status_reserva(reserva_id, "🎫 Bilhete gerado com sucesso.")
        elif method.routing_key == 'pagamento-aprovado':
            print(f"[] Pagamento aprovado {reserva_id}")
            notificar_status_reserva(reserva_id, "✅ Pagamento aprovado.")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='pagamento-aprovado')
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='pagamento-recusado')
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='bilhete-gerado')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":

    threading.Thread(target=escutar_filas, daemon=True).start()
    threading.Thread(target=escutar_promocoes, daemon=True).start()
    app.run(debug=True, port=5002)
    # print("Deseja consultar ou fazer uma reserva? (1 - Consultar, 2 - Reservar): ")
    # opcao = input("Digite sua opção: ")
    # if opcao == '1':
    #     console_consultar()
    # elif opcao == '2':
    #     console_reservar()
    # else:
    #     print("Opção inválida.")