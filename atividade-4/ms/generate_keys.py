from Crypto.PublicKey import RSA

# Gera um par de chaves de 2048 bits
key = RSA.generate(2048)

# Exporta a chave privada para um arquivo
private_key = key.export_key()
with open("private_key.der", "wb") as f:
    f.write(private_key)

# Exporta a chave pública para um arquivo
public_key = key.publickey().export_key()
with open("public_key.pem", "wb") as f:
    f.write(public_key)

print("✔️ Chaves geradas com sucesso!")
