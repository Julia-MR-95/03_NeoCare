from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.models import User, Board, BoardList, Card, WorkLog
from app.schemas.schemas import WorkLogCreate, WorkLogOut, WorkLogUpdate

router = APIRouter()

'''Verifica que la tarjeta existe y que el usuario tiene acceso para cualquier acción
tarjeta -> lista -> tabler -> owner_id == user.id'''
def get_card_access(card_id: int, db: Session, current_user: User) -> Card:

    #buscamos la tarjeta en la base de datos
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tarjeta no encontrada"
            )
    
    return card

'''Busca un worklog y verifica que pertenece al usuario autenticado
Sólo el owner_id que registró las horas puede modificarlas o borrarlas'''
def get_worklog_access(worklog_id: int, db: Session, current_user: User) -> WorkLog:
    #buscamso el worklog
    worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if not worklog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registro no encontrado"
            )

    # verificamos que el usuario tenga acceso al worklog
    if worklog.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para acceder a este registro de horas."
            )

    return worklog

'''Registra horas de trabajo en una tarjeta'''
@router.post("/", response_model=WorkLogOut, status_code=status.HTTP_201_CREATED)
def create_worklog(
    worklog_data: WorkLogCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    #verificamos que la tarjeta existe y que el usuario tiene acceso
    get_card_access(worklog_data.card_id, db, current_user)

    #validamos que las horas sean mayores o iguales a 0.25
    #la restricción ya existe en la BBDD per mejor detectar el error aquí
    if worklog_data.hours < 0.25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Las horas deben ser mayores o iguales a 0.25 (15 minutos)"
            )

    #creamos el worklog
    new_worklog = WorkLog(
        card_id=worklog_data.card_id,
        user_id=current_user.id,
        hours=worklog_data.hours,
        date=worklog_data.date,
        note=worklog_data.note
    )

    if worklog_data.date > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=422,
            detail="La fecha no puede ser futura."
        )

    db.add(new_worklog)
    db.commit()
    db.refresh(new_worklog)

    return new_worklog

'''Devuelve TODOS los registros de horas del usuario autenticado, sin filtrar por tarjeta.'''
#debe estar antes de /{worlog_id} para que no lo confunda con un worklog_id
@router.get("/my-logs", response_model=List[WorkLogOut])
def get_my_worklogs(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    #filtramos por user_id para que sólo devuelva los worklogs del usuario autenticado
    worklogs = db.query(WorkLog).filter(
        WorkLog.user_id == current_user.id
        ).order_by(WorkLog.date).all()

    return worklogs


'''Devuelve solo los registros de horas del usuario autenticado para una tarjeta específica.'''
@router.get("/card/{card_id}", response_model=List[WorkLogOut])
def worklogs_by_card(
    card_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    #verificamos que la tarjeta existe y que el usuario tiene acceso
    get_card_access(card_id, db, current_user)

    #q devuelva los worklogs de los usuarios
    worklogs = (
        db.query(WorkLog)
        .filter(WorkLog.card_id == card_id)
        .order_by(WorkLog.date)
        .all()
    ) 
    return worklogs

'''Actualiza el registro de horas de trabajo. 
Sólo el owner_id del worklog puede actualizarlo.'''
@router.put("/{worklog_id}", response_model=WorkLogOut)
def update_worklog(
    worklog_id: int, 
    worklog_data: WorkLogUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    #verificamos que el worklog existe y que el usuario tiene acceso
    worklog = db.query(WorkLog).filter(
        WorkLog.id == worklog_id, 
        WorkLog.user_id == current_user.id
    ).first()
    
    if not worklog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registro de horas no encontrado"
            )

    #validamos las horas nuevas si se proporcionan
    if worklog_data.hours is not None:
        if worklog_data.hours < 0.25:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Las horas deben ser mayores o iguales a 0.25 (15 minutos)"
            )
        worklog.hours = worklog_data.hours

    #actualizamos solo los cmapos cuyo valor se proporciona
    if worklog_data.date is not None:
        worklog.date = worklog_data.date
    if worklog_data.note is not None:
        worklog.note = worklog_data.note
        
    db.commit()
    db.refresh(worklog)
    return worklog

'''Elimina un registro de horas de trabajo.
Sólo el owner_id del worklog puede eliminarlo.'''
@router.delete("/{worklog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worklog(
    worklog_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    #verificamos que el worklog existe y que el usuario tiene acceso
    worklog = get_worklog_access(worklog_id, db, current_user)

    db.delete(worklog)
    db.commit()
    return {"message": "Registro de horas eliminado correctamente"}