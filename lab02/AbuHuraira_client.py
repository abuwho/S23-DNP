# Author: Abu Huraira
# Email: a.huraira@innopolis.university

# Note: Since the creation of the GIF is CPU intensive, we will use multiple processes to create the GIF.
# On the other hand, the downloading of the frames is I/O intensive, so we will use multiple threads to download the frames.

import os
import socket
import time
from multiprocessing import Pool
from threading import Thread
from PIL import Image

SERVER_URL = '127.0.0.1:1234'
FILE_NAME = 'AbuHuraira.gif'
CLIENT_BUFFER = 1024
FRAME_COUNT = 5000
NUM_PROCESSES = os.cpu_count()  # number of processes to use for GIF creation
NUM_THREADS = 10  # number of threads to use for downloading frames


def download_frames(start, end):
    ip, port = SERVER_URL.split(':')
    for i in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            image = b''
            while True:
                packet = s.recv(CLIENT_BUFFER)
                if not packet:
                    break
                image += packet
            with open(f'frames/{i}.png', 'wb') as f:
                f.write(image)


def create_gif(process_id):
    t0 = time.time()
    frames = []
    for frame_id in range(process_id, FRAME_COUNT, NUM_PROCESSES):
        frames.append(Image.open(f"frames/{frame_id}.png").convert("RGBA"))
    frames[0].save(f"{process_id}.gif", format="GIF",
                   append_images=frames[1:], save_all=True, duration=500, loop=0)
    return time.time() - t0


if __name__ == '__main__':
    print("Downloading frames...")
    t0 = time.time()
    if not os.path.exists('frames'):
        os.mkdir('frames')
    pool = Pool(processes=NUM_THREADS)
    batch_size = FRAME_COUNT // NUM_THREADS
    for i in range(NUM_THREADS):
        start = i * batch_size
        end = (i + 1) * batch_size
        pool.apply_async(download_frames, args=(start, end))
    pool.close()
    pool.join()
    print(f"Frames download time: {time.time() - t0:.2f}s")

    print("Creating GIF...")
    t0 = time.time()
    pool = Pool(processes=NUM_PROCESSES)
    for i in range(NUM_PROCESSES):
        pool.apply_async(create_gif, args=(i,))
    pool.close()
    pool.join()
    gif_files = [f"{i}.gif" for i in range(NUM_PROCESSES)]
    with open(FILE_NAME, 'wb') as f:
        for gif_file in gif_files:
            with open(gif_file, 'rb') as g:
                f.write(g.read())
            os.remove(gif_file)
    print(f"GIF creation time: {time.time() - t0:.2f}s")
