import csv

# Dados para inserir
dados = [
    [1, 0, "msg1"],
    [1, 1, "msg2"],
    [1, 2, "msg3"],
    [1, 3, "msg4"],
]

# Nome do arquivo CSV
nome_arquivo = "dados.csv"

# Escrevendo no arquivo CSV
with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
    escritor = csv.writer(arquivo_csv)
    # Escreve o cabeçalho
    escritor.writerow(["epoch", "offset", "data"])
    # Escreve os dados
    escritor.writerows(dados)

print(f"Arquivo '{nome_arquivo}' criado com sucesso!")
