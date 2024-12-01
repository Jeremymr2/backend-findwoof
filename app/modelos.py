from sqlmodel import SQLModel, Field
from datetime import datetime
import shortuuid

# Tabla de usuarios
class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: str = Field(default_factory=shortuuid.uuid, primary_key=True)
    nombre: str
    dni: str = Field(sa_column_kwargs={"unique": True})
    email: str = Field(sa_column_kwargs={"unique": True})
    password: str
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

# Tabla de razas
class Raza(SQLModel, table=True):
    __tablename__ = "raza"

    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(sa_column_kwargs={"unique": True})

# Tabla de mascotas
class Mascota(SQLModel, table=True):
    __tablename__ = "mascotas"

    id: str = Field(default_factory=shortuuid.uuid, primary_key=True)  # UUID corto
    id_usuario: str = Field(foreign_key="usuarios.id")
    nombre: str
    edad: int
    sexo: bool
    estado_mascota: bool = True  # True para "Disponible", False para "Desaparecida"
    id_raza: int = Field(foreign_key="raza.id")
    descripcion: str
    vacunas: bool = True
    condicion_clinica: bool = False
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)


# Tabla de imágenes de mascotas (perfil y nariz)
class ImagenMascota(SQLModel, table=True):
    __tablename__ = "imagenes_mascota"

    id: int = Field(default=None, primary_key=True)
    id_mascota: str = Field(foreign_key="mascotas.id")
    url_imagen: str
    tipo_imagen: str  # perfil - nariz
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)


# Tabla de avistamientos
class Avistamiento(SQLModel, table=True):
    __tablename__ = "avistamientos"

    id: int = Field(default=None, primary_key=True)
    id_mascota: str = Field(foreign_key="mascotas.id")
    fecha_avistamiento: datetime
    ubicacion: str
    descripcion: str
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)


# Tabla de desapariciones
class Desaparicion(SQLModel, table=True):
    __tablename__ = "desapariciones"

    id: int = Field(default=None, primary_key=True)
    id_mascota: str = Field(foreign_key="mascotas.id")
    fecha_desaparicion: datetime
    descripcion: str
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
