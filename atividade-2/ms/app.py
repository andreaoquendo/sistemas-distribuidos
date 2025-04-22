# ms_marketing/app.py
from flask import Flask, request, jsonify
import pika
import pandas as pd
from consulta import consultar_opcoes
from marketing import publish_sale

app = Flask(__name__)

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

@app.route("/consulta", methods=["GET"])
def consulta():
    destino = request.args.get("destino")
    data_embarque = request.args.get("data_embarque")
    porto_embarque = request.args.get("porto_embarque")

    if not destino or not data_embarque or not porto_embarque:
        return jsonify({"erro": "destino, data_embarque e porto_embarque são obrigatórios"}), 400

    return consultar_opcoes(destino, data_embarque, porto_embarque), 200

@app.route("/efetuar_reserva", methods=["GET"])
def efetuar_reserva():
    destino = request.args.get("destino")
    data_embarque = request.args.get("data_embarque")
    porto_embarque = request.args.get("porto_embarque")

    if not destino or not data_embarque or not porto_embarque:
        return jsonify({"erro": "destino, data_embarque e porto_embarque são obrigatórios"}), 400

    # Aqui você pode adicionar a lógica para efetuar a reserva
    return jsonify({"status": "Reserva efetuada com sucesso!"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8080)
