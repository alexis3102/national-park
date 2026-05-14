from datetime import date, time

from pydantic import BaseModel
from backend.model.user_mod import GeneroEnum

#-------- USER ------------------------------------------

class update_admit_schema(BaseModel):
    nombre: str
    nuevo_nombre: str
    nueva_contraseña: str
    nuevo_gmail: str
    nuevo_genero: GeneroEnum
    nuevo_edad: int

class delete_admit_schema(BaseModel):
    ID: int

# ------ EVENTOS ----------------------------------------
   
class creted_event_schema(BaseModel):
    nombre: str
    descripcion: str
    fecha: date
    hora: time
    cupos: int
    edad_minima: int
    categoria: str

class search_event_schema(BaseModel):
    id: int | None = None
    nombre: str | None = None
    fecha: date | None = None
    hora: time | None = None
    categoria: str | None = None
    cupos: int | None = None
    edad: int | None = None

class update_event_schema(BaseModel):
    id: int
    nombre: str
    nombre_new: str | None = None
    fecha_new: date | None = None
    hora_new: time | None = None
    categoria_new: str | None = None
    cupos_new: int | None = None
    edad_new: int | None = None

class detele_event_schema(BaseModel):
    id: int


