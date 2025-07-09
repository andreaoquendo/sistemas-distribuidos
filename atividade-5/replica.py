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
commited_log = []
nome = "nome_replica"
class ReplicaServicer(mensagem_pb2_grpc.ReplicaServiceServicer):
    def ReplicarDados(self, request, context):
        global replica_log

        print("Replicando os dados...")
        print(request.data)
        if os.path.exists(f'{nome}.csv'):
            replica_log = []
            print("EXISTE")
            with open(f'{nome}.csv', mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    entry = mensagem_pb2.Log(
                        epoch=int(row['epoch']),
                        offset=int(row['offset']),
                        data=row['data']
                    )
                    replica_log.append(entry)
        
        if not replica_log:
            expected_offset = 0
            expected_epoch = request.epoch
        else:
            last_entry = replica_log[-1]
            expected_offset = last_entry.offset + 1
            expected_epoch = last_entry.epoch

        
        if request.offset != expected_offset or request.epoch != expected_epoch:
            print(f"[{nome}] Inconsistência: esperado offset={expected_offset}, epoch={expected_epoch}, mas recebeu offset={request.offset}, epoch={request.epoch}")

            if request.offset < expected_offset:
                replica_log[:] = [entry for entry in replica_log if entry.offset < request.offset]
                expected_offset = request.offset
                expected_epoch = request.epoch

                with open(f'{nome}.csv', mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['epoch', 'offset', 'data'])
                    for entry in replica_log:
                        writer.writerow([entry.epoch, entry.offset, entry.data])
                print(f"[{nome}] CSV atualizado após truncamento")

            return mensagem_pb2.Ack(
                recebido=False,
                ultima_epoca=expected_epoch,
                ultimo_offset=expected_offset - 1
            )
        
        replica_log.append(request)
        print(f"[{nome}] Entrada aceita: Época={request.epoch}, Offset={request.offset}, Dado='{request.data}'")

        return mensagem_pb2.Ack(recebido=True)
    
    def CommitarDados(self, request, context):

        file_exists = os.path.exists(f'{nome}.csv')
        write_header = not file_exists or os.stat(f'{nome}.csv').st_size == 0
        print("Na hora de comitar: replica_log tem")
        for e in replica_log:
            print(e.data)
        log = replica_log[-1]
        with open(f'{nome}.csv', mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(['epoch', 'offset', 'data'])
            writer.writerow([log.epoch, log.offset, log.data])

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
    
    if len(sys.argv) != 3:
        print("Uso: python replica1.py <nome_replica> <porta>")
        sys.exit(1)
    nome = sys.argv[1]
    port = sys.argv[2]

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
