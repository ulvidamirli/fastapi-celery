from sqlmodel import SQLModel, Field


class Entity(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(default=None)
    description: str = Field(default=None)
    image: str = Field(default=None)
