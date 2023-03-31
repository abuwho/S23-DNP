# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import argparse
import os
import socket

MSS = 20476  # MSS = Server buffer size (20480) - data header size (4)

def receive_file(s, file_name, file_size):
    with open(file_name, "wb") as f:
        bytes_received = 0
        seqno = 1
        while bytes_received < file_size:
            try:
                data, addr = s.recvfrom(MSS + 4)
                message_type = data[0:1].decode()
                message_seqno = int(data[2:3].decode())
                if message_type != "d" or message_seqno != seqno:
                    raise ValueError("Invalid message")
                f.write(data[4:])
                bytes_received += len(data[4:])
                print(f"Server: Received chunk {seqno}")
                ack = f"a|{(seqno + 1) % 2}".encode()
                s.sendto(ack, addr)
                seqno = (seqno + 1) % 2
            except ValueError:
                print("Server: Invalid message received")
                break

        if bytes_received == file_size:
            print(f"Server: File {file_name} received successfully")
        else:
            print(f"Server: File {file_name} transfer incomplete")

def main(port):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
        s.bind(("0.0.0.0", port))
        print(f"Server: Listening on port {port}")

        while True:
            try:
                data, addr = s.recvfrom(MSS)
                message_type = data[0:1].decode()
                if message_type == "s":
                    # Start of file transfer
                    file_info = data.decode().split("|")
                    file_name = file_info[2]
                    file_size = int(file_info[3])
                    print(f"Server: Receiving file {file_name} ({file_size} bytes)")
                    ack = b"a|1"
                    s.sendto(ack, addr)
                    receive_file(s, file_name, file_size)
                else:
                    raise ValueError("Invalid message")
            except ValueError:
                print("Server: Invalid message received")
            except KeyboardInterrupt:
                print("Server: Exiting...")
                exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    main(args.port)
