from sqlmodel import SQLModel


class BaseModel(SQLModel):
    """A superclass that acts as SQLModel, Strawberry GraphQL type and converts to gRPC Messages."""

    pass
