#abre el .env y permite el uso de la variables
#pydantic valida automáticamente q las variables existan y su tipo sea correcto
#si algo es incorrecto, pydantic lanza un error y no deja iniciar la app

from pydantic_settings import BaseSettings

#los nombres de las variables de entorno deben coincidir con los nombres de las variables en el .env
class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256" #valor por defecto
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 #30 min
    
    # App
    APP_NAME: str = "NeoCare Health API"
    ENVIRONMENT: str = "development"

 #clase interna de configuración q indica dónde encontrar el archivo con las cariables   
    class Config:
        env_file = ".env" #indica que lea el .env

#creamos una única instancia q se usa durante todo el proyecto
settings = Settings()