import os

from fastapi import FastAPI, UploadFile, Depends, File
from sqlmodel import SQLModel, select, Session

from login import create_token, profile, encode_token, decode_token
from service import create_imagen_mascota, get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from PIL import Image
from io import BytesIO
from http.client import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response #handling API responses
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# Import
from database import create_db_and_tables, get_session
from service import (create_user, get_user, update_user, delete_user, create_pet, get_pet, update_pet,
                     delete_pet, get_pets_by_user, get_image_profile_by_pet)
from nose_scan import detect_nose_to_json, detect_nose_to_image
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()



#CORS (Cross-Origin Resource Sharing) middleware, allows the API to be accessed from different domains or origins.

origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/healthcheck/")
def healthcheck(session: Session = Depends(get_session)):
    try:
        statement = select(1)
        result = session.exec(statement).first()
        if result:
            return {
                "Status": "Ok",
                "version": "1.0",
                "database": "Conexión exitosa"
            }
        else:
            return {
                "Status": "Fail",
                "version": "1.0",
                "database": "No se pudo conectar a la base de datos"
            }
    except Exception as e:
        return {
            "Status": "Error",
            "version": "1.0",
            "database": f"Error de conexión: {str(e)}"
        }

# @app.post("/predict/")
# async def predict(file: UploadFile):
#     return {"filename": file.filename}

# LOGIN
@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    token = create_token(db, form_data)
    if not token:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecta")
    return {"access_token": token}

@app.get("/usuario/profile")
def usuario_profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user

@app.post("/usuario/mascota")
def usuario_mascota(nombre: str, edad: int, sexo: bool,
                    estado_mascota: bool, id_raza: int, descripcion: str, vacunas: bool, condicion_clinica: bool,
                    my_user: Annotated[dict, Depends(decode_token)], db: Session = Depends(get_session)):
    # id usuario autenticado
    id_autenticado = my_user.id
    if not id_autenticado:
        raise HTTPException(status_code=403, detail="No autorizado para realizar esta acción")
    # Crear la mascota
    db_mascota = create_pet(db, id_autenticado, nombre, edad, sexo, estado_mascota, id_raza, descripcion, vacunas, condicion_clinica)
    return db_mascota

# USUARIOS
@app.post("/usuarios")
def crear_usuario(nombre: str, dni: str, email: str, password: str, db:Session = Depends(get_session)):
    db_usuario = create_user(db, nombre, dni, email, password)
    return db_usuario

@app.get("/usuarios/{id}")
def obtener_usuario(id: str, db:Session = Depends(get_session)):
    db_usuario = get_user(db, id)
    return db_usuario

@app.put("/usuarios/{id}")
def actualizar_usuario(id_usuario: str, nombre: str, dni: str, email: str, password: str, db: Session = Depends(get_session)):
    db_usuario = update_user(db, id_usuario, nombre, dni, email, password)
    return db_usuario

@app.delete("/usuarios/{id}")
def eliminar_usuario(id_usuario: str, db:Session = Depends(get_session)):
    db_usuario = delete_user(db, id_usuario)
    return db_usuario

# MASCOTAS
@app.post("/mascotas")
def crear_mascota(id_usuario: str, nombre: str, edad: int, sexo: bool
               , estado_mascota: bool, id_raza: int, descripcion: str, vacunas: bool, condicion_clinica: bool, db: Session = Depends(get_session)):
    db_mascota = create_pet(db, id_usuario, nombre, edad, sexo, estado_mascota, id_raza, descripcion, vacunas, condicion_clinica)
    return db_mascota

@app.get("/mascotas")
def obtener_mascotas(id_mascota: str, db:Session = Depends(get_session)):
    db_mascota = get_pet(db, id_mascota)
    return db_mascota

@app.put("/mascotas/{id}")
def actualizar_mascota(id_mascota:str, id_usuario: str, nombre: str, edad: int, sexo: bool
               , estado_mascota: bool, raza_id: int, descripcion: str, vacunas: bool, condicion_clinica: bool, db: Session = Depends(get_session)):
    db_mascota = update_pet(db, id_mascota, id_usuario, nombre, edad, sexo, estado_mascota, raza_id, descripcion, vacunas, condicion_clinica)
    return db_mascota

@app.delete("/mascotas/{id}")
def eliminar_mascota(id_mascota: str, db:Session = Depends(get_session)):
    db_mascota = delete_pet(db, id_mascota)
    return db_mascota

# IMAGENES_MASCOTAS
@app.post("/mascotas/imagen")
async def subir_imagen_mascota(id_mascota: str, file: UploadFile, tipo_imagen: str, db: Session = Depends(get_session)):
    db_imagen_mascota = create_imagen_mascota(db, id_mascota, file, tipo_imagen)
    return db_imagen_mascota

# EXTRAS
@app.get("/mascota/usuario/{id}")
def mascota_por_usuario(id_usuario: str, db: Session = Depends(get_session)):
    db_mascotas = get_pets_by_user(db, id_usuario)
    return db_mascotas

# Modelo
@app.post("/detect/json")
async def detect_nose_json(file: UploadFile):
    binary_image = await file.read()
    response_json = detect_nose_to_json(binary_image)
    return {"result":response_json}

@app.post("/detect/image")
async def detect_nose_image(file: UploadFile):
    binary_image = await file.read()
    response_image = detect_nose_to_image(binary_image)
    return Response(content=response_image.getvalue(), media_type="image/jpeg")

# @app.get("/findpet/{pet_id}")
# def find_pet(pet_id: int):
#     return {"pet_id": pet_id}
