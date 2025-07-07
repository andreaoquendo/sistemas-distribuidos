import grpc
from concurrent import futures

import mensagem_pb2
import mensagem_pb2_grpc

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
            print(f"[LEADER] Tentando reconectar replica {index+1}...")
            canal = grpc.insecure_channel(replicas[index])
            try:
                grpc.channel_ready_future(canal).result(timeout=1.0)
                stub = mensagem_pb2_grpc.ReplicaServiceStub(canal)
                replica_stubs[index] = stub
                print(f"[LEADER] Reconexão com réplica {index+1} bem-sucedida.")
                return True
            except grpc.FutureTimeoutError:
                print(f"[LEADER] Falha ao reconectar réplica {index+1}.")
                return False

        def replicar(i, stub):
            response = stub.ReplicarDados(log, timeout=1.0)
            if response.recebido:
                print(f"[LEADER] Réplica {i+1} confirmou recebimento")
                success_count += 1
            else:
                print(f"[LEADER] Réplica {i+1} desatualizada. Offset dela: {response.ultimo_offset}, epoch: {response.ultima_epoca}")
                ressintonizar_replica(i, response.ultimo_offset)

        def ressintonizar_replica(index, offset):
            print("a")
            missing_entries = [e for e in log if e.offset > offset]
            for e in missing_entries:
                try:
                    resend_response = index.ReplicarDados(e, timeout=1.0)
                    if resend_response.recebido:
                        print(f"[LEADER] Réplica {i+1} sincronizada até offset {e.offset}")
                except grpc.RpcError:
                    print(f"[LEADER] Falha ao reenviar offset {e.offset} para réplica {i+1}")

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
                    print(f"[LEADER] Réplica {i+1} desatualizada. Offset dela: {response.ultimo_offset}, epoch: {response.ultima_epoca}")
                    ressintonizar_replica(index=i, offset=response.las)
            except grpc.RpcError as e:
                print(f"[LEADER] ERRO no envio de dados...")
                if reconectar_replica(i):
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
        
    serve()
