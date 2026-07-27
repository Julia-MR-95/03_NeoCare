from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, Base
from app.api.v1 import auth, users, boards, lists, cards, worklogs, reports

#crea la aplicación FastAPI
#los parámetros son opcionales pero aparecen en la documentación de la API
app = FastAPI(
    title=settings.APP_NAME,
    descripcion="API para la gestión de proyectos y tareas",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI disponible en /docs
    redoc_url="/redoc" #documentación alternativa disponible en /redoc
)

#crear las tablas en la bd
#en produción lo hace alembic
Base.metadata.create_all(bind=engine)

# CORS (Cross-Origin Resource Sharing) mecanismo de seguridad del navegador
# permite peticiones desde el frontend q tiene url distinta al API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
    "https://03-neo-care.vercel.app"],
    allow_credentials=True, #permite enviar cookies
    allow_methods=["*"], #permite todos los métodos
    allow_headers=["*"], #permite todas las cabeceras
)

# Registrar routers
#router: conjunto de endpoints relacionados con un recurso
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(boards.router, prefix="/api/v1/boards", tags=["boards"])
app.include_router(lists.router, prefix="/api/v1/lists", tags=["lists"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["cards"])
app.include_router(worklogs.router, prefix="/api/v1/worklogs", tags=["worklogs"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

#ruta raiz para comprobar que la API funciona
@app.get("/", tags=["Estado"])
def read_root():
    return {"message": "API funcionando correctamente",
            "docs":"/docs"}

