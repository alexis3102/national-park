from pydantic import BaseModel
from typing import Literal
from backend.model.user_mod import GeneroEnum

class user_schema(BaseModel):
    nombre: str
    contrasena: str
    email: str
    genero : GeneroEnum
    edad: int

class login_schem(BaseModel):
    nombre: str
    contrasena: str