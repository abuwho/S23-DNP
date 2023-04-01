import os
import socket
import threading
import random
from PIL import Image

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1234
BUFFER_SIZE = 1024

def handle_connection(client_socket, client_address):
    print(f"New connection from {client_address}")
    image = Image.new('RGB', (10, 10), color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    with open('temp.png', 'wb') as f:
        image.save(f, 'png')
    with open('temp.png', 'rb') as f:
        data = f.read(BUFFER_SIZE)
        while data:
            client_socket.send(data)
            data = f.read(BUFFER_SIZE)
    os.remove('temp.png')
    client_socket.close()
    print(f"Connection from {client_address} closed")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_connection, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    start_server()
