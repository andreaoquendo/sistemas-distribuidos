from flask import Flask
from flask import request, jsonify
from ms.reserva import {
    cancelar_reserva(),
    interesses_promocoes
}

app = Flask(__name__)

@app.route("/itinerarios", methods=["GET"])
def consultar_itinerarios():
    return "<p>Hello, World!</p>"

@app.route("/itinerarios/disponibilidade", methods=["GET"])
def consultar_disponibilidade():
    return "<p>Hello, World!</p>"

@app.route("/cancelar-reserva/<reserva_id>", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    cancelar_reserva(reserva_id)
    return  jsonify({
        "mensagem": f"Reserva {reserva_id} cancelada com sucesso!"
    }), 200

@app.route("/promocoes", methods=["POST"])
def registrar_interesse():
    dados = request.get_json()
    user_id = dados.get('user_id') 
    if not usuario_id:
        return jsonify({'erro': 'user_id é obrigatório'}), 400
    interesses_promocoes.add(user_id)
    return jsonify({
        "mensagem": f"Cadastro de interesse em promoções para {user_id} concluído com sucesso!"
    }), 200

@app.route("/cancelar-promocao/<user_id>", methods=["DELETE"])
def cancelar_interesse(user_id):
    if usuario_id in interesses_promocoes:
        interesses_promocoes.discard(user_id)
        sse_subscribers.pop(user_id, None)
        return '', 200
    else:
        return jsonify({'erro': 'Cadastro de interesse não encontrado'}), 404

@app.route("/reservar", methods=["POST"])
def reservar_itinerario(itinerario_id):
    data = request.get_json()
    user_id = data.get("user_id")
    num_cabines = data.get("numero_cabines")
    num_pessoas = data.get("numero_pessoas")
    if not all([user_id, num_cabines, num_pessoas]):
        return jsonify({"error": "Parâmetros obrigatórios ausentes"}), 400
    return jsonify({
        "mensagem": f"Itinerário {itinerario_id} reservado com sucesso!",
        "user_id": user_id,
        "numero_cabines": num_cabines,
        "numero_pessoas": num_pessoas
    }), 200

@app.route("/solicitar-pagamento", methods=["POST"])
def solicitar_pagamento():
    data = request.get_json()
    user_id = data.get("user_id")
    valor = data.get("valor")
    moeda = data.get("moeda")
    reserva_id = data.get("reserva_id")
    if not all([user_id, valor]):
        return jsonify({"error": "Parâmetros obrigatórios ausentes"}), 400
    # retornar um link para o ms reserva
    return jsonify({
        "mensagem": f"Pagamento de {valor} solicitado com sucesso para o usuário {user_id}!"
    }), 200
