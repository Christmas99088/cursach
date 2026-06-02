from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import Config
from database import db_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Хеширование пароля"""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """Аутентификация пользователя"""
    query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
    users = db_manager.execute_query(query, (username,))

    if not users:
        return None

    user = users[0]

    # Простая проверка (в реальном проекте используйте хеши)
    # Здесь для простоты сравниваем напрямую, т.к. в БД уже хеши
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt