from datetime import date, time
from typing import Optional
from sqlmodel import SQLModel, Field

from .user_mod import engine
from sqlmodel import SQLModel
from typing import Optional

class event_mod(SQLModel, table=True):
    __tablename__="evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    fecha: date
    cupos: int
    edad_minima: int
    hora: time
    categoria: str

class imagen_mod(SQLModel, table=True):
    __tablename__ = "imagen"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int
    url: str