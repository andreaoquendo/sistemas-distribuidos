filename = "fotinha.jpg"

try:
    with open(filename, "rb") as f:
        content = f.read()
except Exception as e:
    print(f"Erro ao ler o arquivo {filename}: {e}")
