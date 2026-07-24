from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut, UserUpdate

router = APIRouter()


'''Devuelve la lista de todos los usuarios registrados'''
@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #dependes(get-db) indica a FastAPI 
    #antes de ejecutar la funcion, llamaba a get_db()
    #y pasa el resultado como parametro db
    users=db.query(User).all()
    return users

''''Devuelve el perfil del usuario autenticado'''
#debe estar antes de /{user_id} para que 
#FastAPI no lo confunda con un user_id
@router.get("/me", response_model=UserOut) 
def read_current_user(
    current_user: User = Depends(get_current_user)
    ):
    
    return current_user

'''Permite modificar el perfil del usuario autenticado
Solo puede actualizar su propio perfil, no el de otros usuarios.'''
@router.put("/me", response_model=UserOut)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name       
    
    db.commit()
    db.refresh(current_user)

    return current_user

'''Permite desactivar el perfil del usuario autenticado
Solo puede desactivar su propio perfil, no el de otros usuarios.
Los datos permanecen en la BBDD'''
@router.delete("/me", response_model=UserOut)
def deactivate_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    current_user.is_active = False
    db.commit()

    return {"message": "Usuario desactivado correctamente"}

'''Devuelve el perfil de un usuario por su ID'''
@router.get("/{user_id}", response_model=UserOut) 
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user