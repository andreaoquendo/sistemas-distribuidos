# ms_marketing/app.py
from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

# Função responsável por publicar mensagens ao destino (destiny=promocoes_destiny) no RabbitMQ
def publish_sale(destiny, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
    channel.basic_publish(
        exchange='direct_logs', routing_key=destiny, body=message)
    connection.close()

# Endpoint para receber requisições POST com dados de promoção, isto é, destino e mensagem
@app.route("/sales", methods=["POST"])
def send_sale():
    data = request.json
    destiny = data.get("destiny")
    message = data.get("message", "Nenhuma promoção!")

    if not destiny:
        return jsonify({"erro": "destiny é obrigatório"}), 400

    publish_sale(destiny, message)
    return jsonify({"status": "Promoção enviada!", "destiny": destiny}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8080)
