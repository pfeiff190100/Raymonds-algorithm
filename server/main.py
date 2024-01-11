import json
import sys
import os
from dataclasses import dataclass
from socketserver import TCPServer, BaseRequestHandler
from threading import Thread
from time import sleep

try:
    from treelib import Node, Tree
except:
    pass

@dataclass
class Node():
    id: int
    address: str
    port: int

token = "ThisIsTheSuperSecretToken"
nodes: list[Node] = []

class MyHandler(BaseRequestHandler):
    def handle(self):
        print(f"{self.client_address[0]} connected")

        data = self.request.recv(1024).strip()
        data = json.loads(data)
        node = Node(len(nodes) + 1, data["address"], int(data["port"]))

        # check if node is the first one
        if len(nodes) == 0:
            self.request.send(json.dumps({"token": token, "id": node.id}).encode())
        else:
            parent = nodes[-1]
            self.request.send(json.dumps({"parent": {"address": parent.address, "port": parent.port}, "id": node.id}).encode())
        
        nodes.append(node)
        print(f"{self.client_address[0]} added as {node.address}:{node.port}")

def print_func():
    tree = Tree()
    while len(nodes) == 0:
        sleep(1)

    tree.create_node("1", "1")
    nodes_len = 1

    while True:
        if len(nodes) > nodes_len:
            tree.create_node(str(nodes_len + 1), str(nodes_len + 1), str(nodes_len))
            nodes_len += 1
            os.system("cls")
            tree.show()

if __name__ == "__main__":
    if "treelib" in sys.modules:
        Thread(target=print_func, daemon=True).start()

    with TCPServer(("192.168.0.154", 20004), MyHandler) as server:
        server.serve_forever()
