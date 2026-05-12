from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from enum import Enum

DATABASE_URL = "postgresql://postgres:D%2Farwin999@localhost:5432/park"

engine = create_engine(DATABASE_URL, echo=True)

class GeneroEnum(str,Enum):
    M = "M"
    W = "W"

class UserModel(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    contrasena: str
    edad: int
    genero: GeneroEnum