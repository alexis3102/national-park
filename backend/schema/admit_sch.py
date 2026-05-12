from pydantic import BaseModel
from backend.model.user_mod import GeneroEnum


class update_admit_schema(BaseModel):
    nombre: str
    nuevo_nombre: str
    nueva_contraseña: str
    nuevo_gmail: str
    nuevo_genero: GeneroEnum
    nuevo_edad: int

class delete_admit_schema(BaseModel):
    ID: int