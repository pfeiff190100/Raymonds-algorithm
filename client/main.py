import socket
import socketserver
import queue
import threading
import json

class NodeHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        message = data.decode()

        if message.startswith("REQUEST-TOKEN"):
            data = message.split("|")
            self.server.node.requests.put(f"{data[1]}|{data[2]}")
            self.server.node.request_token()
        if message.startswith('RETURN-TOKEN'):
            data = message.split("|")
            self.server.node.token = data[1]
            self.server.node.receive_token()

class NodeServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class, node):
        self.node = node
        super().__init__(server_address, handler_class)

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
        sock_server = NodeServer((self.client_address, self.client_port), NodeHandler, self)
        threading.Thread(target=sock_server.serve_forever).start()
        
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
            self.parent_port = message["parent"]["port"]
        sock.close()

    def request_token(self):
        if self.parent_address is not None and not self.has_token:
            message = f'REQUEST-TOKEN|{self.client_address}|{self.client_port}'
            parent_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            parent_sock.connect((self.parent_address, self.parent_port))
            parent_sock.send(message.encode())
            parent_sock.close()
        else:
            self.receive_token()

    def receive_token(self):
        self.has_token = True
        if not self.requests.empty():
            next_node_address = self.requests.get().split("|")
            next_node_address = (next_node_address[0], int(next_node_address [1]))
            message = f'RETURN-TOKEN|{self.token}'

            token_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            token_sock.connect(next_node_address)
            token_sock.send(message.encode())
            token_sock.close()
            self.parent_address = next_node_address[0]
            self.parent_port = next_node_address[1]
            self.has_token = False
            self.token = None
        else:
            print(f"Node {self.id} got the token: {self.token}")

for i in range(10):
    if i == 3:
        node = Node(i + 2000)
        node.request_token()
    else:
        Node(i + 2000)
