from concurrent import futures

import grpc  # type: ignore
import protobuf.product_service.service_pb2 as service_pb2
import protobuf.product_service.service_pb2_grpc as service_pb2_grpc
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorServer
from src.models.model import ModelBase

from src.crud.model import CrudModel

grpc_server_instrumentor = GrpcAioInstrumentorServer()
grpc_server_instrumentor.instrument()


class ProductService(service_pb2_grpc.ProductServiceServicer):
    async def CreateModel(
        self, request: service_pb2.ModelBase, context: grpc.ServicerContext
    ) -> service_pb2.Model:
        crud = CrudModel()
        model = await crud.create(ModelBase.from_grpc(request))
        if model is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Model not found")
            return service_pb2.Model()
        return model.to_grpc()

    async def GetModel(
        self, request: service_pb2.ModelId, context: grpc.ServicerContext
    ) -> service_pb2.Model:
        crud = CrudModel()
        model = await crud.get(id=request.id)
        if model is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Model not found")
            return service_pb2.Model()
        return model.to_grpc()


async def serve_grpc() -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("Listening on port 50051")
    await server.wait_for_termination()
    print("Server stopped")
