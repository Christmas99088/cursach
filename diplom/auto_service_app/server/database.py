import mysql.connector
from mysql.connector import Error
from config import Config
import json
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config.DB_HOST,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME,
                port=self.config.DB_PORT
            )
            print(f"✅ Подключено к БД: {self.config.DB_HOST}/{self.config.DB_NAME}")
            return True
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def execute_query(self, query: str, params: tuple = None, fetch=True):
        """Выполнение SQL запроса"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return {'affected_rows': cursor.rowcount, 'last_insert_id': last_id}
        except Error as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            return {'error': str(e)}

    def close(self):
        if self.connection:
            self.connection.close()
            print("🔌 Соединение с БД закрыто")


# Создаём глобальный экземпляр
db_manager = DatabaseManager()