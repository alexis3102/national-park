from .user_mod import engine
from sqlmodel import SQLModel

def create_all_tables():
    SQLModel.metadata.create_all(engine)