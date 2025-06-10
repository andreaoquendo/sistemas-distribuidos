import base64
import pika
import uuid
import pandas as pd
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

interesses_promocoes = set()

#TODO Verificar Itinerario REST com MS_Itinerários
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

# Funcionalidade (3b)
# Função para realizar a reserva de um cruzeiro, salvando os dados em um arquivo CSV
# e publicando uma mensagem na fila de reservas
def realizar_reserva(destino, data_embarque, quantidade_passageiros, quantidade_cabines):
    file_path = 'reservas.csv'

    # Procura na planilha cruise_data o valor do cruzeiro
    def calcular_valor(data_embarque, destino, quantidade_cabines):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, '..', 'path/to/cruise_data.xlsx')
        file_path = os.path.abspath(file_path)

        df = pd.read_excel(file_path)
        df['data_embarque'] = pd.to_datetime(df['data_embarque'], format='%d/%m/%Y')
        data_embarque = pd.to_datetime(data_embarque, format='%d/%m/%Y')
        filtered_data = df[(df['destino'] == destino) & (df['data_embarque'] == data_embarque)]

        if not filtered_data.empty:
            valor_cabine = filtered_data.iloc[0]['valor_cabine']
            return valor_cabine * quantidade_cabines
        else:
            raise ValueError("Destino ou data de embarque não encontrados na planilha.")

    # Salva a reserva no arquivo CSV
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

    # Publica uma mensagem na rota reserva-criada
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    reserva_id = str(uuid.uuid4())  

    message = f"id={reserva_id}"

    channel.basic_publish(
        exchange='cruzeiros', 
        routing_key='reserva-criada', 
        body=message, 
    )

    connection.close()

    # Começa a mostrar no console o andamento da reserva
    andamento_reserva()  

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
    channel.basic_publish(exchange='cruzeiros', routing_key='reserva-cancelada', body=mensagem)
    connection.close()

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

def console_reservar():
    destino = input("Digite o destino: ")
    data_embarque = input("Digite a data de embarque (dd/mm/aaaa): ")
    quantidade_passageiros = int(input("Digite a quantidade de passageiros: "))
    quantidade_cabines = int(input("Digite a quantidade de cabines: "))
    realizar_reserva(destino, data_embarque, quantidade_passageiros, quantidade_cabines)

if __name__ == "__main__":
    print("Deseja consultar ou fazer uma reserva? (1 - Consultar, 2 - Reservar): ")
    opcao = input("Digite sua opção: ")
    if opcao == '1':
        console_consultar()
    elif opcao == '2':
        console_reservar()
    else:
        print("Opção inválida.")