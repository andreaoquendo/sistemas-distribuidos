import os
import time

# Caminho da pasta que você quer monitorar
caminho_pasta = '.'

# Pega os arquivos atuais da pasta
arquivos_anteriores = set(os.listdir(caminho_pasta))

print(arquivos_anteriores)

print(f"👀 Começando a monitorar {caminho_pasta}...")

try:
    while True:
        time.sleep(2)  # tempo entre verificações (em segundos)

        arquivos_atual = set(os.listdir(caminho_pasta))

        # Detecta novos arquivos
        novos = arquivos_atual - arquivos_anteriores
        for arquivo in novos:
            print(f"📥 Novo arquivo: {arquivo}")

        # Detecta arquivos deletados
        deletados = arquivos_anteriores - arquivos_atual
        for arquivo in deletados:
            print(f"🗑️ Arquivo deletado: {arquivo}")

        # Atualiza o estado anterior
        arquivos_anteriores = arquivos_atual

except KeyboardInterrupt:
    print("⏹️ Monitoramento encerrado.")
