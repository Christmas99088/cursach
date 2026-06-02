import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SERVER_URL = "http://localhost:8000"
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'auto_service_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # Настройки сервера
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))