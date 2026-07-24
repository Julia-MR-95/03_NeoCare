#conexión a la base de datos y creación de sesión

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#importamos los settings de config.py
from app.core.config import settings

#conexión al motor de la base de datos usando la URL de configuración
engine = create_engine(settings.DATABASE_URL)

#cada petición HTTP usará una sesión independiente
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#CLASE de base q heredan los modelos de la BBDD
Base = declarative_base()

# Dependency para FastAPI: obtiene sesión y la cierra al terminar
def get_db():
    db = SessionLocal() #abre sesión
    try:
        yield db #devuelve la sesión para usarla en los endpoints
    finally:
        db.close()  #cierra aunque haya error, para no dejar sesiones abiertas y saturar la BBDD