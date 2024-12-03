from typing import List

import numpy as np
from fastapi import UploadFile
import boto3
from app.modelos import Usuario, Mascota, ImagenMascota
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import requests
import cv2
from app.predict import preprocess_numpy, reshape_numpy

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Conexion al s3
s3 = boto3.client('s3',
                  region_name= REGION_NAME,
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)

# CRUD USER
def create_user(db: Session, nombre: str, apellido: str, telefono: str, dni: str, email: str, password: str) -> Usuario:
    db_usuario = Usuario(nombre=nombre, apellido=apellido, telefono=telefono, dni=dni, email=email, password=password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_user(db: Session, id_usuario: str) -> Usuario:
    return db.query(Usuario).filter(Usuario.id == id_usuario).first()

def get_user_by_email(db: Session, email_usuario: str) -> Usuario:
    return db.query(Usuario).filter(Usuario.email == email_usuario).first()

def update_user(db: Session, id_usuario: str, nombre: str, apellido: str,
                telefono: str, dni: str, email: str, password: str) -> Usuario:
    db_usuario = get_user(db, id_usuario)
    db_usuario.nombre = nombre
    db_usuario.dni = dni
    db_usuario.email = email
    db_usuario.password = password
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_user(db: Session, id_usuario: str) -> None:
    db.query(Usuario).filter(Usuario.id == id_usuario).first().delete()
    db.commit()

# CRUD PET

def create_pet(db: Session, id_usuario: str, nombre: str, edad: int, sexo: bool
               , estado_mascota: bool, id_raza: int, descripcion: str, vacunas: bool, condicion_clinica: bool) -> Mascota:
    db_mascota = Mascota(id_usuario=id_usuario, nombre=nombre, edad=edad, sexo=sexo, estado_mascota= estado_mascota,
                         id_raza=id_raza, descripcion=descripcion, vacunas=vacunas, condicion_clinica=condicion_clinica)
    db.add(db_mascota)
    db.commit()
    db.refresh(db_mascota)
    return db_mascota

def get_pet(db: Session, id_mascota: str) -> Mascota:
    return db.query(Mascota).filter(Mascota.id == id_mascota).first()

def update_pet(db: Session, id_mascota: str, id_usuario: str, nombre: str, edad: int, sexo: bool
               , estado_mascota: bool, raza_id: int, descripcion: str, vacunas: bool, condicion_clinica: bool) -> Mascota:
    db_mascota = get_pet(db, id_mascota)
    db_mascota.id_usuario = id_usuario
    db_mascota.nombre = nombre
    db_mascota.edad = edad
    db_mascota.sexo = sexo
    db_mascota.estado_mascota = estado_mascota
    db_mascota.raza_id = raza_id
    db_mascota.descripcion = descripcion
    db_mascota.vacunas = vacunas
    db_mascota.condicion_clinica = condicion_clinica
    db.commit()
    db.refresh(db_mascota)
    return db_mascota

def delete_pet(db: Session, id_mascota: str) -> None:
    db.query(Mascota).filter(Mascota.id == id_mascota).first().delete()
    db.commit()

# CRUD ImagenMascota
def create_imagen_mascota(db: Session, id_mascota: str, file: UploadFile, tipo_imagen: str) -> ImagenMascota:
    # Generar nombre
    file_key = f"{id_mascota}/{tipo_imagen}/{file.filename}"
    # Subir imagen a s3
    s3.upload_fileobj(
        file.file,
        BUCKET_NAME,
        file_key,
        ExtraArgs={"ContentType": file.content_type, 'ACL': 'public-read'}
    )
    url_imagen = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{file_key}"
    db_imagen_mascota = ImagenMascota(id_mascota=id_mascota, url_imagen=url_imagen, tipo_imagen=tipo_imagen)
    db.add(db_imagen_mascota)
    db.commit()
    db.refresh(db_imagen_mascota)
    return db_imagen_mascota

def get_imagen_mascota(db: Session, id_imagen_mascota: int) -> ImagenMascota:
    return db.query(ImagenMascota).filter(ImagenMascota.id == id_imagen_mascota).first()

def update_imagen_mascota(db: Session, id_imagen_mascota: int, url_imagen: str, tipo_imagen: str) -> ImagenMascota:
    db_imagen_mascota = get_imagen_mascota(db, id_imagen_mascota)
    db_imagen_mascota.url_imagen = url_imagen
    db_imagen_mascota.tipo_imagen = tipo_imagen
    db.commit()
    db.refresh(db_imagen_mascota)
    return db_imagen_mascota

def delete_imagen_mascota(db: Session, id_imagen_mascota: int) -> None:
    db.query(ImagenMascota).filter(ImagenMascota.id == id_imagen_mascota).first().delete()
    db.commit()

# Servicios extras

def compare_to_all(db: Session,model, img):
    umbral = 0
    best = 0
    np_array = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    img_numpy = preprocess_numpy(img)
    img_numpy = reshape_numpy(img_numpy)

    # traer todas las imagenes_mascota de narices de la bd
    imagenes_bd = all_mascota_nariz(db)

    # llamar urls
    for imagen_mascota in imagenes_bd:
        try:
            url = imagen_mascota.url_imagen
            response = requests.get(url)
            response.raise_for_status()  # Lanza una excepción si la descarga falla
            np_url = np.frombuffer(response.content, dtype=np.uint8)
            img_url = cv2.imdecode(np_url, cv2.IMREAD_COLOR)
            img_url = preprocess_numpy(img_url)
            img_url = reshape_numpy(img_url)
            result = model.predict([img_numpy, img_url])
            if result > umbral:
                umbral = result
                best = imagen_mascota
        except requests.exceptions.RequestException as e:
            print(f"Error descargando la imagen: {url} - {e}")
        except cv2.error as e:
            print(f"Error procesando la imagen: {url} - {e}")
    if umbral > 0.8:
        return best
    return None


def all_mascota_nariz(db: Session) -> List[ImagenMascota]:
    imagenes_nariz = db.query(ImagenMascota).filter(ImagenMascota.tipo_imagen == "nariz").all()
    return imagenes_nariz

def get_pets_by_user(db: Session, id_usuario: str) -> List[Mascota]:
    return db.query(Mascota).filter(Mascota.id_usuario == id_usuario).all()

def get_image_profile_by_pet(db: Session, id_mascota: str) -> List[ImagenMascota]:
    return db.query(ImagenMascota).filter(ImagenMascota.id_mascota == id_mascota and ImagenMascota.tipo_imagen=="perfil").all()