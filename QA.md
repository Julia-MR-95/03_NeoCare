# Pruebas - Neocare

## Información general:
Proyecto: Tablero de trabajo para NeoCare Health Kanban
Fecha de realización: julio de 2026
Documento de control de calidad (QA) del backend y frontend  de NeoCare Health. En este, se resumen los endpoints probados, su estado actual y los problemas detectados y corregidos durante las pruebas realizadas.

## Pruebas Swagger UI manuales
En desarrollo local (http://127.0.0.1:8000) con PostgreSQL (neocare_db) como base de datos.

Se verificaron un ttoal de 29 endpoints que funcionaron correctamente. Para realizar cualquier acción (excepto registrar usuario) hay que estar autenticado.

1. Auth: /api/v1/auth
Durante el login se usa el flujo estándar OAuth2PasswordRequestForm (username + password). El token JWT expira automáticamente a los 30 minutos (ACCESS_TOKEN_EXPIRE_MINUTES en .env). Tras ese tiempo, hay que volver a autenticarse en /docs. 

| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| POST | /register | 201 created | correcto |
| POST | /login | 200 OK + access_token | correcto |

2. Users: /api/v1/users
El método 'DELETE /me' desactiva la cuenta (is_active = False) sin eliminar el registro para poder preservar integridad referencial con borads/cards/worklogs.
'UserOut' nunca expone 'hashed_password'.

| Método | Ruta | Resultado esperado | Autenticación | Estado |
| :--- | :---: | :---: | :---: | ---: |
| GET | / | 200 OK - lista de usuarios | Sí | correcto |
| GET | /me | 200 OK - prefil propio | Sí | correcto |
| PUT | /me | 200 OK - prefil actualizado | Sí | correcto |
| DELETE | /me | 204 No Content - desactiva cuenta | Sí | correcto |
| GET | /{user_id} | 200 OK - prefil de otro usuario | Sí | correcto |

3. Bosrds: /api/v1/boards
Regla verificada: un usuario sólo puede modificar/eliminar boards de los que es 'owner_id'. 

| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| GET | / | 200 OK | correcto |
| POST | / | 201 Created | correcto |
| GET | /{board_id} | 200 OK | correcto |
| PUT | /{board_id} | 200 OK | correcto |
| DELETE | /{board_id} | 204 No Content | correcto |

4. Lists: /api/v1/lists
| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| POST | / | 201 created | correcto |
| GET | / board/{board_id}| 200 OK -listas creadas por 'order' | correcto |
| PUT | /{list_id} | 200 OK | correcto |
| DELETE | /{list_id} | 204 No Content | correcto |

5. Cards: /api/v1/cards
Reglas verificadas: acceso de lectura validado por cadena 'card -> list -> board -> owner_id'; eliminación ('DELETE') permitido solo al creador.

| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| POST | / | 201 created | correcto |
| GET | /list/{list_id} | 200 OK -tarjetas de una lista | correcto |
| GET | /{card_id} | 200 OK | correcto |
| PUT | /{card_id} | 200 OK | correcto |
| DELETE | /{card_id} | 204 No Content | correcto |


6. Worklog: /api/v1/worklogs
Reglas verificadas: cualquier usuario puede ver las horas registradas por otros usuarios, pero no puede editarlas ni borrarlas; hay un mínimo de horas ('hours >= 0.25') tanto a nivel de API (422) como de base de datos (CheckConstraint).

| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| POST | / | 201 created | correcto |
| GET | /my-logs | 200 OK -todos los registros propios | correcto |
| GET | /card/{card_id} | 200 OK -registros propios de una tarjeta | correcto |
| POST | /{worklog_id} | 200 OK | correcto |
| POST | /{worklog_id} | 204 No Content | correcto |

7. Reports: /api/v1/reports
Todos los usuarios pueden acceder a todos los informes de horas por usuario y horas por tarjeta.
'cards-by-list' usa 'outerjoin' para incluir listas sin tarjetas (con 'total_cards: 0').

| Método | Ruta | Resultado esperado | Estado |
| :--- | :---: | :---: | ---: |
| GET | /board/{board_id}/hours-by-card | 200 OK | correcto |
| GET | /board/{board_id}/hours-by-user | 200 OK | correcto |
| GET | /board/{board_id}/cards-by-list | 200 OK | correcto |

## Pruebas automáticas 'pytest'
35 tests automáticos con 'pytest' en 'neocare-backend/tests/' que corren contra una BBDD SQLite en memoria, aislada de los datos reales.

| Archivo | Qué cubre | 
| :--- | :---: | 
| test | /board/{board_id}/hours-by-card |

## Incidencias detectadas y resueltas durante el QA
1. 'ModuleNotFoundError: No mocule named 'app'' | Uvicorn ejecutado desde carpeta raíz incorrecta | Ejecutar desde 'neocare-backend'
2. Faltaban __init__.py en subcarpetas | No se habían creado | Creados en 'app/', 'api/v1', 'core/', 'models/', 'schemas/'.
3. uvicorn apuntaba al Python global, no al venv | PATH del sistema | Uso de '../.venv/bin/python -m uvicorn'
4. Conflicto 'jose' vs 'PyJWT' | Librería incorrecta importada | Migrado a 'PyJWT' ('import jwt', 'PyJWTError')
5. Conflicto 'passlib' vs 'bycript' | Librería desactualizada | Migrado a 'bcrypt' directo ('bcript.hashpw', 'bcrypt.checkpw')
6. 'config.py' leía '.env.example' en vez de '.env' | Error de configuración | Corregido 'env_file = ".env"'
7. Inconsistencia 'name' vs 'title' en Board/BoardList/Label | Falta de convención unificada | Unificado a 'title' en todos los modelos y schemas
8. Inconsistencia 'owner_id' vs 'assignee_id' en Card/Board | Confusión conceptual entre dueño de board y responsable de tarjeta | 'Baord.owner_id' vs 'Card.assignee_id'
9. Funciones auxiliares con 'Depends()' llamadas manualmente | 'Depends' sólo funciona vía inyección de FastAPI en endpoints | Refactorizadas para recibir 'db' y 'current_user' como parámetros normales
10. Endpoints duplicados en 'worklogs.py' | Copia accidental de funciones | Eliminados duplicados, un único router limpio
11. URLs duplicadas '/api/v1/users/user/...' | Prefix en rutas del router + prefix en 'main.py' | Rutas del router simplificadas a '/', '/{user_id}'
12. 'from_attribute' sin la 's' en varios schemas | Error tipográfico | Corregido a 'from_attributes = True' en todos los 'Config'
13. 'GET /users' y 'GET /users/{id}' sin autenticación | Faltaba 'Depends(get_current_user)' | Añadida dependencia de autenticación
14. Router 'lists' no registrado en 'main.py' | Importado pero no incluido con 'include_router' | Añadida línea de registro

## Infraestructura verificada
1. Alembic configurado y sincronizado con el esato actual de la BBDD
2. CORS configurado para permitir peticiones del frontend ('localhost:5000', dominio de producción).
3. Documentación automática disponible y funcional en '/docs' (Swagger) y '/redoc'.

