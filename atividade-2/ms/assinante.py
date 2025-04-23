import pika

def receber_notificacoes(destinos):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='promocoes', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    for destino in destinos:
        channel.queue_bind(
            exchange='promocoes', queue=queue_name, routing_key=destino)
        
    print('Esperando por alertas...')

    def callback(ch, method, properties, body):
        print(body.decode())

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    channel.start_consuming()

if __name__ == "__main__":
    opcoes = ['Bahamas', 'Alaska', 'Roma']
    print("Escolha os destinos pelo número (separados por vírgula):")
    for i, opcao in enumerate(opcoes, 1):
        print(f"{i} - {opcao}")
    
    escolhas = input("Digite sua escolha: ")
    try:
        indices = [int(i) for i in escolhas.split(',') if i.strip().isdigit()]
        destinos_escolhidos = [opcoes[i - 1] for i in indices if 1 <= i <= len(opcoes)]
        if not destinos_escolhidos:
            raise ValueError("Nenhum destino válido foi selecionado.")
    except Exception as e:
        print(f"Erro: {e}")
        exit(1)

    receber_notificacoes(destinos_escolhidos)