# Author: Abu Huraira
# Email: a.huraira@innopolis.university

import grpc
import calculator_pb2
import calculator_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50000') as channel:
        calc_stub = calculator_pb2_grpc.CalculatorStub(channel)
        
        response = calc_stub.Add(calculator_pb2.Numbers(a=10, b=2))
        print(f"Client log: Add(10,2) = {response.result}")
        calc_stub.PrintResult(calculator_pb2.Result(result=response.result))
        
        response = calc_stub.Subtract(calculator_pb2.Numbers(a=10, b=2))
        print(f"Client log: Subtract(10,2) = {response.result}")
        calc_stub.PrintResult(calculator_pb2.Result(result=response.result))
        
        response = calc_stub.Multiply(calculator_pb2.Numbers(a=10, b=2))
        print(f"Client log: Multiply(10,2) = {response.result}")
        calc_stub.PrintResult(calculator_pb2.Result(result=response.result))
        
        response = calc_stub.Divide(calculator_pb2.Numbers(a=10, b=2))
        print(f"Client log: Divide(10,2) = {response.result}")
        calc_stub.PrintResult(calculator_pb2.Result(result=response.result))
        
        response = calc_stub.Divide(calculator_pb2.Numbers(a=10, b=0))
        print(f"Client log: Divide(10,0) = {response.result}")
        calc_stub.PrintResult(calculator_pb2.Result(result=response.result))

if __name__ == '__main__':
    run()
