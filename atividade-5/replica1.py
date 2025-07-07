import grpc
from concurrent import futures
import time
import sys

import mensagem_pb2
import mensagem_pb2_grpc

# Armazena dados replicados
replica_log = []

class ReplicaServicer(mensagem_pb2_grpc.ReplicaServiceServicer):
    def ReplicarDados(self, request, context):
        replica_log.append(request)
        print(f"[RÉPLICA 1] Recebido: Época={request.epoch}, Offset={request.offset}, Dado='{request.data}'")
        return mensagem_pb2.Ack(recebido=True)

    # def CommitData(self, request, context):
    #     # Por enquanto, não implementado
    #     print(f"[RÉPLICA 1] Commit recebido (Época={request.epoch}, Offset={request.offset})")
    #     return mensagem_pb2.Ack(received=True)

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mensagem_pb2_grpc.add_ReplicaServiceServicer_to_server(ReplicaServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Réplica (1) iniciada na porta {port}")
    server.wait_for_termination()
    # try:
    #     while True:
    #         time.sleep(86400)
    # except KeyboardInterrupt:
    #     print(f"[RÉPLICA] Encerrando servidor...")
    #     server.stop(0)

if __name__ == '__main__':
    port = 50052
    serve(port)
