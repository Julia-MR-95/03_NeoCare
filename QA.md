# QA - Neocare

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

3. Boards: /api/v1/boards

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
| test_auth.py | Registro, login (in)correcto, rutas protegidas con/sin token, contraseña siempre tratada como texto |
| test_card.py | Crear/ver/editar/borrar tarjetas, permisos de creator, arrastrar y soltar entre columnas, reordenar dentro de la misma columna |
| test_worklogs.py | Validación mínima de horas (0.25h), fechas futuras rechazadas, límite de 200 caracteres en notas, permisos de regisgtros, suma total por tarjeta |
| test_reports.py | Cálculo de horas por tarteja y por usuario, acceso compartido a informes |
| test_permissions.py | tablero compartido (visibilidad entre usuarios), no fuga de contraseñas, cálculo automático de horas al completar tarjetas |

## Incidencias detectadas y resueltas durante el QA
### Backend
| # | Bug | Causa | Corrección |
| :--- | :---: | :---: | ---: |
1 | 'ModuleNotFoundError: No mocule named 'app'' | Uvicorn ejecutado desde carpeta raíz incorrecta | Ejecutar desde 'neocare-backend'
2 | Faltaban __init__.py en subcarpetas | No se habían creado | Creados en 'app/', 'api/v1', 'core/', 'models/', 'schemas/'.
3 | uvicorn apuntaba al Python global, no al venv | PATH del sistema | Uso de '../.venv/bin/python -m uvicorn'
4 | Conflicto 'jose' vs 'PyJWT' | Librería incorrecta importada | Migrado a 'PyJWT' ('import jwt', 'PyJWTError')
5 | Conflicto 'passlib' vs 'bycript' | Librería desactualizada | Migrado a 'bcrypt' directo ('bcript.hashpw', 'bcrypt.checkpw')
6 | 'config.py' leía '.env.example' en vez de '.env' | Error de configuración | Corregido 'env_file = ".env"'
7 | Inconsistencia 'name' vs 'title' en Board/BoardList/Label | Falta de convención unificada | Unificado a 'title' en todos los modelos y schemas
8 | Inconsistencia 'owner_id' vs 'assignee_id' en Card/Board | Confusión conceptual entre dueño de board y responsable de tarjeta | 'Baord.owner_id' vs 'Card.assignee_id'
9 | Funciones auxiliares con 'Depends()' llamadas manualmente | 'Depends' sólo funciona vía inyección de FastAPI en endpoints | Refactorizadas para recibir 'db' y 'current_user' como parámetros normales
10 | Endpoints duplicados en 'worklogs.py' | Copia accidental de funciones | Eliminados duplicados, un único router limpio
11 | URLs duplicadas '/api/v1/users/user/...' | Prefix en rutas del router + prefix en 'main.py' | Rutas del router simplificadas a '/', '/{user_id}'
12 | 'from_attribute' sin la 's' en varios schemas | Error tipográfico | Corregido a 'from_attributes = True' en todos los 'Config'
13 | 'GET /users' y 'GET /users/{id}' sin autenticación | Faltaba 'Depends(get_current_user)' | Añadida dependencia de autenticación
14 | Router 'lists' no registrado en 'main.py' | Importado pero no incluido con 'include_router' | Añadida línea de registro
15 | 'move_card' fallaba con 'AttributeError' | Typo 'db.quert()' en vez de 'db.query()' | Corregido el nombre
16 | Reordenar tarjetas dentro de la misma columna no hacía nada | Toda la lógica de 'move_card' estaba dentro de un 'if' que solo cubría el cambio de columna | Añadida rama 'else' para el reordenamiento dentro de la misma lista
17 | Mover tarjeta entre columnas no reordenaba bien la lista destino | Copiar-pegar: filtraba 'old_lis_id' dos veces en vez de 'new_list_id' en el segundo bloque | Corregido el filtro
18 | Login funcionaba pero la peticiones posteriores daban 401 | 'user_id' del token (texto) se comparaba directamente con 'User.id' (número) sin convertir | Cast explícito a 'int()'
19 | 'users/me' fallaba de forma intermitente | Un endpoint local sobreescribía el nombre de la dependencia 'get_current_user' importada | Renombrado el handler local
20 | CORS bloqueaba el frontend en local | Backend permitía 'localhost:5000', Vite corre en '5173' | Corregido el puerto permitido
21 | 'requirements.txt' vacío | Nunca se generó | Creado con las dependencias reales detectadas en el código
22 | Actualizar sólo la nota de un registros borraba las horas | 'worklog.hours = worklod_data.hours' ejecutaba sin comprobar si venía 'None' | Solo se actualiza el valor si no es 'None'
23 | 'create_access_token' y 'move_card' fallaban con 'AttributeError: 'datetime.datetime' has no attribute 'datetime'' | Se llamaba a 'datetime.datetime()' habiendo importado ya la clase directamente ('from datetime import datetime') | Sustituido por 'datetime.now(timezone.utc)', y elimina una línea redundante (el modelo ya actualiza 'updated_at' solo)
24 | Login fallaba tras iniciar sesión con contraseñas numéricas | Sin blindaje explícito de tipo | Validador Pydantic que fuerza 'str(v)' antes de validar
25 | 'total_hours'/'hours_per-user' provocaban '500 Internal Server Error' | Dos causas: referencia adelantada innecesaria ('List['HoursPerUser']') que confundía a Pydantic, y un error de sintaxis real ('totals[uid]...' con paréntesis en vez de corchetes) | Quitadas las comilla de la anotación: reescrita la función usando 'dataclass' en vez de diccionarios
26 |'GET /users/' filtraba el hash de la contraseña de todos los usuarios | Endpoint sin 'response_model': FastAPI serializaba el objeto ORM completo | Añadido 'response_model'
27 | Tablero compartido roto tras abrir el tablero a todos los usuarios | 'worklogs.py' y 'reports.py' seguían exigiendo 'board.owner == current_user.id', y bloqueaba a cualquiera que no fuera el creador original del tablero | Quitada de la comprobación de propietario en 'get_card_access' y 'board_access'

### Frontend
| # | Bug | Causa | Corrección |
| :--- | :---: | :---: | ---: |
1 | La app no arrancaba ('Invalid hook call') | Import corregido, dependencias reinstaladas desde cero |
2 | Sesión no persisitía al recargar, redirigía al login sin motivo | Discrepancia de nombre en 'localStorage': se guardaba como 'access_token' pero se leía como 'acess_token'/'acces_token' en distintos puntos | Unificado el nombre en todos los usos |
3 | '/login' no redirigía aunque ya hubiera sesión válida | 'LoginPage' nunca comprobaba 'user'/'loading' del contexto de auth | Añadido 'useEffect' que redirige si ya hay sesión |
4 | Al caducar el token a mitad del uso, tras logearse se aterrizaba en el tablero, nunca en la página de origen | No se guardaba "a dónde ibas" antes de redirigir al login | Se guarda como parámetro '? redirect=' en la URL (que sobrevive a la recargwa completa que dispara el interceptor de axios) |
5 | Tarjetas se veían como texto plano y no se podían arrastrar | Faltabla la clase CSS '.kanban-card'; sin el 'touch-action:none' el navegador competía con 'dond-kit' por interpretar el gesto como selección de texto | Añadidos los estilos y 'touchAction: 'none'' |
6 | El tablero se veía centrado en una cjaa de ancho fijo con columnas cortadas | Restos de una plantilla base | Eliminadas esas reglas |
7 | Varios errores de sintaxis JSX/TS a lo largo del desarrollo | Errores de tecleo al copiar/adaptar el código a mano | Corregiso uno a uno |

### Pytest
| # | Bug | Causa | Corrección |
| :--- | :---: | :---: | ---: |
1 | Error de zonas horarias 'TypeError: can't substract offset-naive and offset-aware datetimes' | 'created_at' era un datetime naive mientras que 'datetime.now(timezone.utc)' era aware | Normalización de 'created_at' a un datetime aware |
2 | Rutas incorrectas en los tests | ---- | Se corrigieron rutas y llamadas al endpoint (especialmente de WorkLogs) |
3 | Enpoint incorrecto en pruebas | ---- | Se ajustaron las pruebas para utilizar el enpoint adecuado |
4 | Error en el informe por usuario |altaba la creación del worklog de Julia para sumarla a la de Carlos | Se añadió la creación del registro faltante |
5 | Eliminación del WorkLog automático | ---- | Se verifica que únicamente se elemina el WorkLog automático y los manuales no se modifican |

### Despliegue
| # | Bug | Causa | Corrección |
| :--- | :---: | :---: | ---: |
| 1 | Render no encontraba requirements.txt | requirements.txt sí existe | Se actualiza y se hace un git push
| 2 | DATABASE_URL incorrecta | La URL proporcionada por Render utilizaba un formato distinto | Se copia la URL interna de PostgreSQL de Render y actualizamos la variable de entorno
| 3 | Push rechazado | git devolvía "Updates were rejected because the remote contains work that you do not have locally" | Se soluciona con git pull --rebase origin main y git push origin main
| 4 | Frontend no iniciaba sesión | Se revisó CORS, VITE_API_URL, rutas /api/v1, AuthContext, Axios, Render y Vercel | Se corrigió la comunicación entre frontend y backend utilizando la URL pública de Render
| 5 | Endopoint incorrecto de WorkLogs | TypeError al intentar acceder a "logs[i]["is_automatic] | El test llamaba al endpoint equivocado | Unificar la ruta utilizada por la API y los tests
| 6 | Rutas "/hours" y "/reports" devolvían 404 | Accediendo manualmente Vercel respondía con error 404 | Se añadieron botones de navegación dentro de la app para utilizar React Router
| 7 | Swagger funcionaba, pero Vercel no | Frontend tenía una configuración incorrecta | Se revisa variables de entorno, URL del backend, CORS, despliegue en Vercel 
| 8 | No hay botones de navegación | No hay botón de "Cerrar sesión" o para redirigir a "/hours" y "/reports" | Se añaden los botones


## Infraestructura verificada
1. Alembic configurado y sincronizado con el esato actual de la BBDD
2. CORS configurado para permitir peticiones del frontend ('localhost:5000', dominio de producción).
3. Documentación automática disponible y funcional en '/docs' (Swagger) y '/redoc'.

## Limitaciones conocidas
| Título | Limitación |
| :--- | :---: | 
| Informes por semana | Los informes actuales son por tablero completo (horas por tarjeta, horas por usuario) sin filtrar por semana ('week=YYYY-WW). No se implementó un endpoint de "tareas completadas/vencidas/creadas recientemnte". |
Mejoras de productividad | Queda pendiente. |
Exportación CSV | Se resolvió el frontend (convierte el JSON ya cargadoa CSV y lo descarga), pero no existe un endpoint de backend dedicado a generar el archivo. |
Columna "de cierre" identificada por nombre exacto | El cálculo automátido de horas (creación -> completado) detecta la columna de cierre buscando el texto exacto "Completado". Si se renombra la columna, deja de detectarse. En una v2 se añadiría un campo 'is_done' a la lista en vez de comparar por título. |
Detalle de horas por tarjeta en FastAPI es privado por usuario | Cada versona ve el desglose de sus propias horas en 'GET /worklogs/card{id}', aunque en el tablero y en '/hours' y '/report' sí es visible para todos los usuarios autenticados. |
Avisos de dependecias obsoletas | Quedan 12 warnings de Pydantic ('class Config' en vez de 'ConfigDict') y SQLAlchemy ('declarative_base()') que no afectan al funcionamiento. Se dejan para no tocar decenas de archivos sin necesidad real. |
Sin pruebas automáticas del frontend | La cobertura de test automáticos es únicamente del backend. El frontent se probó de forma manual |