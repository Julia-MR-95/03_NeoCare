# Propósito del proyecto
El proyecto es el desarrollo full-stack de una web ligera de uso interno para ayudar a organizar iniciativas, seguir el progreso semanal, registrar las horas invertidas en cada tarea y generar informes claros.

El objetivo es permitir a un usuario autenticado acceder a un tablero kanban, crear y editar tarjetas, moverlas entre columnas de flujo de trabajo (Pendiente, En progreso, En revisión, y Completado) mediante arrastrar y soltar, registrar las horas trabajadas por usuario, revisar hojas de tiempo personales, generar informes semanales, exportar datos e incluir un conjunto pequeño de mejoras útiles de productividad.

# 1. Tecnología usada
## Backend
alembic==1.18.5

annotated-doc==0.0.4

annotated-types==0.7.0

anyio==4.14.1

bcrypt==5.0.0

click==8.4.2

dnspython==2.8.0

email-validator==2.3.0

fastapi==0.138.1

greenlet==3.5.2

h11==0.16.0

idna==3.18

iniconfig==2.3.0

Mako==1.3.12

MarkupSafe==3.0.3

packaging==26.2

pluggy==1.6.0

psycopg2-binary==2.9.12

pwdlib==0.3.0

pydantic==2.13.4

pydantic-settings==2.14.2

pydantic_core==2.46.4

Pygments==2.20.0

PyJWT==2.13.0

pytest==9.1.1

python-dotenv==1.2.2

python-multipart==0.0.32

setuptools==82.0.1

SQLAlchemy==2.0.51

starlette==1.3.1

typing-inspection==0.4.2

typing_extensions==4.15.0

uvicorn==0.49.0

wheel==0.47.0

## Frontend
1. Scripts

dev == vite

build == tsc -b && vite build

lint==eslint

preview==vite preview

2. Dependencias

dnd-kit/core == 6.3.1

dnd-kit/sorable == 10.0.0

dnd-kit/utilities == 3.2.2

axios==1.18.1

react==19.2.7

react-dom==19.2.7

react-router-dom==7.18.1

3. devDependencias

eslint/js==10.0.1

types/node==24.13.2

types/react==19.2.17

types/react-dom==19.2.3

vitejs/plugin-react==6.0.2

eslint==10.5.0

eslint-plugin-react-hooks==7.1.1

esling-plugin-react-refresh==0.5.3

globals==17.6.0

typescript==6.0.2

typescript-eslint==8.61.0

vite==8.1.0

## Pruebas
pytest

testclient de FastAPI

pruebas manuales end-to-end (frontend)

# 2. Configuración local
Requisitos previos: Python 3.11 y PostgreSQL instalado y corriendo | Node.js 18+ y npm

## Backend
cd neocare-backend

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt


cp .env.example .env

alembic upgrade head

python seed_demo_data.py

uvicorn app.main:app --reload --port 8000

La API queda en http://localhost:8000, con documentación interactiva en http://localhost:8000/docs .

## Frontend
cd neocare-frontend

npm install

cp .env.example .env

npm run dev

La app queda en http://localhost:5173 .

# 3. Variables de entorno
1. neocare-backend/.env
DATABASE_URL | cadena de conexión a PostgreSQL

SECRET_KEY | clave para firmar los tokens JWT (única por entorno)

ALGORITHM | algoritmo de firma del JWT (HS256 por defecto)

ACCESS_TOKEN_EXPIRE_MINUTES | minutos de duración de la sesión (30 min)

FRONTEND_URL | URL del frontend desplegado para CORS 

2. neocare-frontend/.env
VITE_API_URL | URL del backend + /api/v1

# 4. Estructura de la BBDD
users            id, email, full_name, hashed_password, is_active, created_at
boards           id, title, owner_id → users, created_at
board_lists      id, board_id → boards, title, order
cards            id, title, description, list_id → board_lists,
                 creator_id → users, assignee_id → users, due_date,
                 order, created_at, updated_at, completed_at
work_logs        id, card_id → cards, user_id → users, hours, date,
                 note, is_automatic
labels           id, title, color, board_id → boards        
card_labels      card_id, label_id    

Relaciones clave: una tarjeta pertenece a una lista; una lista pertenece a un tablero; un registro de horas pertenece a una tarjeta y a un usuario.

El borrado en cascada está configurado en "list_id", "card_id" y "board_id". Si borras un tablero, también se elimina toda la información contenido en él (listas, tarjetas y horas).

Todas las migraciones pueden verse en "neocare-backend/alembic/versions/".

# 5. Enpoints principales de la API
Documentación interactiva completa en "/docs".

| Método | Ruta | Qué hace |
| :--- | :---: | ---: |
POST | /api/v1/auth/register | Crea un usuario nuevo
POST | /api/v1/auth/login | Devuelve un token JWT
GET | /api/v1/users/me | Perfil del usuario autenticado
GET | /api/v1/boards/ | Lista todos los tableros (compartido)
GET/POST | /api/v1/lists/ | Columnas del tablero
GET/POST/PUT/DELETE | /api/v1/cards/ | CRUD de tarjetas (borrado solo por el creador)
PATCH | /api/v1/cards/{id}/move | Mueve/reordena una tarjeta (arrastrar y soltar)
GET/POST/PUT/DELETE | /api/v1/worklogs/ | Registros de horas
GET | /api/v1/reports/board/{id}/hours-by-card | Horas totales por tarjeta
GET | /api/v1/reports/board/{id}/hours-by-user | Horas totales por usuario

# 6. Rutas del frontend
"/login" | Inicio de sesión
"/" | Tablero kanban
"/hours" | Mis horas (vista semanal personal)
"/reports" | Informe de horas por tarjeta/usuario con exportación CSV

Todas las rutas, a excepción de "/login", requieren inicio de sesión y, si el token caduca a mitad de uso, se guarda dónde se encontraba y el reinicio de sesión te devuelve ahí.

# 7. Despliegue en producción
Se sube el proyecto a GitHub desde la consola de Visual Code Studio, y se inicia sesión en ambas tecnologías desde la cuenta de GitHub.
## Render (backend)
Durante el despliegue ha sido necesario modificar la conexión SLQAlchemy para aceptar la  URL proporcionada por Render. El despliegue se ha hecho de forma manual, importando el proyecto desde GitHub.
1. Se crea la BBDD PostgreSQL en Render.
2. Se crea un "Web Service" apuntando al PostgreSQL: 
    Root directory | neocare-backend
    Build command | pip install -r requirements.txt
    Start command | uvicorn app.main:app --host 0.0.0.0 --port $PORT
3. Se añaden las variables de entorno del punto 3 y se usa la "Internal Database URL" de PostgreSQL que proporciona Render para "DATABASE_URL".

## Vercel (frontend)
1. Se importa el repositorio de GitHub con "New Project".
    Root directory | neocare-frontend
    Framework preset | Vite
    Variable de entorno | VITE_API_URL: URL de render + "/api/v1"
