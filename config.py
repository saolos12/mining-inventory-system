import os
from dotenv import load_dotenv

load_dotenv() # Carga variables si tienes un archivo .env local

class Config:
    # Llave de seguridad (Cámbiala por algo random y largo)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_super_secreta_sayd_mining')
    
    # Obtiene la URL de la base de datos de Render
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///mineria_local.db')
    
    # Parche: SQLAlchemy necesita 'postgresql://', pero Render a veces da 'postgres://'
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False