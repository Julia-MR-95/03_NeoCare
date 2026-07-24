'''Configuración compartia de pytests.
Cada test corre contra la base de datos SQLite en memoria local, completamente aislada de la base de datos real en Postgres. 
De esta forma, los tests nunca tocan ni ensucian los datos de desarrollo/producción'''
import os

#variables q tienen q existir ANTES de importar nada de APP
#poq app/core/config.py las lee al arrancar c/pydantic-settings
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:") #la BBDD q vive solo en la memoria RAM
os.environ.setdefault("SECRET_KEY", "Clave-Secreta-Solo-Para-Tests")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.db import Base, get_db

@pytest.fixture()
def db_session():
    """Crea una base de datos SQLite en memoria nueva para cada test individual"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread":False},
        poolclass=StaticPool, #para q la memoria persista durante el test
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session 
#yield convierte una func normal en un generador -> "pausa" la funcion devuelve valor y 
#recuerda su estado para reanudarse donde se quedó la próxima vez q se solicite
    finally: 
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db_session):
    """Cliente de pruebas de FastAPI que apunta a la BBDD de TEST"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def register_and_login(client, email="test@neocare.com", password="password123", full_name="Usuario Test"):
    """Registra un usuario y devuelve sus headers de autenticación (bearer token)"""
    client.post("/api/v1/auth/register", json={
        "email": email, "password":password, "full_name":full_name,
    })
    res = client.post(
        "/api/v1/auth/login",
        data={"username":email, "password": password},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}