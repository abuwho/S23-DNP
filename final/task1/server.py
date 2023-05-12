# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import json
import socket

class RR:
    def __init__(self, type, key, value):
        self.type = type
        self.key = key
        self.value = value

class DNS_Server:
    def __init__(self):
        self.records = [
            RR(type="A", key="example.com", value="1.2.3.4"),
            RR(type="PTR", key="1.2.3.4", value="example.com")
        ]
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('0.0.0.0', 50000))
            print("Server: listening on 0.0.0.0:50000")
            while True:
                data, addr = sock.recvfrom(1024)
                query = json.loads(data.decode())
                print(f"Client: {query}")
                response = self.lookup(query)
                print(f"Server: {response}")
                sock.sendto(json.dumps(response).encode(), addr)

    def lookup(self, query):
        for record in self.records:
            if record.type == query["type"] and record.key == query["key"]:
                return {"type": record.type, "key": record.key, "value": record.value}
        return {"type": query["type"], "key": query["key"], "value": "NXDOMAIN"}

if __name__ == '__main__':
    server = DNS_Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer: Shutting down...")
