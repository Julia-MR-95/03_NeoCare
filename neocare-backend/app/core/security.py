#importaciones necesarias para la seguridad de la API
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import cast, String
import jwt
from jwt.exceptions import PyJWTError
import bcrypt
from app.core.config import settings

#importaciones que relacionan con la seguridad de la API a otros módulos
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer #lee la cabecera Authorization de una peticion HTTP automáticamente
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import User

#"bcrypt" es el algoritmo recomendado
# == SEGURIDAD DE LA API ==
def hash_password(password: str) -> str:
    """Hashea la contraseña en texto plano."""
    password_bytes = password.encode("utf-8")  # Convertir a bytes para bcrypt
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    #cada vez q se llame a la funcion con la MISMA contraseña
    #se obtiene un hash DIFERENTE 
    #veirify_password() se encarga de verificarlo correctamente
    return hashed.decode("utf-8")  # Convertir de bytes a string para almacenar en la BD    

def verify_password(plain_pswd: str, hashed_pswd: str) -> bool:
    """Verifica contraseña entexto plano contra el hash almacenado."""
    return bcrypt.checkpw(
        plain_pswd.encode("utf-8"),
        hashed_pswd.encode("utf-8")
    )

def create_access_token(data: dict) -> str:
    """Genera un JWT con expiración configurada y datos proporcionados."""
    to_encode = data.copy()
    #se trabaja con una copia para no modificar el diccionario original  
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    #"firma" el token con la clave secreta
    #garantiza que nadie pueda modificarlo sin q se detecte
    return encoded

def decode_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza excepción si es inválido."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except PyJWTError:
        raise ValueError("Token inválido o expirado.")
    
# === DEPENDENCIA FASTAPI CON AUTENTICACIÓN ===
#oauth2_scheme le indica a FastAPI dónde está el endpoint de login
#se muestra en /docs el botón "Authorize" para autenticarse y obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

#función para obtener el usuario autenticado a partir del token
def get_current_user(
        token: str = Depends(oauth2_scheme), #antes de llamar a la funcion, ejecuta oauth2_scheme() y pasa el resultado como parametro token,
                                            #coge lo que devuelva y pásalo como parámetro token
        db: Session = Depends(get_db)  #antes de llamar a la funcion, ejecuta get_db() y pasa el resultado como parametro db
) -> User: #anotación de tipo: devuelve un objeto User
    """Obtiene el usuario autenticado a partir del token JWT."""
    #error de autenticación si el token no es válido o ha expirado
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, #tipo de error
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    #decodificar el token y obtener el user_id
    try:
        payload = decode_token(token) #función existe en este módulo
        # try:
        #     payload = decode_token(token)
        #     print("PAYLOAD DECODIFICADO:", payload)  #test error
        # except ValueError as e:
        #     print("ERROR AL DECODIFICAR:", e)          #test error
        #     raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    #extraer el user_id del payload decodificado
    user_id: Optional[int] = payload.get("sub") #sub es el "subject" del token, que es el user_id
                                #.get() devuelve None si no existe la clave "sub" 
                                #evitamos crash
    if user_id is None:
        raise credentials_exception
    
    #extraer el usuario de la base de datos (tablas de models.py)
    #user_id es str en la bbdd, pero int en User así que convertimos User.id en str para la comparativa
    user = db.query(User).filter(cast(User.id, String) == user_id).first()
    #print("USUARIO ENCONTRADO:", user)   #test error
    if user is None:
        raise credentials_exception
    
    return user