import grpc
import mensagem_pb2, mensagem_pb2_grpc
import sys

def enviar_dados(stub, data):
    request = mensagem_pb2.EnviarDadosParams(data=data)
    response = stub.EnviarDados(request)
    print(f"[CLIENT] Enviando dado: '{data}'")
    print(f"[CLIENT] Resposta do líder: {response.message}")

def consultar_dados(stub):
    response = stub.ConsultarDados(mensagem_pb2.ConsultarDadosParams())
    print("[CLIENT] Consulta dos dados:")
    for entry in response.entries:
        print(f"  - Época: {entry.epoch}, Offset: {entry.offset}, Dado: {entry.data}")

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = mensagem_pb2_grpc.ClientServiceStub(channel)
        if len(sys.argv) > 1:
            if(sys.argv[1] == "consultar"):
                consultar_dados(stub)
            else: 
                mensagem = " ".join(sys.argv[1:])
                enviar_dados(stub, mensagem)
        else:
            print("Uso: python client.py <mensagem>")

if __name__ == '__main__':
    main()
