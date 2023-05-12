# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
import socket

class Query:
    def __init__(self, type, key):
        self.type = type
        self.key = key

if __name__ == '__main__':
    queries = [
        Query(type="A", key="example.com"),
        Query(type="PTR", key="1.2.3.4"),
        Query(type="CNAME", key="moodle.com")
    ]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for query in queries:
            print(f"Client: Sending query for {query.key}")
            sock.sendto(json.dumps({"type": query.type, "key": query.key}).encode(), ('localhost', 50000))
            data, addr = sock.recvfrom(1024)
            response = json.loads(data.decode())
            print(f"Server: {response}")
