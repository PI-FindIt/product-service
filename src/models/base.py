from typing import Type, ClassVar, Self, Any

import strawberry
from google.protobuf.json_format import ParseDict, MessageToDict
from google.protobuf.message import Message
from sqlmodel import SQLModel
from strawberry.experimental.pydantic.conversion_types import StrawberryTypeFromPydantic


class BaseModel(SQLModel):
    """A superclass that acts as SQLModel, Strawberry GraphQL type and converts to gRPC Messages."""

    __grpc_model__ = Message
    __strawberry_type__ = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__()
        cls.__strawberry_type__ = cls.as_strawberry_type()

    @classmethod
    def as_strawberry_type(cls) -> Type[StrawberryTypeFromPydantic[Self]]:
        @strawberry.experimental.pydantic.type(model=cls, all_fields=True)
        class _StrawberryModel:
            pass

        return _StrawberryModel

    def to_grpc(self) -> __grpc_model__:
        """Convert SQLModel instance to gRPC message."""
        return ParseDict(self.model_dump(), self.__grpc_model__())

    @classmethod
    def from_grpc(cls, grpc_message: __grpc_model__) -> "HybridModel":
        """Convert gRPC message to SQLModel instance."""
        data_dict = MessageToDict(grpc_message, preserving_proto_field_name=True)
        return cls(**data_dict)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Convert model to dictionary (useful for JSON responses)."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HybridModel":
        """Create an instance from a dictionary."""
        return cls(**data)
