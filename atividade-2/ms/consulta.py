from flask import Flask, request, jsonify
import pandas as pd

try:
    dados_df = pd.read_excel('path/to/cruise_data.xlsx', sheet_name='Página1')
except Exception as e:
    dados_df = pd.DataFrame()
    erro_carregamento = str(e)

def consultar_opcoes(destino, data_embarque, porto_embarque):
    if dados_df.empty:
        return jsonify({"erro": f"Erro ao carregar os dados: {erro_carregamento}"}), 500

    try:
        # Filtrar usando critérios recebidos
        filtro = dados_df[
            dados_df['destino'].str.strip().str.lower() == destino.strip().lower()
        ]

        if data_embarque:
            filtro = filtro[
                filtro['data_embarque'].astype(str) == data_embarque
            ]

        if porto_embarque:
            filtro = filtro[
                filtro['porto_embarque'].str.strip().str.lower() == porto_embarque.strip().lower()
            ]

        resultados = filtro.to_dict(orient='records')

        if not resultados:
            return jsonify({
                "mensagem": "Nenhum itinerário encontrado com os critérios informados.",
                "criterios": {
                    "destino": destino,
                    "data_embarque": data_embarque,
                    "porto_embarque": porto_embarque
                }
            }), 404

        return jsonify({
            "mensagem": "Itinerários encontrados com sucesso.",
            "criterios": {
                "destino": destino,
                "data_embarque": data_embarque,
                "porto_embarque": porto_embarque
            },
            "itinerarios": resultados
        })

    except Exception as e:
        return jsonify({
            "mensagem": "Erro ao processar os dados.",
            "erro": str(e)
        }), 500