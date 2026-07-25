from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, timezone

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import User, Board, BoardList, Card, WorkLog
from app.schemas.schemas import CardCreate, CardOut, CardUpdate

router = APIRouter()

'''Función que verifica que la lista existe dentro del tablero compartido entre usuarios autenticados
Recibe db y current_user como parámetros normales, NO Depends'''
def verify_list(
                list_id: int, 
                db: Session, 
                current_user: User) -> BoardList:
    
    board_list = db.query(BoardList).filter(BoardList.id == list_id).first()
    
    if board_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada"
        )

    return board_list


'''Función que busca una card por su ID y verifica que el usuario actual tenga permiso para acceder a ella.
Aunque el tablero es compartido y se pueden ver todas las tarjetas, las modificaciones de estas se limitan a sus creadores.
tarjeta -> lista -> tablero -> propietario == current_user.id'''
def verify_card(
        card_id: int, 
        db: Session , 
        current_user: User
        ) -> Card:
    

    #buscamos la tarjeta por su ID
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada"
        )

    return card

'''Verificamos que el usuario autenticado es el dueño de la tarjeta para permitir que modifique o elimine esta'''
def verify_card_owner(
        card_id: int,
        db: Session,
        current_user: User
        ) -> Card:
    card= verify_card(card_id, db, current_user)
    if card.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sólo quien creó la tarjeta puede modificarla"
        )
    return card


'''Nombre de la columna considerada "cierre" del registro de tiempo. 
Si se renombra en el frontend, también aquí'''
COMPLETED_LIST_TITLE = "Completado"

'''Cuando una tarjeta entra/sale de "Completado" actualizada "completed_at" y crea/borra el registro de hs automçatico
No toca los registros manuales'''
def handle_completion(card: Card, new_list: BoardList, db:Session, current_user: User) -> None:
    entering_completed = new_list.title == COMPLETED_LIST_TITLE and card.completed_at is None
    leaving_completed = new_list.title != COMPLETED_LIST_TITLE and card.completed_at is not None

    if entering_completed:
        created_at=card.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        card.completed_at = now

        hours_passed = (now - created_at).total_seconds() / 3600
        hours_passed = max(0.25, round(hours_passed, 2))
    

        #si ya se había completado antes
        db.query(WorkLog).filter(WorkLog.card_id == card.id, WorkLog.is_automatic == True).delete()

        db.add(WorkLog(
            card_id = card.id,
            user_id=current_user.id,
            hours=hours_passed,
            date=now,
            note="Tiempo automático (de creación a completado)",
            is_automatic=True,
        ))
    elif leaving_completed:
        card.completed_at= None
        db.query(WorkLog).filter(WorkLog.card_id == card.id, WorkLog.is_automatic == True).delete()


'''Crea una nueva tarjeta en una lista específica del usuario autenticado.'''
@router.post("/", response_model=CardOut, status_code=status.HTTP_201_CREATED)
def create_card(
        card_data: CardCreate, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):

    #PRIMERO verificamos que la lista existe y es accesible
    verify_list(card_data.list_id, db, current_user)

    new_card = Card(
        title=card_data.title,
        description=card_data.description,
        list_id=card_data.list_id,
        creator_id=current_user.id,  #asigna el ID del usuario autenticado como creator_id
        assignee_id=card_data.assignee_id,
        due_date=card_data.due_date,
        order=card_data.order or 0  #si no se proporciona un orden, se establece en 0
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


'''Devuelve todas las tarjetas de una lista específica si el usuario autenticado tiene permiso para acceder a ella.'''
@router.get("/list/{list_id}", response_model=List[CardOut])
def list_cards(
        list_id: int, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    #verificamos que la lista existe y el usuario tiene permiso
    verify_list(list_id, db, current_user)
    
    cards = db.query(Card).filter(Card.list_id == list_id).all()
    return cards


'''Devuelve una tarjeta específica si el usuario autenticado tiene permiso para acceder a ella.'''
@router.get("/{card_id}", response_model=CardOut)
def get_card_endpoint(
        card_id: int, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    card = verify_card(card_id, db, current_user)
    return card


'''Actualiza una tarjeta específica si el usuario autenticado tiene permiso para acceder a ella o es el creador.'''
@router.put("/{card_id}", response_model=CardOut)
def update_card(
        card_id: int, 
        card_data: CardUpdate, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):

    #verificamos que la tarjeta existe y el usuario tiene permiso para acceder a ella
    card = verify_card_owner(card_id, db, current_user)

    #al ser datos opcionales, solo actualizamos los campos que se proporcionan
    #if comprueba campo por campo si se proporciona un valor distinto de None, y actualiza el objeto card en consecuencia
    if card_data.title is not None:
        card.title = card_data.title
    if card_data.description is not None:
        card.description = card_data.description
    if card_data.assignee_id is not None:
        card.assignee_id = card_data.assignee_id
    if card_data.due_date is not None:
        card.due_date = card_data.due_date
    if card_data.list_id is not None:
        #verificamos que la lista a la que se quiere move la tarjeta existe y es accesible
        verify_list(card_data.list_id, db, current_user)
        card.list_id = card_data.list_id
        #si el cliente manda un list_id nuevo hay que verificar que tiene acceso a la lista de destino
        #si no, se podría mover una tarjeta a una lista de otro usuario

    db.commit()
    db.refresh(card)
    return card


'''Función que mueve las tarjetas entre las listas/columnas
Conectada con el frontend
Primero se resta 1 a las tarjetas q están por encima & se suma 1 a la columna destino = se actuliza la tarjeta'''
class CardMoveRequest(BaseModel):
    list_id: int #id columna destino
    order: int #posicion deseada

@router.patch("/{card_id}/move", response_model=CardOut)
def move_card(
    card_id: int,
    data: CardMoveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # verificamos que la tarjeta existe y el usuario tiene permiso para modificarla a ella
    card = verify_card_owner(card_id, db, current_user)
    #verificamos q la lista destino es accesible
    target_board_list = verify_list(data.list_id, db, current_user)

    old_list_id = card.list_id
    old_older = card.order
    new_list_id = data.list_id
    new_order = data.order

    #movemos fuera de la lista original
    if old_list_id != new_list_id:
        #reajusta orden en la lista origen (rellenar el hueco q queda vacío)
        db.query(Card).\
            filter(Card.list_id == old_list_id, Card.order > old_older).\
            update({Card.order: Card.order - 1})
    
        #hacemos espacio en la lista destino
        db.query(Card).\
            filter(Card.list_id == new_list_id, Card.order > new_order).\
            update({Card.order: Card.order + 1})

        #actualizamos la tarjeta movida
        card.list_id = new_list_id
        card.order = new_order
        # card.updated_at = datetime.datetime()

    else: #reordenar dentro de la misma lista
        if new_order > old_older:
            db.query(Card).\
                filter(Card.list_id == old_list_id,
                       Card.order > old_older, Card.order <= new_order,
                       Card.id != card.id).\
                update({Card.order : Card.order -1})
        elif new_order < old_older:
            db.query(Card).\
                filter(Card.list_id == old_list_id,
                       Card.order >= new_order, Card.order < old_older,
                       Card.id != card.id).\
                    update({Card.order: Card.order + 1})
        card.order = new_order   

    #no importa si cambió de lista o si se reordenó, hay que comprobar si la lista destino es "Completado"
    handle_completion(card, target_board_list, db, current_user)                

    db.commit()
    db.refresh(card)
    return card


'''Sólo el creador de la tarjeta puede eliminarla.'''
@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
        card_id: int, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    
    card = verify_card_owner(card_id, db, current_user)

    # solo el creador eliminar la tarjeta
    # if card.creator_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, 
    #         detail="No tienes permiso para eliminar esta card"
    #     )
    
    db.delete(card)
    db.commit()
    return {"message": "Tarjeta eliminada correctamente"}
    