from sqlalchemy import (Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Table, CheckConstraint)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

# Tabla pivote para relación N:N entre cards y labels
card_labels = Table('card_labels', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id', ondelete='CASCADE')),
    Column('label_id', Integer, ForeignKey('labels.id', ondelete='CASCADE'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    #relación con otras clases
    lists = relationship("BoardList", back_populates="board", 
                          order_by="BoardList.order", cascade="all, delete")

class BoardList(Base):
    __tablename__ = "board_lists"
    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)  # Backlog, En Progreso, etc.
    order = Column(Integer, nullable=False, default=0)
    #relación con otras clases
    board = relationship("Board", back_populates="lists")
    cards = relationship("Card", back_populates="list",
                          order_by="Card.order", cascade="all, delete")

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    list_id = Column(Integer, ForeignKey("board_lists.id", ondelete="CASCADE"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True) #se da por completado cuando llegan a la columna COMPLETADO
    #relación con otras clases
    list = relationship("BoardList", back_populates="cards")
    work_logs = relationship("WorkLog", back_populates="card", cascade="all, delete")
    labels = relationship("Label", secondary=card_labels)
    creator=relationship("User", foreign_keys=[creator_id]) #para mostrar el creador
    assignee = relationship("User", foreign_keys=[assignee_id]) #para mostrar responsable en tarjeta

    #función q muestra las horas totales EN las tarjetas 
    @property
    def total_hours(self) -> float:
        '''Suma todas las h registradas (manuales y automáticas)'''
        #print(f"La tarjeta {self.id} tiene {len(self.work_logs)} work_logs: {[wl.hours for wl in self.work_logs]}")  #mensaje interno test
        return round(sum(wl.hours for wl in self.work_logs), 2)
    
    #función para agrupar las horas por usuario
    @property
    def hours_per_user(self) -> list:
        from dataclasses import dataclass
        @dataclass
        class UserHours:
            user_id:int
            user_email: str
            total_hours: float

        totals: dict={}
        for wl in self.work_logs:
            uid = wl.user_id
            if uid not in totals:
                totals[uid] = {
                    'user_id' : uid,
                    'user_email' : wl.user.email if wl.user else str(uid),
                    'total_hours': 0.0 #empieza conteo en cero
                }
            totals[uid]['total_hours']=round(totals[uid]['total_hours'] + wl.hours, 2)
        return list(totals.values())

class WorkLog(Base):
    __tablename__ = "work_logs"
    __table_args__ = (CheckConstraint('hours >= 0.25', name='min_hours'),)
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    hours = Column(Float, nullable=False)  #min 0.25/15min
    date = Column(DateTime(timezone=True), nullable=False)
    note = Column(String(200), nullable=True)  # max  200 caracteres
    is_automatic = Column (Boolean, nullable=False, default=False) #true calcula tiempo solo // false en manual 
    #relación con otras clases
    card = relationship("Card", back_populates="work_logs")
    user = relationship("User") #muestra el wl de cada usuario

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)  # Hex: #FF5733
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"))