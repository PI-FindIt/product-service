from concurrent import futures

import grpc  # type: ignore

import protobuf.service_template.service_pb2 as service_pb2
import protobuf.service_template.service_pb2_grpc as service_pb2_grpc
from src.models.book import CrudBook


class MicroserviceTemplate(service_pb2_grpc.MicroserviceTemplateServicer):
    async def GetBook(
        self, request: service_pb2.BookId, context: grpc.ServicerContext
    ) -> service_pb2.Book:
        crud = CrudBook()
        book = await crud.get(id=request.id)
        if book is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Book not found")
            return service_pb2.Book()
        return book.to_grpc()


async def serve_grpc() -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MicroserviceTemplateServicer_to_server(
        MicroserviceTemplate(), server
    )

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("Listening on port 50051")
    await server.wait_for_termination()
    print("Server stopped")
    return None
