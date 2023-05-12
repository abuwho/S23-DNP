# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import grpc
import math
import concurrent.futures

import calculator_pb2
import calculator_pb2_grpc


class Calculator(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        return calculator_pb2.Result(result=request.a + request.b)

    def Subtract(self, request, context):
        return calculator_pb2.Result(result=request.a - request.b)

    def Multiply(self, request, context):
        return calculator_pb2.Result(result=request.a * request.b)

    def Divide(self, request, context):
        if request.b == 0:
            return calculator_pb2.Result(result=math.nan)
        else:
            return calculator_pb2.Result(result=request.a / request.b)
    
    def PrintResult(self, request, context):
        print(f"Server log: Received result == {request.result}")
        return calculator_pb2.Empty()

def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
    server.add_insecure_port('[::]:50000')
    server.start()
    print("gRPC server is listening on 0.0.0.0:50000")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("^CShutting down...")
        server.stop(0)

if __name__ == '__main__':
    serve()
