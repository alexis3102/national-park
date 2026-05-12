from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from sqlmodel import Session, select
from backend.model.user_mod import UserModel, engine
from backend.model import create_all_tables, user_mod
from backend.schema.user_sch import user_schema, login_schem



create_all_tables()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- USUARIOS --------------------------------------------------------------------

@app.post("/create_user/", tags=['user'])
def cread_user(user: user_schema):
    with Session(user_mod.engine) as session:
        db_user = user_mod.UserModel(
            nombre=user.nombre,
            contrasena=user.contrasena,
            email=user.email,
            genero=user.genero,
            edad=user.edad
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    
@app.post("/login/", tags=['user'])
def login(data: login_schem):
    with Session(engine) as session:
        search = select(UserModel).where(
            UserModel.nombre == data.nombre,
            UserModel.contrasena == data.contrasena,
        )
        result = session.exec(search).first()
        if not result:
            return {"status": "error", "message": "no existe el usuario"}
        return {"status": "ok", "data": {"usuario": result.nombre, "contrasena": result.contrasena}}

