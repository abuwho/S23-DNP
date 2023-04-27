from argparse import ArgumentParser
from bisect import bisect_left
from threading import Thread
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

M = 5
PORT = 1234
RING = [2, 7, 11, 17, 22, 27]


class Node:
    def __init__(self, node_id):
        """Initializes the node properties and constructs the finger table according to the Chord formula"""
        self.id = node_id
        self.finger_table = []
        for i in range(M):
            start = (self.id + 2**i) % 2**M
            self.finger_table.append((start, self.find_successor(start)))
        print(f"Node {self.id} created! Finger table = {self.finger_table}")

    def closest_preceding_node(self, id):
        """Returns node_id of the closest preceeding node (from n.finger_table) for a given id"""
        for i in range(M - 1, -1, -1):
            if self.finger_table[i][1] != self.id and self.finger_table[i][1] < id:
                return self.finger_table[i][1]
        return self.id

    def find_successor(self, id):
        """Recursive function returning the identifier of the node responsible for a given id"""
        if id == self.id:
            return self.id
        succ = self.closest_preceding_node(id)
        if succ == self.id:
            proxy = None
        else:
            proxy = ServerProxy(f'http://localhost:{succ}')
        return proxy.find_successor(id) if proxy else self.id

    def put(self, key, value):
        """Stores the given key-value pair in the node responsible for it"""
        if self.find_successor(key) == self.id:
            self.store_item(key, value)
            print(f"put({key}, {value})")
            return True
        else:
            proxy = ServerProxy(f'http://localhost:{self.find_successor(key)}')
            return proxy.put(key, value)

    def get(self, key):
        """Gets the value for a given key from the node responsible for it"""
        if self.find_successor(key) == self.id:
            value = self.retrieve_item(key)
            print(f"get({key}) = {value}")
            return value
        else:
            proxy = ServerProxy(f'http://localhost:{self.find_successor(key)}')
            return proxy.get(key)

    def store_item(self, key, value):
        """Stores a key-value pair into the data store of this node"""
        return True

    def retrieve_item(self, key):
        """Retrieves a value for a given key from the data store of this node"""
        return -1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('id', type=int)
    args = parser.parse_args()
    node = Node(args.id)
    server = SimpleXMLRPCServer(('localhost', PORT + args.id))
    server.register_instance(node)
    print(f"Starting server for node {args.id} on port {PORT + args.id}")
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
