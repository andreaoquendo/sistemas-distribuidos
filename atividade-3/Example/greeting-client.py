# saved as greeting-client.py
import Pyro5.api

name = input("What is your name? ").strip()

greeting_maker = Pyro5.api.locate_ns()
uri_object = greeting_maker.lookup("example.greeting")    # use name server object lookup uri
print(greeting_maker.get_fortune(name))