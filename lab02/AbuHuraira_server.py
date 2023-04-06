# Author: Abu Huraira
# Email: a.huraira@innopolis.university

# Note: Since the creation of the GIF is CPU intensive, we will use multiple processes to create the GIF.
# On the other hand, the downloading of the frames is I/O intensive, so we will use multiple threads to download the frames.

import socket
import threading
from PIL import Image
import io
import random

SERVER_IP = '0.0.0.0'
SERVER_PORT = 1234
BUFFER_SIZE = 1024


def handle_client(client_socket, client_addr):
    print(f"Sending image to {client_addr}")
    # Create a random 10x10 image
    img = Image.new('RGB', (10, 10), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    # Convert the image to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    # Send the image to the client
    client_socket.sendall(img_bytes)
    # Close the client socket
    client_socket.close()


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    print(f"Listening on {SERVER_IP}:{SERVER_PORT}")
    try:
        while True:
            # Accept a client connection
            client_socket, client_addr = server_socket.accept()
            # Spawn a new thread to handle the connection
            t = threading.Thread(target=handle_client, args=(client_socket, client_addr))
            t.start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        server_socket.close()


if __name__ == '__main__':
    server()
