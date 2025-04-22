from flask import Flask, request, jsonify
import pandas as pd

def consultar_opcoes(destino, data_embarque, porto_embarque):
    try:
        dados = pd.read_excel('/path/to/cruise_data.xlsx')
    except Exception as e:
        return jsonify({"erro": f"Erro ao carregar a planilha: {str(e)}"}), 500

    dados = dados.to_dict(orient='records')

    filtered_cruises = [
        cruise for cruise in dados
        if destino in cruise.get("lugares_visitados", "").split(",") and
           data_embarque in cruise.get("datas_partida", "").split(",") and
           cruise.get("porto_embarque") == porto_embarque
    ]

    return jsonify(filtered_cruises)