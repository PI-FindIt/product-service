from concurrent import futures

import grpc  # type: ignore
import protobuf.service_name.service_pb2 as service_pb2
import protobuf.service_name.service_pb2_grpc as service_pb2_grpc


class ServiceName(service_pb2_grpc.ServiceNameServicer):
    async def CreateModel(
        self, request: service_pb2.ModelBase, context: grpc.ServicerContext
    ) -> service_pb2.Model:
        return service_pb2.Model(id=0, message=f"Hello, I'm CreateModel!")

    async def GetModel(
        self, request: service_pb2.ModelId, context: grpc.ServicerContext
    ) -> service_pb2.Model:
        # *Example*
        # crud = CrudBook()
        # book = await crud.get(id=request.id)
        # if book is None:
        #     context.set_code(grpc.StatusCode.NOT_FOUND)
        #     context.set_details("Book not found")
        #     return service_pb2.Book()
        # return book.to_grpc()
        return service_pb2.Model(id=0, message=f"Hello, I'm GetModel!")


async def serve_grpc() -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ServiceNameServicer_to_server(ServiceName(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("Listening on port 50051")
    await server.wait_for_termination()
    print("Server stopped")
