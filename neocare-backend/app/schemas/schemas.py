from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

# === USUARIO ===
class UserCreate(BaseModel):
    '''Datos que el cliente envía para registrar a un usuario'''
    email: EmailStr #automáticamente comprueba que sea un email válido
    password: str #contraseña en texto plano, se hasheará antes de guardar en la BD
    full_name: Optional[str] = None

    @field_validator("password", mode="before")
    @classmethod
    def password_to_string(cls, value):
        return str(value)

class UserOut(BaseModel):
    '''Datos del usuario que devuelve la API (sin contraseña)'''
    id: int
    email: EmailStr
    full_name: str 
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True #permite usar nombres de atributos de SQLAlchemy

class UserSimple(BaseModel):
    #datos básicos que mostrar en las tarjetas
    id: int
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    '''Datos para actualizar un usuario'''
    #de momento sólo el nombre
    full_name: Optional[str] = None


# === TOKEN ===
class Token(BaseModel):
    '''Respuesta del endpoint /login con el token de acceso''' 
    access_token: str
    token_type: str

class TokenData(BaseModel):
    '''Datos extraídos del token JWT decodificado'''
    user_id: Optional[int] = None

# === BOARD ===
class BoardCreate(BaseModel):
    title: str


class BoardOut(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BoardUpdate(BaseModel):
    title: str


# === LIST ===
class ListCreate(BaseModel):
    title: str
    board_id: int
    order: Optional[int] = 0

class ListOut(BaseModel):
    id: int
    title: str
    board_id: int
    order: int

    class Config:
        from_attributes = True

class ListUpdate(BaseModel):
    title: str
    order: Optional[int] = 0


# === CARDS ===
class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    list_id: int
    assignee_id: Optional[int] = None
    assignee: Optional[UserSimple] = None #mostrar datos responsable tarjeta
    due_date: Optional[datetime] = None
    order: Optional[int] = 0

'''Resume la horas de un usuario en una tarjeta concreta'''
class HoursPerUser(BaseModel):
    user_id: int
    user_email: str
    total_hours: float

    class Config:
        from_attributes = True


'''Datos que devuelve la API al consultar un tarjeta'''
class CardOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    list_id: int
    creator_id: int #obligatorio

    assignee_id: Optional[int] = None
    assignee: Optional[UserSimple] = None #datos básicos usuario

    due_date: Optional[datetime] = None
    order: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None #no completado al momento de crearse

    total_hours: float = 0 #inicio de hs totales es 0
    hours_per_user: List[HoursPerUser] = [] #muestras horas wl por usuario

    class Config:
        from_attributes = True

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    order: Optional[int] = None #permite mover la tarjeta a otra lista
    list_id: Optional[int] = None


# === WORKLOG ===
class WorkLogCreate(BaseModel):
    card_id: int
    hours: float = Field(ge=0.25, description="Mínimo 15 minutos (0.25h)")
    date: datetime
    note: Optional[str] = Field(default=None, max_length=200)
    

class WorkLogOut(BaseModel):
    id: int
    card_id: int
    user_id: int
    hours: float
    date: datetime
    note: Optional[str] = None
    is_automatic: bool = False #relleno manual de horas por defecto

    class Config:
        from_attributes = True

class WorkLogUpdate(BaseModel):
    hours: Optional[float] = None
    date: Optional[datetime] = None
    note: Optional[str] = None


# === LABEL ===
class LabelCreate(BaseModel):
    title: str
    color: str #formato hex #FF5733
    board_id: int

class LabelOut(BaseModel):
    id: int
    title: str
    color: str
    board_id: int

    class Config:
        from_attributes = True


# === REPORT ===
#son respuestas del servidor, no se crean ni modifican datos
class HoursByCard(BaseModel):
    card_id: int
    card_title: str
    total_hours: float

    class Config:
        from_attributes = True

class HoursByUser(BaseModel):
    user_id: int
    user_email: EmailStr
    total_hours: float

    class Config:
        from_attributes = True

class CardsByList(BaseModel):
    list_id: int
    list_title: str
    total_cards: int

    class Config:
        from_attributes = True