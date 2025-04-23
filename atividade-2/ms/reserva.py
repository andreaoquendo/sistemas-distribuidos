import pika
import uuid
import pandas as pd
import os

def consultar_opcoes(destino, data_embarque, porto_embarque):
    try:
        dados_df = pd.read_excel('../path/to/cruise_data.xlsx', sheet_name='Página1')

        if dados_df.empty:
            print("Não foi possível consultar os dados.")
        
    except Exception as e:
        erro_carregamento = str(e)
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

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    reserva_id = str(uuid.uuid4())  

    message = f"id={reserva_id}, destino={destino}, data_embarque={data_embarque}, quantidade_passageiros={quantidade_passageiros}, quantidade_cabines={quantidade_cabines}, valor_total={calcular_valor(data_embarque, destino, quantidade_passageiros)}"

    channel.basic_publish(
        exchange='cruzeiros', 
        routing_key='reserva-criada', 
        body=message, 
    )

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