import grpc
from concurrent import futures
import time
import sys

import mensagem_pb2
import mensagem_pb2_grpc
import csv
import os

# Armazena dados replicados
replica_log = []
nome = "nome_replica"
class ReplicaServicer(mensagem_pb2_grpc.ReplicaServiceServicer):
    def ReplicarDados(self, request, context):
        
        if not replica_log:
            expected_offset = 0
            expected_epoch = request.epoch
        else:
            last_entry = replica_log[-1]
            expected_offset = last_entry.offset + 1
            expected_epoch = last_entry.epoch

        
        if request.offset != expected_offset or request.epoch != expected_epoch:
            print(f"[{nome}] Inconsistência: esperado offset={expected_offset}, epoch={expected_epoch}, mas recebeu offset={request.offset}, epoch={request.epoch}")

            # NÃO aceita a entrada ainda. Informa ao líder o estado atual.
            return mensagem_pb2.Ack(
                recebido=False,
                ultima_epoca=expected_epoch,
                ultimo_offset=expected_offset - 1
            )
        else:
            # Entrada consistente
            replica_log.append(request)
            print(f"[{nome}] Entrada aceita: Época={request.epoch}, Offset={request.offset}, Dado='{request.data}'")

        return mensagem_pb2.Ack(recebido=True)
    
    def CommitarDados(self, request, context):
        # Salva os dados do replica_log em um arquivo CSV
        with open(f'{nome}.csv', mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['epoch', 'offset', 'data'])
            for entry in replica_log:
                writer.writerow([entry.epoch, entry.offset, entry.data])
        print("[RÉPLICA 1] Dados commitados e salvos em replica1_log.csv")

        return mensagem_pb2.Ack(recebido=True)


def serve(nome, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mensagem_pb2_grpc.add_ReplicaServiceServicer_to_server(ReplicaServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Réplica {nome} iniciada na porta {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    
    entrada = input("Escreva o nome e porta da réplica: ")
    nome = entrada.split(":")[0]
    port = entrada.split(":")[1]

    if os.path.exists(f'{nome}.csv'):
        with open(f'{nome}.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entry = mensagem_pb2.Log(
                    epoch=int(row['epoch']),
                    offset=int(row['offset']),
                    data=row['data']
                )
                replica_log.append(entry)

    serve(nome, port)
