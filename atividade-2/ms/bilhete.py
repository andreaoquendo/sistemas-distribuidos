import pika, os, base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

bilhetes_dir = "bilhetes"
os.makedirs(bilhetes_dir, exist_ok=True)

def verificar_assinatura(mensagem, assinatura_b64):
    key = RSA.import_key(open('keys/public_key.pem').read())
    h = SHA256.new(mensagem.encode("utf-8"))
    assinatura = base64.b64decode(assinatura_b64)
    try:
        pkcs1_15.new(key).verify(h, assinatura)
        return True
    except (ValueError, TypeError):
        return False

def gerar_bilhete(reserva_id):
    caminho = os.path.join(bilhetes_dir, f"bilhete_{reserva_id}.txt")
    with open(caminho, "w") as f:
        f.write(f"Bilhete gerado para reserva {reserva_id}\n")
    print(f"[MS Bilhete] Bilhete salvo em: {caminho}")

def gerar_mensagem_recusa(reserva_id):
    print(f"[MS Bilhete] Pagamento recusado para reserva {reserva_id}. Bilhete NÃO emitido.")

def escutar_pagamentos():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Escuta pagamento-aprovado
    channel.queue_bind(exchange='cruzeiros', queue=queue_name, routing_key='pagamento-aprovado')

    print('[MS Bilhete] Aguardando mensagens de pagamento...')

    def callback(ch, method, properties, body):
        mensagem = body.decode()
        try:
            reserva_id, assinatura = mensagem.split(':')
        except ValueError:
            print("[MS Bilhete] Erro no formato da mensagem recebida.")
            return

        if verificar_assinatura(reserva_id, assinatura):
            if method.routing_key == 'pagamento-aprovado':
                gerar_bilhete(reserva_id)
                # ✔️ Publica bilhete-gerado
                channel.queue_declare(queue='bilhete-gerado')
                mensagem_bilhete = f"id={reserva_id}"
                channel.basic_publish(exchange='cruzeiros', routing_key='bilhete-gerado', body=mensagem_bilhete)
                print(f"[MS Bilhete] Confirmação publicada na fila 'bilhete-gerado'.")
        else:
            print(f"[MS Bilhete] Assinatura inválida para reserva {reserva_id}. Ignorado.")
            gerar_mensagem_recusa(reserva_id)
            # ❗ Publica bilhete-nao-gerado
            channel.queue_declare(queue='bilhete-nao-gerado')
            mensagem = f"id={reserva_id}"
            channel.basic_publish(exchange='cruzeiros', routing_key='bilhete-nao-gerado', body=mensagem)
            print(f"[MS Bilhete] Confirmação publicada na fila 'bilhete-nao-gerado'.")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    escutar_pagamentos()
