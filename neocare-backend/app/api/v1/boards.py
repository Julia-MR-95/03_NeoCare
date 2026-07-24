'''Sólo los usuarios autenticados pueden acceder al tablero compartido.
Los dueños de los boards (owner_id) pueden crear, listar (los propios), 
ver uno en concreto y modificar.
Las tarjetas sólo pueden ser modificadas por los usuarios que las crearon'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import Board, User
from app.schemas.schemas import BoardCreate, BoardOut, BoardUpdate

router = APIRouter() #creamos router vacío
                        #cada @router.algo se añade a este objeto
                        #luego conecta en main.py con la app

'''Crear un tablero'''
@router.post("/", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(
    board_data: BoardCreate, #recibimos info de petición HTTP en JSON
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) #si la funcion funciona nos pasa el objeto User entero
    ):
    new_board = Board(
        title=board_data.title,
        owner_id=current_user.id  # Asignar el ID del usuario autenticado como owner_id
    )

    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

'''Listar todos los tableros: es compartido entre usuarios autenticados'''
@router.get("/", response_model=List[BoardOut]) #GET para leer datos | List-> devuelve una lista con objetos BoardOut
def list_boards(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    boards = db.query(Board).all() #todos los usuarios acreditados pueden ver 1 tablero común
    return boards

'''Ver un tableros específico para cualquier usuario autenticado'''
@router.get("/{board_id}", response_model=BoardOut)
def get_board(
    board_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    board = db.query(Board).filter(Board.id == board_id).first() #buscamos el board por su ID
    
    if not board: #board no encontrado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tablero no encontrado"
            )

    return board

'''Modificar el nombre deun tablero'''
@router.put("/{board_id}", response_model=BoardOut)
def update_board(
    board_id: int, 
    board_data: BoardUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Board no encontrado"
        )
    if board.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para modificar este board"
        )
    board.title = board_data.title
    db.commit()
    db.refresh(board)
    return board

'''Borrar un tablero'''
@router.delete("/{board_id}", response_model=BoardOut)
def delete_board(
    board_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Board no encontrado"
        )
    if board.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para borrar este board"
        )
    db.delete(board)
    db.commit()
    return board