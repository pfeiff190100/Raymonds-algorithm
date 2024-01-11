import socket
import queue
import threading
import json

class Node:
    def __init__(self, port):
        self.id = None
        self.server_address = ('ableytner.ddns.net', 20004)
        self.client_address = None
        self.client_port = port
        self.parent_address = None
        self.parent_port = None
        self.has_token = False
        self.token = None
        self.requests = queue.Queue()

        self.inital_socket_con()

        
    def inital_socket_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        self.client_address = sock.getsockname()[0]

        sock.send(json.dumps({"address": self.client_address,
                   "port": self.client_port}).encode())

        data = sock.recv(1024)
        message = json.loads(data.decode())

        self.id = message["id"]
        if "token" in message.keys():
            self.has_token = True
            self.token = message["token"]
        else:
            self.parent_address = message["parent"]["address"]
            self.parent_address = message["parent"]["port"]
        sock.close()

    def listen_for_messages(self):
        while True:
            data = self.sock.recv(1024)
            message = data.decode()
            print(f'Received message: {message}')

            if message == 'TOKEN':
                self.receive_token()
            elif message.startswith('PARENT'):
                _, parent_ip, parent_port = message.split()
                self.parent_address = (parent_ip, int(parent_port))

    def request_token(self):
        if self.parent_address is not None:
            message = 'REQUEST'
            self.sock.sendto(message.encode(), self.parent_address)
        else:
            self.receive_token()

    def receive_token(self):
        self.has_token = True
        print(f'Node {self.id} received the token')

        if not self.requests.empty():
            next_node_address = self.requests.get()
            message = 'TOKEN'
            self.sock.sendto(message.encode(), next_node_address)
            self.has_token = False

for i in range(10):
    Node(i)

#node.request_token()
