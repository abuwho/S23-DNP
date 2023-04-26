# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import sqlite3
from concurrent.futures import ThreadPoolExecutor
import grpc

import schema_pb2 as service
import schema_pb2_grpc as stub


SERVER_ADDR = '0.0.0.0:1234'
DB_NAME = 'db.sqlite'

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Users
                 (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
    conn.commit()
    conn.close()

class Database(stub.DatabaseServicer):
    def PutUser(self, request, context):
        print(f"PutUser({request.user_id}, '{request.user_name}')")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute(f"INSERT INTO Users (id, name) VALUES ({request.user_id}, '{request.user_name}')")
            conn.commit()
            return service.status(status=True)
        except Exception as e:
            print(e)
            return service.status(status=False)
        finally:
            conn.close()

    def DeleteUser(self, request, context):
        print(f"DeleteUser({request.user_id})")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute(f"DELETE FROM Users WHERE id={request.user_id}")
            conn.commit()
            return service.status(status=True)
        except Exception as e:
            print(e)
            return service.status(status=False)
        finally:
            conn.close()

    def GetUsers(self, request, context):
        print("GetUsers()")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM Users")
            rows = c.fetchall()
            users = []
            for row in rows:
                user = service.User(user_id=row[0], user_name=row[1])
                users.append(user)
            return service.Users(users=users)
        except Exception as e:
            print(e)
            return service.Users(users=[])

if __name__ == '__main__':
    initialize_db()
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    stub.add_DatabaseServicer_to_server(Database(), server)
    server.add_insecure_port(SERVER_ADDR)
    server.start()
    print(f"gRPC server is listening on {SERVER_ADDR}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
