from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from sqlmodel import Session, select
from backend.model.user_mod import UserModel, engine, incripcionModel
from backend.model import create_all_tables, user_mod
from backend.model.eventos_mod import event_mod

from backend.schema.user_sch import user_schema, login_schem, incripcion
from backend.schema.admit_sch import (
    creted_event_schema,
    search_event_schema,
    update_event_schema,
    detele_event_schema)



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


@app.post("inscripcion", tags=['user'])
def inscripcion(data: incripcion):
    with Session(engine) as session:
        
        #verifica que el evento existe
        evento = session.exec(
            select(event_mod).where(event_mod.id == data.evento_id)
        ).first()
        if not evento:
            return {"starus": "error", "mensage": "el evento no existe"}
        
        #verifica que el usuario existe
        usuario = session.exec(
            select(user_mod).where(UserModel.id == data.usuario_id)
        ).first()
        if not usuario:
            return {"status": "error", "mesage": "el usuario no existe"}
        
        #verifica que el usaurio no este ya inscrito
        ya_inscrito = session.exec(
            select (incripcionModel).where(
                incripcionModel.usuario_id == data.usuario_id,
                incripcionModel.evento_id == data.evento_id
            )
        ).first()
        if ya_inscrito:
            return {"status": "error", "message": "el usuario ya esta inscripto en el evento"}

        #verifica cupos disponibles
        if evento.cupos >= 0:
            return {"status": "error", "message":"no hay cupos disponibles"}
        
        #verifica eadd minima del evento
        if usuario.edad < evento.edad_minima:
            return {
                "status": "error",
                "message": f"el usuario debe tener minimo {evento.edad_minima} años"
            }
        
        #crea la inscripcion
        nueva_inscripcion = incripcionModel(
            usuario_id=data.usuario_id,
            evento_id=data.evento_id,
            fecha=data.fecha
        )

        #descontar un cupo
        evento.cupos -= 1

        session.add(nueva_inscripcion)
        session.add(evento)
        session.commit()
        session.refresh(nueva_inscripcion)
        return {"status": "ok", "data": nueva_inscripcion}
    
# --- ADMIT --------------------------------------------------------------------




# --- EVENTOS ------------------------------------------------------------------

@app.post("/created_event/", tags=['event'])
def created_event(data: creted_event_schema):
    with Session(engine) as session:
        db_eventos = event_mod(
            nombre=data.nombre,
            descripcion=data.descripcion,
            fecha=data.fecha,
            cupos=data.cupos,
            edad_minima=data.edad_minima,
            hora=data.hora,
            categoria=data.categoria
        )
        session.add(db_eventos)
        session.commit()
        session.refresh(db_eventos)
        return db_eventos


@app.get("/search_event/", tags=['event'])
def search_event(data: search_event_schema):
    with Session(engine) as session:
        querry = select(event_mod)
        if data.id is not None:
            querry = querry.where(event_mod.id == data.id)
        if data.fecha is not None:
            querry = querry.where(event_mod.fecha == data.fecha)
        if data.hora is not None:
            querry = querry.where(event_mod.hora == data.hora)
        if data.categoria is not None:
            querry = querry.where(event_mod.categoria == data.categoria)
        if data.cupos is not None:
            querry = querry.where(event_mod.cupos == data.cupos)
        if data.edad is not None:
            querry = querry.where(event_mod.edad_minima == data.edad)
        result = session.exec(querry).first()
    
        if not result:
            return {"status": "error", "message": "no existe usuario"}
        return {"status": "ok", "data":{
            "id": result.id,
            "nombre": result.nombre,
            "descripcion": result.descripcion,
            "fecha": result.fecha,
            "hora": result.hora,
            "categoria": result.categoria,
            "cupos": result.cupos,
            "edad:minima": result.edad_minima
        }}


@app.put("/update_event/", tags=['event'])
def update_event(data: update_event_schema):
    with Session(engine) as session:
        querry= select(event_mod).where(
            event_mod.id == data.id,
            event_mod.nombre == data.nombre
        )
        result = session.exec(querry).first()
        if not result:
            return {"status": "error", "mensajer":"no existe este evento"}
        if data.nombre_new is not None: result.nombre = data.nombre_new
        if data.fecha_new is not None: result.fecha = data.fecha_new
        if data.hora_new is not None: result.hora = data.hora_new
        if data.categoria_new is not None: result.categoria = data.categoria_new
        if data.cupos_new is not None: result.cupos = data.cupos_new
        if data.edad_new is not None: result.edad_minima = data.edad_new

        session.add(result)
        session.commit()
        return {"status": "ok", "mesaje": "evento actualizado"}


@app.delete("/delete_user/", tags=['event'])
def delete_event(data: detele_event_schema):
    with Session(engine) as session:
        querry = select(event_mod).where(
            event_mod.id == data.id
        )
        result = session.exec(querry).first()
        if not result:
            return {"status": "error", "mesage": "no existe el evento"}
        session.delete(result)
        session.commit()
        return {"status": "ok", "message": f"'{data.id}' eliminado"}
        