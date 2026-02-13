#!/usr/bin/python3

import socket
import threading

class Server:
    def __init__(self):
            self.ip = socket.gethostbyname(socket.gethostname())
            while True:
                try:
                    #self.port = int(input('Enter port number to run on --> '))
                    self.port = 4322
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.s.bind((self.ip, self.port))

                    break
                except OSError:
                    print("Couldn't bind to that port")

            self.connections = []
            self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        print('Running on IP: '+self.ip)
        print('Running on port: '+str(self.port))
        
        while True:
            c, addr = self.s.accept()

            self.connections.append(c)

            threading.Thread(target=self.handle_client,args=(c,addr,), daemon=True).start()
        
    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except OSError:
                    if client in self.connections:
                        self.connections.remove(client)

    def handle_client(self,c,addr):
        while True:
            try:
                data = c.recv(1024)
                if not data:
                    break
                self.broadcast(c, data)

            except socket.error:
                break

        if c in self.connections:
            self.connections.remove(c)
        c.close()

server = Server()
