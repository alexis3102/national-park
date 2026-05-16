from datetime import date, time  

from fastapi import FastAPI, Depends, Form
from fastapi.middleware.cors import CORSMiddleware 
from sqlmodel import Session, select
from backend.model.user_mod import UserModel, engine, incripcionModel
from backend.model import create_all_tables, user_mod
from backend.model.eventos_mod import event_mod
from backend.password import ADMIN_NAME, ADMIN_PASS

from backend.schema.user_sch import user_schema, login_schem, incripcion, menu_categoria
from backend.schema.admit_sch import (
    creted_event_schema,
    search_event_schema,
    update_event_schema,
    detele_event_schema,
    
    search_user_schema,
    update_user_schema,
    delete_user_schema)

from backend.other.auth import verify_admit
from fastapi import File, UploadFile
from backend.model.eventos_mod import imagen_mod
import shutil, os
from fastapi.staticfiles import StaticFiles

create_all_tables()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- IMAGENES --------------------------------------------------------------------

os.makedirs("backend/img", exist_ok=True)
app.mount("/img", StaticFiles(directory="backend/img"), name="img")

def get_imagen_url(session, evento_id: int):
    img = session.exec(
        select(imagen_mod).where(imagen_mod.evento_id == evento_id)
    ).first()
    return img.url if img else None


# --- USUARIOS --------------------------------------------------------------------
@app.get("/bring_all_event_menu/", tags=['event'])
def bring_all_event_menu(_=Depends(verify_admit)):
    with Session(engine) as session:
        result = session.exec(select(event_mod)).all()
        if not result:
            return {"status": "error", "message": "no hay eventos disponibles"}
        
        data = []
        for evento in result:
            data.append({
                "id": evento.id,
                "nombre": evento.nombre,
                "descripcion": evento.descripcion,
                "fecha": evento.fecha,
                "hora": evento.hora,
                "categoria": evento.categoria,
                "cupos": evento.cupos,
                "edad_minima": evento.edad_minima,
                "imagen": get_imagen_url(session, evento.id)
            })
        return {"status": "ok", "data": data}

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

    if data.nombre == ADMIN_NAME and data.contrasena == ADMIN_PASS:
        return {
            "status":"ok",
            "role":"admit",
            "data": {"usuario": ADMIN_NAME}
        }

    with Session(engine) as session:
        search = select(UserModel).where(
            UserModel.nombre == data.nombre,
            UserModel.contrasena == data.contrasena,
        )
        result = session.exec(search).first()
        if not result:
            return {"status": "error", "message": "no existe el usuario"}
        return {"status": "ok", "role": "user", "data": {"id": result.id, "usuario": result.nombre}}


@app.post("/inscripcion/", tags=['user'])
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
            select(UserModel).where(UserModel.id == data.usuario_id)
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
        if evento.cupos <= 0:
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

@app.get("/mis_inscripciones/", tags=['user'])
def mis_inscripciones(usuario_id: int):
    with Session(engine) as session:
        inscripciones = session.exec(
            select(incripcionModel).where(incripcionModel.usuario_id == usuario_id)
        ).all()

        if not inscripciones:
            return {"status": "error", "message": "no tienes inscripciones"}

        resultado = []
        for ins in inscripciones:
            evento = session.exec(
                select(event_mod).where(event_mod.id == ins.evento_id)
            ).first()
            resultado.append({
                "inscripcion_id": ins.id,
                "fecha_inscripcion": ins.fecha,
                "evento": {
                    "id": evento.id,
                    "nombre": evento.nombre,
                    "descripcion": evento.descripcion,
                    "fecha": evento.fecha,
                    "hora": evento.hora,
                    "categoria": evento.categoria,
                    "cupos": evento.cupos,
                    "imagen": get_imagen_url(session, evento.id)
                }
            })
        return {"status": "ok", "data": resultado}
# --- ADMIT --------------------------------------------------------------------

@app.get("/bring_all_usuarios_menu/", tags=['admit'])
def bring_all_usuarios_menu (_=Depends(verify_admit)):
    with Session(engine) as session:
        result = session.exec(select(UserModel)).all()
        if not result:
            return {"status": "error", "message": "no hay eventos disponibles"}
        return {"status": "ok", "data": result}

@app.get("/search_user/", tags=['admit'])
def search_usuario(data: search_user_schema, _=Depends(verify_admit)):
    with Session(engine) as session:
        querry = select(UserModel)
        if data.id is not None:
            querry = querry.where(UserModel.id == data.id)
        if data.nombre is not None:
            querry = querry.where(UserModel.nombre == data.nombre)
        result = session.exec(querry).first()
    
        if not result:
            return {"status": "error", "message": "no existe usuario"}
        return {"status": "ok", "data":{
            "id": result.id,
            "nombre": result.nombre,
            "gmail": result.email,
            "contrasena": result.contrasena,
            "edad": result.edad,
            "genero": result.genero
        }}
    
@app.put("/update_user/", tags=['admit'])
def update_usuario(data: update_user_schema,_=Depends(verify_admit)):
    with Session(engine) as session:
        querry= select(UserModel).where(
            UserModel.id == data.id
        )
        result = session.exec(querry).first()
        if not result:
            return {"status": "error", "mensajer":"no existe este usuario"}
        if data.nuevo_nombre is not None: result.nombre = data.nuevo_nombre
        if data.nueva_contraseña is not None: result.contrasena = data.nueva_contraseña
        if data.nuevo_gmail is not None: result.email = data.nuevo_gmail
        if data.nuevo_genero is not None: result.genero = data.nuevo_genero
        if data.nuevo_edad is not None: result.edad = data.nuevo_edad

        session.add(result)
        session.commit()
        return {"status": "ok", "mesaje": "usuario actualizado"}    

@app.delete("/delete_user/", tags=['admit'])
def delete_usuario(data: delete_user_schema,_=Depends(verify_admit)):
    with Session(engine) as session:
        querry = select(UserModel).where(
            UserModel.id == data.id
        )
        result = session.exec(querry).first()
        if not result:
            return {"status": "error", "mesage": "no existe el usuario"}
        session.delete(result)
        session.commit()
        return {"status": "ok", "message": f"'{data.id}' eliminado"}    

# --- EVENTOS ------------------------------------------------------------------

@app.get("/bring_all_categoria_menu/", tags=['user'])
def bring_all_categoria_menu(data: menu_categoria):
    with Session(engine) as session:
        querry = select(event_mod).where(event_mod.categoria == data.categoria)
        result = session.exec(querry).all()

        if not result:
            return {"status": "error", "message": "no hay eventos en esa categoria"}

        data_result = []
        for evento in result:
            data_result.append({
                "id": evento.id,
                "nombre": evento.nombre,
                "descripcion": evento.descripcion,
                "fecha": evento.fecha,
                "hora": evento.hora,
                "categoria": evento.categoria,
                "cupos": evento.cupos,
                "edad_minima": evento.edad_minima,
                "imagen": get_imagen_url(session, evento.id)
            })
        return {"status": "ok", "data": data_result}


@app.post("/created_event/", tags=['event'])
async def created_event(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    fecha: date = Form(...),
    hora: time = Form(...),
    cupos: int = Form(...),
    edad_minima: int = Form(...),
    categoria: str = Form(...),
    imagen: UploadFile = File(None),  # opcional
    _=Depends(verify_admit)
):
    with Session(engine) as session:
        db_evento = event_mod(
            nombre=nombre,
            descripcion=descripcion,
            fecha=fecha,
            cupos=cupos,
            edad_minima=edad_minima,
            hora=hora,
            categoria=categoria
        )
        session.add(db_evento)
        session.commit()
        session.refresh(db_evento)

        if imagen:
            carpeta = "backend/img"
            os.makedirs(carpeta, exist_ok=True)
            nombre_archivo = f"evento_{db_evento.id}_{imagen.filename}"
            ruta = f"{carpeta}/{nombre_archivo}"

            with open(ruta, "wb") as f:
                shutil.copyfileobj(imagen.file, f)

            db_imagen = imagen_mod(
                evento_id=db_evento.id,
                url=ruta
            )
            session.add(db_imagen)
            session.commit()

        return {"status": "ok", "data": db_evento}


@app.get("/search_event/", tags=['event'])
def search_event(data: search_event_schema, _=Depends(verify_admit)):
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
            return {"status": "error", "message": "no existe el evento"}
        return {"status": "ok", "data": {
            "id": result.id,
            "nombre": result.nombre,
            "descripcion": result.descripcion,
            "fecha": result.fecha,
            "hora": result.hora,
            "categoria": result.categoria,
            "cupos": result.cupos,
            "edad_minima": result.edad_minima,
            "imagen": get_imagen_url(session, result.id)
        }}


@app.put("/update_event/", tags=['event'])
async def update_event(
    id: int = Form(...),
    nombre_new: str = Form(None),
    fecha_new: date = Form(None),
    hora_new: time = Form(None),
    categoria_new: str = Form(None),
    cupos_new: int = Form(None),
    edad_new: int = Form(None),
    imagen_new: UploadFile = File(None),
    _=Depends(verify_admit)
):
    with Session(engine) as session:
        evento = session.exec(
            select(event_mod).where(event_mod.id == id)
        ).first()
        if not evento:
            return {"status": "error", "message": "no existe el evento"}

        if nombre_new: evento.nombre = nombre_new
        if fecha_new: evento.fecha = fecha_new
        if hora_new: evento.hora = hora_new
        if categoria_new: evento.categoria = categoria_new
        if cupos_new: evento.cupos = cupos_new
        if edad_new: evento.edad_minima = edad_new

        if imagen_new:
            # borra imagen anterior
            img_anterior = session.exec(
                select(imagen_mod).where(imagen_mod.evento_id == id)
            ).first()
            if img_anterior:
                if os.path.exists(img_anterior.url):
                    os.remove(img_anterior.url)
                session.delete(img_anterior)

            # guarda la nueva
            carpeta = "backend/img"
            nombre_archivo = f"evento_{id}_{imagen_new.filename}"
            ruta = f"{carpeta}/{nombre_archivo}"
            with open(ruta, "wb") as f:
                shutil.copyfileobj(imagen_new.file, f)

            nueva_img = imagen_mod(evento_id=id, url=ruta)
            session.add(nueva_img)

        session.add(evento)
        session.commit()
        return {"status": "ok", "message": "evento actualizado"}


@app.delete("/delete_event/", tags=['event'])
def delete_event(data: detele_event_schema, _=Depends(verify_admit)):
    with Session(engine) as session:
        evento = session.exec(
            select(event_mod).where(event_mod.id == data.id)
        ).first()
        if not evento:
            return {"status": "error", "message": "no existe el evento"}

        # borra imagen si existe
        img = session.exec(
            select(imagen_mod).where(imagen_mod.evento_id == data.id)
        ).first()
        if img:
            if os.path.exists(img.url):
                os.remove(img.url)
            session.delete(img)

        session.delete(evento)
        session.commit()
        return {"status": "ok", "message": f"evento '{data.id}' eliminado"}
        