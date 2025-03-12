from typing import Callable, Awaitable, Type, TypeVar

import strawberry
from google.protobuf.message import Message
from grpc.aio import AioRpcError  # type: ignore

from protobuf.connections import (
    service_name_stub,
    service_name_models,
)
from src.models.base import BaseModel
from src.models.model import Model, ModelBase

ModelType = TypeVar("ModelType", bound=BaseModel)  # type: ignore


async def make_grpc_call(
    stub_method: Callable[[Message], Awaitable[Message]],
    response_model_cls: Type[ModelType],
    *request_message: Message,
) -> ModelType:
    """
    Make a gRPC call and return the response.

    :param stub_method: The gRPC method to call (e.g., ``GetModel``).
    :param response_model_cls: The response SQLModel class (e.g., ``Model``).
    :param request_message: The request message to send (e.g., ``service_name_models.ModelId(id=id)``).
    :return: The response SQLModel instance.
    """
    try:
        response = await stub_method(*request_message)
        return response_model_cls.from_grpc(response)
    except AioRpcError as e:
        raise Exception(e.details())


async def create_model(model: ModelBase) -> Model:
    return await make_grpc_call(
        service_name_stub.CreateModel,
        Model,
        model.to_grpc(),
    )


async def get_model(id: int) -> Model:
    return await make_grpc_call(
        service_name_stub.GetModel,
        Model,
        service_name_models.ModelId(id=id),
    )


@strawberry.type
class Query:
    get_model: Model = strawberry.field(resolver=get_model)


@strawberry.type
class Mutation:
    create_model: Model = strawberry.field(resolver=create_model)
