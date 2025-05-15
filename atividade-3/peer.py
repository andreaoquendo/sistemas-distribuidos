import threading

# saved as greeting-server.py
import Pyro5.api

class PeerMaker(object):
    def __init__(self):
        self.name = "peer1"
        self.is_tracker = True
        self.tracker_uri = None
        self.arquivos = {}
    
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

    def server(self):
        daemon = Pyro5.server.Daemon()         # make a Pyro daemon
        ns = Pyro5.api.locate_ns()            # find the name server
        uri = daemon.register(PeerMaker)   # register the greeting maker as a Pyro object
        ns.register(self.name, uri)   # register the object with a name in the name server

        print("Ready.")
        daemon.requestLoop()              # start the event loop of the server to wait for calls
    

    def run(self):
        server_thread = threading.Thread(target=self.server)
        client_thread = threading.Thread(target=self.procurar_tracker)

        server_thread.start()
        client_thread.start()

        server_thread.join()
        client_thread.join()

peer = PeerMaker()
peer.run()