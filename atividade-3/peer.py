import threading
import time
from enum import Enum
import random  # no topo do arquivo


# saved as greeting-server.py
import Pyro5.api

class Estado(Enum):
        CANDIDATO = 1
        SEGUIDOR = 2
        TRACKER = 3

class PeerMaker(object):
    def __init__(self):
        self.name = "peer1"
        self.is_tracker = True
        self.tracker_uri = None
        self.arquivos = {}
        self.state = Estado.TRACKER
        self.epoca = 1
        self.ultimo_heartbeat = time.time()
    
    def enviar_heartbeat(self):
        while self.is_tracker:
            ns = Pyro5.api.locate_ns()
            all_peers = ns.list()
            for name, uri in all_peers.items():
                if name != self.name:  # não envia pra si mesmo
                    try:
                        peer = Pyro5.api.Proxy(uri)
                        peer.receber_heartbeat()
                    except Exception as e:
                        print(f"Erro ao enviar heartbeat para {name}: {e}")
            time.sleep(0.1)  # 100ms
    
    @Pyro5.api.expose
    @Pyro5.api.oneway
    def receber_heartbeat(self):
        self.ultimo_heartbeat = time.time()
        print(f"Recebi heartbeat em {self.name}")
    
    def escutar_heartbeat(self):
        # Timer aleatório entre 150 e 300ms
        timeout = 0.15 + (0.15 * random.random())  # em segundos
        while not self.is_tracker:
            if time.time() - self.ultimo_heartbeat > timeout:
                print(f"[{self.name}] Tracker falhou! Tentando eleição ou novo tracker...")
                # Aqui você pode chamar sua lógica de eleição ou failover
                break
            time.sleep(0.05)




    @Pyro5.api.expose
    def cadastrar_arquivos(self, nome, arquivos):
        print("oiiiii")
        try:
            self.arquivos[nome] = arquivos
        except Exception as e :
            print("deu erro")
            print(e)
        
        print(f"Arquivos cadastrados: {self.arquivos}")
    
    @Pyro5.api.expose
    def get_is_tracker(self):
        print("Me perguntaram se eu sou o tracker")
        return self.is_tracker
    
    @Pyro5.api.expose
    @Pyro5.api.callback
    def procurar_arquivo(self, nome_arquivo):
        print(f"Procurando arquivo {nome_arquivo}")
        for peer_nome in self.arquivos.keys():
            for arquivo in self.arquivos[peer_nome]:
                if(nome_arquivo == arquivo):
                    print(peer_nome)
                    # fazer callback
                    return peer_nome
        
        return "-1"
    
    def procurar_tracker(self):
        if not self.is_tracker:
            if (self.name == "peer1"):
                print("Tentar procurar o tracker 1")
                peer = Pyro5.api.Proxy(f"PYRONAME:peer2")
            else:
                print("Tentar procurar o tracker 2")
                peer = Pyro5.api.Proxy(f"PYRONAME:peer1")
            
            print(f"Encontrou o tracker: {peer}")
            if peer.get_is_tracker():
                self.tracker_uri = peer
                print(self.tracker_uri)
        else:
            print("Eu sou o tracker")
            ns = Pyro5.api.locate_ns()
            print("listaaaa")
            print(ns.list())
            # a gente faz um loop nesses ns.list pra enviar o heartbeat 
            print("fim da listaaa")

    def server(self):
        daemon = Pyro5.server.Daemon()         # make a Pyro daemon
        ns = Pyro5.api.locate_ns()            # find the name server
        uri = daemon.register(PeerMaker)   # register the greeting maker as a Pyro object
        ns.register(self.name, uri)   # register the object with a name in the name server

        print("Ready.")
        daemon.requestLoop()              # start the event loop of the server to wait for calls
    
    @Pyro5.api.expose
    def atualizar_tracker(self, nome_tracker):
        print(f"{self.name} agora reconhece {nome_tracker} como novo tracker")
        self.tracker_uri = Pyro5.api.Proxy(f"PYRONAME:{nome_tracker}")
        self.is_tracker = False
        self.state = Estado.SEGUIDOR

    def anunciar_novo_tracker(self):
        ns = Pyro5.api.locate_ns()
        peers = ns.list()

        for nome, uri in peers.items():
            if nome != self.name:
                try:
                    peer = Pyro5.api.Proxy(uri)
                    peer.atualizar_tracker(self.name)
                except Exception as e:
                    print(f"Erro ao avisar novo tracker para {nome}: {e}")

    def iniciar_eleicao(self):
    self.state = Estado.CANDIDATO
    self.epoca += 1
    self.votos_recebidos = 1  # vota em si mesmo

    ns = Pyro5.api.locate_ns()
    peers = ns.list()

    for nome, uri in peers.items():
        if nome != self.name:
            try:
                peer = Pyro5.api.Proxy(uri)
                voto = peer.votar(self.epoca, self.name)
                if voto:
                    self.votos_recebidos += 1
            except Exception as e:
                print(f"Erro ao pedir voto de {nome}: {e}")
    
    if self.votos_recebidos > len(peers) // 2:
        print(f"{self.name} virou TRACKER na época {self.epoca}")
        self.state = Estado.TRACKER
        self.is_tracker = True
        self.tracker_uri = None
        self.anunciar_novo_tracker()
    else:
        print(f"{self.name} perdeu a eleição")
        self.state = Estado.SEGUIDOR

    
    def run(self):
        server_thread = threading.Thread(target=self.server)
        client_thread = threading.Thread(target=self.procurar_tracker)

        server_thread.start()
        client_thread.start()

        if self.is_tracker:
            heartbeat_thread = threading.Thread(target=self.enviar_heartbeat)
            heartbeat_thread.start()
        else:
            escuta_thread = threading.Thread(target=self.escutar_heartbeat)
            escuta_thread.start()

        server_thread.join()
        client_thread.join()

        # timer_thread = threading.

peer = PeerMaker()
peer.run()