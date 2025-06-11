import uuid
from flask import Flask, request, jsonify
import threading
import time
import random
import requests

app = Flask(__name__)

@app.route('/gerar-link-pagamento', methods=['GET'])
def gerar_link_pagamento():
    dados = request.json
    valor = dados.get("valor")
    moeda = dados.get("moeda")
    user_id = dados.get("user_id")

    if not all([valor, user_id, moeda]):
        return jsonify({"erro": "Valor e cliente são obrigatórios"}), 400

    transacao_id = str(uuid.uuid4())
    print(transacao_id)
    link_pagamento = f"http://sistema-externo.fake/pagar/{transacao_id}"

    webhook_thread = threading.Thread(target=simular_pagamento_e_enviar_webhook, args=(transacao_id,))
    webhook_thread.start()

    return jsonify({
        "transacao_id": transacao_id,
        "link_pagamento": link_pagamento
    }), 200

def simular_pagamento_e_enviar_webhook(transacao_id):
    print("oi")
    time.sleep(3) 
    status = random.choice(["autorizado", "recusado"])

    payload = {
        "transacao_id": transacao_id,
        "status": status,
    }

    try:
        response = requests.post("http://localhost:5010/webhook", json=payload)
        print(f"🔔 Webhook enviado: {payload}")
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")


if __name__ == '__main__':
    app.run(port=5005, debug=True)
