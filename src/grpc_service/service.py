import grpc
from concurrent import futures
import protobuf.service_template.service_pb2 as service_pb2
import protobuf.service_template.service_pb2_grpc as service_pb2_grpc

class ExampleService(service_pb2_grpc.ExampleServiceServicer):
    def SayHello(self, request, context):
        return service_pb2.HelloReply(message=f"Hello, {request.name}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ExampleServiceServicer_to_server(ExampleService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("WHO KNOWS")
    server.wait_for_termination()

# change this to put on docker
if __name__ == '__main__':
    serve()
