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

MAX_NODES_PER_LAYER = 3

@dataclass
class Node():
    id: int
    address: str
    port: int
    parent_id: int | None

token = "ThisIsTheSuperSecretToken"
nodes: dict[int, Node] = {}
tree_changed = True

class MyHandler(BaseRequestHandler):
    def handle(self):
        print(f"{self.client_address[0]} connected")

        data = self.request.recv(1024).strip()
        data = json.loads(data)

        # add node to the network
        if "address" in data and "port" in data:
            self.add_node_to_grid(data)
        # update parent of node
        elif "node_id" in data and "parent" in data:
            self.update_node_parent(data)

        global tree_changed
        tree_changed = True

    def add_node_to_grid(self, data):
        node_id = len(nodes) + 1

        # check if node is the first one
        if len(nodes) == 0:
            node = Node(node_id, data["address"], int(data["port"]), None)
            self.request.send(json.dumps({"token": token, "id": node.id}).encode())
        else:
            # parent = nodes[node_id-1]
            parent_id = self.get_next_parent_id()
            print(parent_id)
            parent = nodes[parent_id]
            node = Node(node_id, data["address"], int(data["port"]), parent.id)
            self.request.send(json.dumps({"parent": {"address": parent.address, "port": parent.port}, "id": node.id}).encode())
        
        nodes[node_id] = node
        print(f"{self.client_address[0]} added as {node.address}:{node.port}")

    def update_node_parent(self, data):
        node_id = data["node_id"]
        node = nodes[node_id]
        parent = (data["parent"]["address"], data["parent"]["port"])
        
        if parent[0] == None and parent[1] == None:
            node.parent_id = None
        else:
            parent_id = None
            for n in nodes.values():
                if n.address == parent[0] and n.port == parent[1]:
                    parent_id = n.id
            node.parent_id = parent_id

    def get_next_parent_id(self) -> int:
        tree = create_tree()

        leaves = []
        for node in nodes.values():
            c = 0
            for n in nodes.values():
                if n.parent_id == node.id:
                    c += 1
            if c < MAX_NODES_PER_LAYER:
                leaves.append(node)

        min_depth_node = None
        for leave in leaves:
            if min_depth_node == None:
                min_depth_node = leave
            else:
                if tree.level(leave.id) < tree.level(min_depth_node.id):
                    min_depth_node = leave
        
        return min_depth_node.id

def print_func():
    while True:
        try:
            global tree_changed
            if tree_changed:
                tree_changed = False
                tree = create_tree()
                os.system("cls")
                tree.show()

            sleep(1)
        except Exception as e:
            print("visualisation errored")
            raise e
            sleep(1)

def create_tree() -> Tree:
    tree = Tree()

    # add top of the tree
    for n in nodes.values():
        if n.parent_id == None:
            tree.create_node(n.id, n.id, n.parent_id)
    
    while len(tree.all_nodes()) < len(nodes):
        for n in nodes.values():
            tree_ids = [tn.identifier for tn in tree.all_nodes()]
            if n.id not in tree_ids and n.parent_id in tree_ids:
                tree.create_node(n.id, n.id, n.parent_id)

    return tree

if __name__ == "__main__":
    if "treelib" in sys.modules:
        Thread(target=print_func, daemon=True).start()

    with TCPServer(("192.168.0.154", 20004), MyHandler) as server:
        server.serve_forever()
