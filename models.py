from sqlalchemy import Column, Integer, String, Date
from db import Base

class ClienteDB(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    fechaRegistro = Column(Date, nullable=False)
