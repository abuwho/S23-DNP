# Distributed and Network Programming - Spring 2023

### Socket module in Python

- To create a socket you must use the socket function which returns a socket object. <br>
  For example, 
  ```Python
  import socket
  s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  ```
  In the given example, AF_INET is used for IPv4 and AF_INET6 is used for IPv6. Also, `type = socket.SOCK_STREAM` is used for TCP connection and `type =  socket.SOCK_DGRAM` is used for UDP connection.

### Available socket methods: 
- `bind((host_addr, port_no))` **TUPLE**
- `send(bytes, address)`
- `recvfrom(bufsize)`


### General socket methods:
- `close()`
- `gethostname()`
- `gethostbyname()`

### UDP Socket Programming
- UDP socket flow: 
  - server: `socket()` -> `bind()` -> `sendto()`/`recvfrom()` -> `close()`
  - client: `socket()` -> `sendto()`/`recvfrom()` -> `close()`


### Blocking and non-blocking modes
- By default, sockets work in blocking mode.
- How to set a non-blocking mode? -> `setblocking(bool)`

### Setting timeout for blocking mode
- `settimeout()` method

### ARQ - Automatic Repeat reQuest
- Stop-and-wait ARQ
- Go-Back-N ARQ
  

### TCP Socket Programming
- Server socket methods
  - `listen(backlog)`
  - `accept()`
- Client socket methods
  - `connect((server_addr, server_port_no))`
- Other socket methods
  - `recv(bufsize)`
  - `send(bytes)`
- Server: `socket()` -> `bind()` -> `listen()` -> `accept()` -> `send()` / `recv()` -> `close()`
- Client: `socket()` -> `connect()` -> `send()` / `recv()` -> `close()`

### Simple TCP Server: 
- Must listen for incoming connections
- Typically runs forever in a loop

### Simple TCP Client: 
- Establish a connection
- Send the message
- Close the connection

### Questions:
- What happens if no connection request is received? 


### Concurrency in Python
- Multiple processes

### Process
- What are the three basic components of a process? 
- What are the 2 categories of processes?

### Threads
- Multiple threads can exist within one process where:
  - Each thread contains its own register set and local variables (stored in stack).
  - All threads of a process share global variables (stored in heap) and the program code.


### The `Thread` class: 
- Methods: `start()`, `is_alive()`, `join()`, `run()`
- 2 Thread identities: human-oriented **name** and machine-oriented **ident**

### Ways to create threads:
1. Using a target function while creating thread.
2. Create a subclass of the `Thread` class, and define the behavior of the thread in the `run()` method. Advantage: No need to pass **target** function. 

### Data-sharing in threads
- Threads can share data within the program (process) they live in.
  
### Race condition in threads
- When reading the same data, everything goes fine. However, when threads try to modify the data, it may lead to unpredictable behavior. 
- Define: critical section

### Synchronization in threads: 
- The `Lock` class
- `acquire()` and `release()` method

### Producer-consumer model
- Some threads produce tasks to do (producer) to a shared data structure, the `Queue`
- Some threads consume the tasks from the queue and do the task

### GIL - Global Interpreter Locker
- A safety mechanism that lets only 1 thread hold the control on the Python interpreter.
- It affects only when you are running CPU-bound tasks.

