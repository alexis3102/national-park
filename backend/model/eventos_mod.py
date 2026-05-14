from datetime import date, time

from sqlmodel import Field 

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
