'''No crea ni modifica datos, sirve como método de lectura y reporte de información.
Datos: horas-tarjeta, horas-usuario, tarjetas-estado'''

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func #objeto de SQLAlchemy para funciones (SUM, COUNT, AVG, etc.)
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import User, Card, Board, BoardList, WorkLog
from app.schemas.schemas import HoursByCard, HoursByUser, CardsByList

router = APIRouter()

'''Verifica que el tablero compartido exista. 
Si no, lanza un error HTTP.'''
def board_access(
        board_id: int, 
        user: User, 
        db: Session
        ) -> Board:
    
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Tablero no encontrado")
    
    return board


'''Devuelve el total de horas registradas en cada tarjeta de un tableto específico
Ordenadas de mayor a menor'''
@router.get("/board/{board_id}/hours-by-card", response_model=List[HoursByCard])
def get_hours_by_card(
    board_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    board_access(board_id, user, db)
    
    #relaciona las tablas Card, BoardList y Worlog
    #para poder filtrar por board_id y sumar las horas de cada tarjeta
    hours_by_card = (
        db.query(Card.id.label("card_id"), #id de la tarjeta
                Card.title.label("card_title"), #titulo de la tarjeta
                func.sum(WorkLog.hours).label("total_hours")) #suma de horas
        .join(WorkLog, Card.id == WorkLog.card_id) #une Card-WorkLog por card_id
        .join(BoardList, Card.list_id == BoardList.id) #une Card-BoardList
        .filter(BoardList.board_id == board_id) #filtra por board_id
        .group_by(Card.id, Card.title) #agrupa por tarjeta
        .order_by(func.sum(WorkLog.hours).desc()) #suma y ordena de mayor a menor
        .all()
    )
    
    #convertimos los resultados a la forma de HoursByCard
    return [
        HoursByCard(
            card_id=card_id, 
            card_title=card_title,
            total_hours=total_hours
            )
            for card_id, card_title, total_hours in hours_by_card
    ]

'''Devuelve el total de horas registradas por cada usuario en un tablero específico
Ordenadas de mayor a menor'''
@router.get("/board/{board_id}/hours-by-user", response_model=List[HoursByUser])
def get_hours_by_user(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    board_access(board_id, current_user, db)

    hours_by_user = (
        db.query(
            User.id.label("user_id"), #id del usuario
            User.email.label("user_email"), #email del usuario
            func.sum(WorkLog.hours).label("total_hours") #suma de horas
            ) 
        .join(WorkLog, User.id == WorkLog.user_id) #une User-WorkLog por user_id
        .join(Card, WorkLog.card_id == Card.id) #une WorkLog-Card
        .join(BoardList, Card.list_id == BoardList.id) #une Card-BoardList
        .filter(BoardList.board_id == board_id) #filtra por board_id
        .group_by(User.id, User.email) #agrupa por usuario
        .order_by(func.sum(WorkLog.hours).desc()) #suma y ordena de mayor a menor
        .all()
    )
    
    return [
        HoursByUser(
            user_id=user_id,
            user_email=user_email,
            total_hours=total_hours
            )
            for user_id, user_email, total_hours in hours_by_user
    ]

'''Devuelve el total de tarjetas en cada lista de un tableto
según el campo "order" de la lista'''
@router.get("/board/{board_id}/cards-by-list", response_model=List[CardsByList])
def get_cards_by_list(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    board_access(board_id, current_user, db)

    cards_by_list = (
        db.query(
            BoardList.id.label("list_id"), #id de la lista
            BoardList.title.label("list_title"), #titulo de la lista
            func.count(Card.id).label("total_cards") #cuenta de tarjetas
            )
        .outerjoin(Card, BoardList.id == Card.list_id) #une BoardList-Card por list_id
        .filter(BoardList.board_id == board_id) #filtra por board_id
        .group_by(BoardList.id, BoardList.title, BoardList.order) #agrupa por lista
        .order_by(BoardList.order) #ordena por el campo order de la lista
        .all()
    )
    
    return [
        CardsByList(
            list_id=list_id,
            list_title=list_title,
            total_cards=total_cards
            )
            for list_id, list_title, total_cards in cards_by_list
    ]

