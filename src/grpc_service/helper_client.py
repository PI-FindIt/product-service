import grpc
import service_pb2
import service_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')

    stub = service_pb2_grpc.ExampleServiceStub(channel)

    name = input("Coloca um nome: ")

    request = service_pb2.HelloRequest(name=name)

    try:
        response = stub.SayHello(request)
        print("Resposta do servidor:", response.message)
    except grpc.RpcError as e:
        print(f"Erro ao comunicar com o servidor: {e.code()}: {e.details()}")
    finally:
        channel.close()


if __name__ == '__main__':
    run()