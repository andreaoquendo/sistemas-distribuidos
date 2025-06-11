import base64
import threading
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
import pika, random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import requests


def pika_pagamento(reserva_id, status):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='cruzeiros', exchange_type='direct')
    mensagem_envio = f"{reserva_id}"
    channel.basic_publish(exchange='cruzeiros', routing_key=status, body=mensagem_envio)
    connection.close()
# API
app = Flask(__name__)
CORS(app)

transacoes = {}

@app.route('/gerar-link-pagamento', methods=['GET'])
def gerar_link_pagamento():
    dados = request.json

    try:
        response = requests.get("http://localhost:5005/gerar-link-pagamento", json=dados)
    except Exception as e:
        print(f"❌ Erro ao enviar requisição para sistema externo: {e}")

    transacao_id = response.json().get("transacao_id")
    if transacao_id:
        transacoes[transacao_id] = {
            "status": "pendente",
            "dados": dados
        }

    return jsonify({"link_pagamento": response.json().get("link_pagamento")}), 200

@app.route('/webhook', methods=['POST'])
def receber_webhook():
    dados = request.json
    transacao_id = dados.get("transacao_id")
    status = dados.get("status")

    if not transacao_id or transacao_id not in transacoes.keys():
        return jsonify({"erro": "Transação não encontrada"}), 404

    # Atualiza o status da transação
    transacoes[transacao_id]["status"] = status
    reserva_id = transacoes[transacao_id]["dados"].get("reserva_id")

    print(f"🔔 Webhook recebido: {transacao_id} → {status}")
    if status =="autorizado":
        pika_pagamento(reserva_id=reserva_id, status='pagamento-aprovado')
    else:
        pika_pagamento(reserva_id=reserva_id, status='pagamento-recusado')

    return jsonify({"mensagem": "Webhook recebido com sucesso"}), 200


if __name__ == "__main__":
    # threading.Thread(target=gerenciar_reserva, daemon=True).start()
    app.run(port=5010, debug=True)