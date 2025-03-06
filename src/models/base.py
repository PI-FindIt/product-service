from sqlmodel import SQLModel

class Base(SQLModel):
    pass

# or for mongo

from odmantic import Model

class BaseModel(Model):
    pass