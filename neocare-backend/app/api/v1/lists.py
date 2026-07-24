from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List as ListType 

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import User, Board, BoardList 
from app.schemas.schemas import ListCreate, ListOut, ListUpdate

router = APIRouter() #creamos router vacío

#cualquier endpoint de lists.py q necesite comprobar permisos sobre un board
#llama a la función y si no pasa ya lanza el error correspondiente
"""Obtiene un board por ID, compartido por todos los usuarios autenticados."""
def get_board_or(board_id: int, db: Session, current_user: User) -> Board:
    board = db.query(Board).filter(Board.id == board_id).first()
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Board no encontrado"
            )
    
    return board

'''Crea una lista dentro de un tablero del usuario atenticado'''
@router.post("/", response_model=ListOut, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_board_or(list_data.board_id, db, current_user)
    
    new_list = BoardList(
        title=list_data.title,
        board_id=list_data.board_id,
        order=list_data.order or 0 #si no se proporciona un orden, se establece en 0 por defecto
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list

'''Devuelve todas las listas de un tablero del usuario autenticado'''
@router.get("/board/{board_id}", response_model=ListType[ListOut]) # == GET /api/ve/lists/board/{board_id}
def lists_by_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_board_or(board_id, db, current_user)
    lists = db.query(BoardList).filter(BoardList.board_id == board_id).all() #de menor a mayor
    return lists

'''Actualiza una lista específica de un tablero del usuario autenticado'''
@router.put("/{list_id}", response_model=ListOut)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    board_list = db.query(BoardList).filter(BoardList.id == list_id).first()
    if board_list is None: #comprobamos que la lista exista
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lista no encontrada"
            )
    
    get_board_or(board_list.board_id, db, current_user) #si la lista existe comprobamos que ese board es del usuario autenticado
    
    board_list.title = list_data.title or board_list.title
    if list_data.order is not None: #order es opcional, si no se proporciona no se actualiza
        board_list.order = list_data.order #se puede renombrar la lista sin tener que reenviar su posición

    db.commit()
    db.refresh(board_list)
    return board_list

'''Elimina una lista específica de un tablero del usuario autenticado'''
@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    board_list = db.query(BoardList).filter(BoardList.id == list_id).first()
    if board_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lista no encontrada"
            )
    
    get_board_or(board_list.board_id, db, current_user)
    
    db.delete(board_list)
    db.commit()