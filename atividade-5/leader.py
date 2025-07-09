import grpc
from concurrent import futures

import mensagem_pb2
import mensagem_pb2_grpc

import csv
import os
import pandas as pd

# Armazenamento interno de dados: lista de entradas do log
logs = []
current_epoch = 1
offset_counter = 0

replicas = [
    'localhost:50052',
    'localhost:50053',
    'localhost:50054'
]

replica_stubs = []

class LeaderServicer(mensagem_pb2_grpc.ClientServiceServicer):
    def EnviarDados(self, request, context):
        global offset_counter

        def reconectar_replica(index):
            print(f"[LEADER] Tentando reconectar réplica {index+1}...")
            try:
                canal = grpc.insecure_channel(replicas[index])
                grpc.channel_ready_future(canal).result(timeout=1.0)  # espera o canal ficar pronto

                stub = mensagem_pb2_grpc.ReplicaServiceStub(canal)
                replica_stubs[index] = stub
                print(f"[LEADER] Reconexão com réplica {index+1} bem-sucedida.")
                return True

            except grpc.FutureTimeoutError:
                print(f"[LEADER] Falha ao reconectar réplica {index+1} (timeout).")
                return False
            except Exception as e:
                print(f"[LEADER] Erro inesperado ao reconectar réplica {index+1}: {e}")
                return False

        def replicar(i, stub):
            try:
                response = stub.ReplicarDados(log, timeout=2.0)
                if response.recebido:
                    print(f"[LEADER] Réplica {i+1} confirmou recebimento")
                    success_count += 1
                else:
                    print(f"[LEADER] Réplica {i+1} desatualizada. Offset dela: {response.ultimo_offset}, epoch: {response.ultima_epoca}")
                    print("oi")
                    ressintonizar_replica(i, response.ultimo_offset)
                    print("oi")
            except Exception as e:
                print("oi")

        def ressintonizar_replica(index, offset):
            missing_entries = [e for e in logs if e.offset > offset]
            print(missing_entries)
            for e in missing_entries:
                try:
                    resend_response = replica_stubs[index].ReplicarDados(e, timeout=1.0)
                    if resend_response.recebido:
                        print(f"[LEADER] Réplica {i+1} sincronizada até offset {e.offset}")
                except grpc.RpcError:
                    print(f"[LEADER] Falha ao reenviar offset {e.offset} para réplica {i+1}")
                    return False
            return True

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
                print("1")
                response = stub.ReplicarDados(log, timeout=1.0)
                if response.recebido:
                    print(f"[LEADER] Réplica {i+1} confirmou recebimento")
                    success_count += 1
                else:
                    print(f"[LEADER] Réplica {i+1} desatualizada. Offset dela: {response.ultimo_offset}, epoch: {response.ultima_epoca}")
                    if ressintonizar_replica(index=i, offset=response.ultimo_offset):
                        success_count+=1
            except grpc.RpcError as e:
                print(f"[LEADER] ERRO no envio de dados...")
                if reconectar_replica(i):
                    print("Voltando a replicar...")
                    replicar(i, replica_stubs[i])

        if success_count >= len(replicas)/2:
            print("[LEADER] Quórum atingido. Confirmando gravação ao cliente.")

            commited_count = 0
            for i, stub in enumerate(replica_stubs):
                try:
                    params = mensagem_pb2.CommitParams(epoch=current_epoch, offset=offset_counter)
                    resposta = stub.CommitarDados(params)
                    if resposta.recebido:
                        commited_count+=1
                except grpc.RpcError as e:
                    print(f"[LEADER] ERRO ao fazer COMMIT na réplica {i+1}: {e.code().name}")

            if commited_count >= len(replicas)/2:

                file_exists = os.path.exists('leader.csv')
                write_header = not file_exists or os.stat('leader.csv').st_size == 0
                with open('leader.csv', mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if write_header:
                        writer.writerow(['epoch', 'offset', 'data'])
                    writer.writerow([log.epoch, log.offset, log.data])

                return mensagem_pb2.EnviarDadosResult(
                    success=True,
                    message="Dado replicado com sucesso (quórum atingido)"
                )
        
        print("[LEADER] Falha ao atingir quórum. Dado não confirmado.")
        return mensagem_pb2.EnviarDadosResult(
            success=False,
            message="Erro: não foi possível replicar para maioria"
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

if __name__ == '__main__':

    for replica in replicas:
        channel = grpc.insecure_channel(replica)
        stub = mensagem_pb2_grpc.ReplicaServiceStub(channel)
        replica_stubs.append(stub)
        
    if os.path.exists('leader.csv'):
        df = pd.read_csv('leader.csv')
        for _, row in df.iterrows():
            log_entry = mensagem_pb2.Log(epoch=int(row['epoch']), offset=int(row['offset']), data=row['data'])
            logs.append(log_entry)
            
        if not df.empty:
            current_epoch = int(df.iloc[-1]['epoch'])
            offset_counter = int(df.iloc[-1]['offset']) + 1

    serve()
