import socket
import queue
import threading
import json

class Node:
    def __init__(self, port):
        self.id = None
        self.server_address = ('ableytner.ddns.net', 20004)
        self.port = port
        self.parent_address = None
        self.parent_port = None
        self.requests = queue.Queue()
        self.has_token = False

        self.socket_connection()

        
    def socket_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        host = sock.getsockname()[0]

        sock.send(json.dumps({"address": host,
                   "port": self.port}).encode())

        data = self.sock.recv(1024)
        message = data.decode()
        print(f'Received message: {message}')

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

node = Node(123)
#node.request_token()
