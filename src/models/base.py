from typing import Type, Self, Any, TypeVar, ClassVar

import strawberry
from google.protobuf.json_format import ParseDict, MessageToDict
from google.protobuf.message import Message
from sqlmodel import SQLModel


T = TypeVar("T", bound=Message)


class BaseModel[T](SQLModel):
    """A superclass that acts as SQLModel, Strawberry GraphQL type and converts to gRPC Messages."""

    __grpc_model__: Type[T]

    __strawberry_model__ = None
    # __strawberry_type__: ClassVar[type] = None

    # def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
    #     super().__init_subclass__(**kwargs)
    #
    #     @strawberry.experimental.pydantic.type(model=cls, all_fields=True)
    #     class _StrawberryType:
    #         pass
    #
    #     cls.__strawberry_model__ = _StrawberryType
    #     cls.__strawberry_type__ = strawberry.type(
    #         cls.__strawberry_model__, name=cls.__name__
    #     )
    #
    # def to_strawberry(self) -> StrawberryTypeFromPydantic[Self]:
    #     """Convert SQLModel instance to Strawberry type."""
    #     return self.__strawberry_model__.from_pydantic(self)

    def to_grpc(self) -> T:
        """Convert SQLModel instance to gRPC message."""
        return self.__grpc_model__(**self.model_dump())

    # def to_grpc(self) -> T:
    #     """Convert SQLModel instance to gRPC message, ensuring no None values."""
    #     data = {k: v if v is not None else "" for k, v in self.model_dump().items() if
    #             k in self.__grpc_model__.__annotations__}
    #     return self.__grpc_model__(**data)

    @classmethod
    def from_grpc(cls, grpc_message: Message) -> Self:  # misc
        """Convert gRPC message to SQLModel instance."""
        data_dict = MessageToDict(grpc_message, preserving_proto_field_name=True)
        return cls(**data_dict)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Convert model to dictionary (useful for JSON responses)."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an instance from a dictionary."""
        return cls(**data)
