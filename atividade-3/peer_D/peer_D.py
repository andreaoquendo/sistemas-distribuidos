import threading
import time
from enum import Enum
import random  # no topo do arquivo
import os
import base64
import Pyro5.api

class State(Enum):
    CANDIDATE = "ESTADO CANDIDATO"
    FOLLOWER = "ESTADO SEGUIDOR"
    TRACKER = "ESTADO TRACKER"

class PeerMaker(object):
    def __init__(self):
        # names
        self.name = "PEER_D"

        # is the one tracking
        self.files = {}
        self.last_heartbeat = time.time()

        # is a follower
        self.tracker_uri = None
        self.tracker_name = None

        # voting states
        print(f"Estou virando tracker 1")
        self.state = State.FOLLOWER
        self.epoca = 1
        self.voted = False
        
        
    ## TRACKER
    def send_heartbeat(self):
        print(f"[{self.name}] Listen to my heart")

        while self.state == State.TRACKER:
            ns = Pyro5.api.locate_ns()
            all_peers = ns.list()
            for name, uri in all_peers.items():
                if name != self.name and name != "Pyro.NameServer":
                    try:
                        peer = Pyro5.api.Proxy(uri)
                        # print(f"ESTADO: {self.state}")
                        peer.receive_last_heartbeat(self.epoca, self.name)
                    except Exception as e:
                        print(f"Erro ao enviar heartbeat para {name}: {e}")
                        ns.remove(name)
            time.sleep(0.05)  # 100ms

    ## FOLLOWER - HEARTBEAT
    @Pyro5.api.expose
    @Pyro5.api.oneway
    def receive_last_heartbeat(self, epoca, tracker_name):
        if epoca > self.epoca:
            print(f"{self.name} agora reconhece {tracker_name} como novo tracker na epoca {self.epoca}")
            self.epoca = epoca
            self.tracker_uri = Pyro5.api.Proxy(f"PYRONAME:{tracker_name}")
            self.tracker_name = tracker_name
            self.state = State.FOLLOWER

            self.send_files(self.tracker_uri)
            escuta_thread = threading.Thread(target=self.listen_heartbeat)
            escuta_thread.start()

        self.last_heartbeat = time.time()
        # print(f"Recebi heartbeat em {self.name}")
    
    ## FOLLOWER
    def listen_heartbeat(self):
        timeout = random.uniform(0.15, 0.3) 
        while self.state == State.FOLLOWER:
            
            elapsed = time.time() - self.last_heartbeat

            if elapsed > timeout:
                print(f"[{self.name}] Tracker falhou! Tentando eleição ou novo tracker...")
                self.start_election()
                break

            time.sleep(0.1)
    

    ## FOLLOWER
    @Pyro5.api.expose
    @Pyro5.api.callback
    def search_file(self, target_file):
        print(f"Looking for {target_file}")
        for peer_name in self.files.keys():
            for filename in self.files[peer_name]:
                if(filename == target_file):
                    return peer_name
        
        return ""

    ## FOLLOWER 
    def send_files(self, tracker_uri):
        path = "."
        current_files = set(os.listdir(path))
        print(f"[{self.name}] Tentando cadastrar arquivos")
        tracker_uri.register_files(self.name, list(current_files))
    
    ## TRACKER
    @Pyro5.api.expose
    def register_files(self, peer_name, filenames):
        print(f"[{self.name}] Tentando registrar arquivos de {peer_name}")
        try:
            self.files[peer_name] = filenames
        except Exception as e :
            print(f"[{self.name}] Erro ao tentar registrar arquivos de {peer_name}")

        print(f"Arquivos cadastrados: {self.files}")
    
    def register_own_files(self):
        print(f"[{self.name}] Tentando registrar meus próprios arquivos")

        path = "."
        current_files = set(os.listdir(path))
        try:
            self.files[self.name] = list(current_files)
        except Exception as e :
            print(f"[{self.name}] Erro ao tentar registrar meus próprios arquivos")

        print(f"Arquivos cadastrados: {self.files}")

    ## EVERY PEER
    @Pyro5.api.expose
    def get_is_tracker(self):
        print("Me perguntaram se eu sou o tracker")
        return self.state == State.TRACKER
    
    ## EVERY PEER
    def search_tracker(self):
        if self.state == State.TRACKER:
            print(f"[{self.name}] Eu sou o tracker.")
            return

        print(f"[{self.name}] Procurando tracker...")
        try:
            ns = Pyro5.api.locate_ns()
            peers = ns.list()
            
            for name, uri in peers.items():
                if name == self.name or name == "Pyro.NameServer":
                    continue 

                try:
                    peer = Pyro5.api.Proxy(uri)
                    if peer.get_is_tracker():
                        self.tracker_uri = peer
                        self.tracker_name = name
                        self.send_files(self.tracker_uri)
                        print(f"[{self.name}] Tracker encontrado: {name}")
                        return
                except Exception as e:
                    print(f"[{self.name}] Erro ao contatar {name}: {e}")
            
            print(f"[{self.name}] Nenhum tracker encontrado.")
            
            if self.epoca == 1:
                self.state = State.TRACKER
                self.register_own_files()
                print(f"[{self.name}] Eu sou o tracker agora.")
                heartbeat_thread = threading.Thread(target=self.send_heartbeat)
                heartbeat_thread.start()
            else:
                self.start_election()
        
        except Exception as e:
            print(f"[{self.name}] Erro ao localizar name server: {e}")

    ## SENDER atividade-3/fotinha.jpg
    @Pyro5.api.callback
    @Pyro5.api.expose
    def get_file(self, filename):
        print("Quiseram um arquivo daqui")
        try:
            with open(filename, "rb") as f:
                content = f.read()
            print("Enviando contéudo")
            print(type(content))
            print(content)
            return content
        except Exception as e:
            print(f"Erro ao ler o arquivo {filename}: {e}")
            return None
    
    ## RECEIVER
    def download_file(self, peer_name, filename):
        print(f"[{self.name}] Procurando {filename} no peer {peer_name}")
        try:
            peer = Pyro5.api.Proxy(f"PYRONAME:{peer_name}")
            content = peer.get_file(filename)
            data = base64.b64decode(content['data'])

            if content:
                with open(f"download_{filename}", "wb") as f:
                    f.write(data)
                print(f"Arquivo {filename} recebido e salvo.")
            else:
                print("Arquivo não encontrado ou erro na transferência.")
        except Exception as e:
            print(f"Erro ao baixar arquivo: {e}")

    def server(self):
        daemon = Pyro5.server.Daemon()       
        ns = Pyro5.api.locate_ns()
        uri = daemon.register(self)
        ns.register(self.name, uri)

        print("Ready.")
        daemon.requestLoop()


    def start_election(self):
        print(f"[{self.name}] Iniciando eleição...")
        self.state = State.CANDIDATE
        self.epoca += 1
        # self.voto = self.name  # vota em si mesmo
        self.received_votes = 1  # vota em si mesmo

        ns = Pyro5.api.locate_ns()
        peers = ns.list()

        for name, uri in peers.items():
            if name != self.name and name != "Pyro.NameServer":
                try:
                    peer = Pyro5.api.Proxy(uri)
                    voto = peer.vote(self.epoca, self.name)
                    if voto:
                        self.received_votes += 1
                except Exception as e:
                    print(f"Erro ao pedir voto de {name}: {e}")
        
        # TO DO: tirar o maior igual
        if self.received_votes >= len(peers) // 2:
            print(f"{self.name} virou TRACKER na época {self.epoca}")
            print(f"Estou virando tracker 2")
            self.state = State.TRACKER
            self.register_own_files()
            self.tracker_uri = None
            self.tracker_name = None
            heartbeat_thread = threading.Thread(target=self.send_heartbeat)
            heartbeat_thread.start()
        else:
            print(f"{self.name} perdeu a eleição")
            self.state = State.FOLLOWER

    @Pyro5.api.expose
    def vote(self, candidate_epoch, candidate_name):
        print(f"[{self.name}] Entrando na cabine de votação...")
        if candidate_epoch > self.epoca:
            # self.epoca = candidate_epoch
            self.voted = False  # permite votar na época "atual"

        if not self.voted:
            self.voted = True
            return True
        print(f"[{self.name}] Votou falso")
        return False

    def look_specific_file(self):
        self.download_file("fotinha.jpg", "PEER_A")
    
    def ask_for_files(self):
        print()
        while(True):
            print("Vamos procurar um arquivo?")
            filename = input("Nome do arquivo: ")
            location = ""
            if self.state == State.FOLLOWER:
                tracker_proxy = Pyro5.api.Proxy(f"PYRONAME:{self.tracker_name}")
                location = tracker_proxy.search_file(filename)
                self.send_files(tracker_proxy)
                # location = self.tracker_uri.search_file(filename)
                print("Localização do arquivo procurado:")
                print(location)
            elif self.state == State.TRACKER:
                location = self.search_file(filename)
            else:
                print("Aguarde as eleições...")
            
            if location == "" or location == self.name:
                continue
            
            self.download_file(location, filename)
            
            
    def run(self):
        server_thread = threading.Thread(target=self.server)
        client_thread = threading.Thread(target=self.search_tracker)
        user_input_thread = threading.Thread(target=self.ask_for_files)

        server_thread.start()
        client_thread.start()
        user_input_thread.start()

        if self.state == State.TRACKER:
            heartbeat_thread = threading.Thread(target=self.send_heartbeat)
            heartbeat_thread.start()
        elif self.state == State.FOLLOWER:
            escuta_thread = threading.Thread(target=self.listen_heartbeat)
            escuta_thread.start()

        server_thread.join()


peer = PeerMaker()
peer.run()