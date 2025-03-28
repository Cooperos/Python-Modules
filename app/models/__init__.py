from .database import Database
from .db_config import DB_CONFIG
from .diploma_repository import DiplomaRepository

try:
    Database.initialize()
except Exception as e:
    print(f"Ошибка при автоматической инициализации базы данных: {e}")
    print("База данных будет инициализирована при первом обращении.") 
    