import os
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from models import ClienteDB


# ======= Crear tablas =======
Base.metadata.create_all(bind=engine)


# ======= Seguridad API KEY =======
API_KEY = os.getenv("API_KEY", "UNICA-2026")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def require_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "API Clientes activa"}

# ======= Sesión DB =======
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======= Modelos Pydantic =======
class EstadoCliente(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class ClienteIn(BaseModel):
    nombre: str = Field(min_length=1)
    email: EmailStr
    estado: EstadoCliente
    fechaRegistro: date


class ClienteOut(ClienteIn):
    id: int


# ======= Excepción personalizada =======
class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


# ======= App =======
app = FastAPI(title="SISTEMA DE GESTION DE CLIENTES")


@app.exception_handler(NotFoundError)
def not_found_handler(_, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": "NOT_FOUND", "message": exc.message})


# ======= Funciones CRUD (Servicio simple) =======
def to_out(c: ClienteDB) -> ClienteOut:
    return ClienteOut(
        id=c.id,
        nombre=c.nombre,
        email=c.email,
        estado=c.estado,
        fechaRegistro=c.fechaRegistro
    )


@app.get("/api/clientes", response_model=List[ClienteOut], dependencies=[Depends(require_api_key)])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(ClienteDB).all()
    return [to_out(c) for c in clientes]


@app.get("/api/clientes/{cliente_id}", response_model=ClienteOut, dependencies=[Depends(require_api_key)])
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not c:
        raise NotFoundError(f"Cliente no encontrado: {cliente_id}")
    return to_out(c)


@app.post("/api/clientes", response_model=ClienteOut, status_code=201, dependencies=[Depends(require_api_key)])
def crear_cliente(cliente_in: ClienteIn, db: Session = Depends(get_db)):
    c = ClienteDB(
        nombre=cliente_in.nombre,
        email=str(cliente_in.email),
        estado=cliente_in.estado.value,
        fechaRegistro=cliente_in.fechaRegistro
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return to_out(c)


@app.put("/api/clientes/{cliente_id}", response_model=ClienteOut, dependencies=[Depends(require_api_key)])
def actualizar_cliente(cliente_id: int, cliente_in: ClienteIn, db: Session = Depends(get_db)):
    c = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not c:
        raise NotFoundError(f"Cliente no encontrado: {cliente_id}")

    c.nombre = cliente_in.nombre
    c.email = str(cliente_in.email)
    c.estado = cliente_in.estado.value
    c.fechaRegistro = cliente_in.fechaRegistro

    db.commit()
    db.refresh(c)
    return to_out(c)


@app.patch("/api/clientes/{cliente_id}/estado", response_model=ClienteOut, dependencies=[Depends(require_api_key)])
def cambiar_estado(cliente_id: int, estado: EstadoCliente, db: Session = Depends(get_db)):
    c = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not c:
        raise NotFoundError(f"Cliente no encontrado: {cliente_id}")

    c.estado = estado.value
    db.commit()
    db.refresh(c)
    return to_out(c)


@app.delete("/api/clientes/{cliente_id}", status_code=204, dependencies=[Depends(require_api_key)])
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    if not c:
        raise NotFoundError(f"Cliente no encontrado: {cliente_id}")

    db.delete(c)
    db.commit()
    return None
