import grpc
from concurrent import futures
import time

import mensagem_pb2
import mensagem_pb2_grpc

# Armazenamento interno de dados: lista de entradas do log
logs = []
current_epoch = 1
offset_counter = 0

replicas = [
    'localhost:50052',
]

replica_stubs = []

class LeaderServicer(mensagem_pb2_grpc.ClientServiceServicer):
    def EnviarDados(self, request, context):
        global offset_counter

        log = mensagem_pb2.Log(
            epoch=current_epoch,
            offset=offset_counter,
            data=request.data
        )

        logs.append(log)
        print(f"[LEADER] Dado recebido: '{request.data}' (epoch={log.epoch}, offset={log.offset})")
        offset_counter += 1

        success_count = 0
        for i, stub in enumerate(replica_stubs):
            try:
                response = stub.ReplicarDados(log, timeout=1.0)
                if response.recebido:
                    print(f"[LEADER] Réplica {i+1} confirmou recebimento")
                    success_count += 1
                else:
                    print(f"[LEADER] Réplica {i+1} negou recebimento")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    print(f"[LEADER] TIMEOUT na réplica {i+1} (sem resposta em 1s)")
                else:
                    print(f"[LEADER] ERRO ao enviar para réplica {i+1}: {e.code().name}")

        return mensagem_pb2.EnviarDadosResult(
            success=True,
            message="Dado gravado com sucesso"
        )

    def ConsultarDados(self, request, context):
        print("[LEADER] Consulta recebida do cliente")
        return mensagem_pb2.ConsultarDadosResult(entries=log)

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mensagem_pb2_grpc.add_ClientServiceServicer_to_server(LeaderServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
    # try:
    #     while True:
    #         time.sleep(86400)  # Mantém o servidor vivo
    # except KeyboardInterrupt:
    #     print("[LEADER] Encerrando servidor...")
    #     server.stop(0)

if __name__ == '__main__':

    for replica in replicas:
        channel = grpc.insecure_channel(replica)
        stub = mensagem_pb2_grpc.ReplicaServiceStub(channel)
        replica_stubs.append(stub)
        
    serve()
