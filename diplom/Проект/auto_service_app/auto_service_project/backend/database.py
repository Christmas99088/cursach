import mysql.connector
from mysql.connector import Error
import json
from typing import List, Dict, Any
from config import Config


class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.connect()

    def connect(self):
        """Подключение к базе данных"""
        try:
            # Сначала подключаемся без указания базы
            temp_conn = mysql.connector.connect(
                host=self.config.DB_HOST,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                port=self.config.DB_PORT
            )

            cursor = temp_conn.cursor()

            # Создаем базу если её нет
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.DB_NAME}")
            cursor.execute(f"USE {self.config.DB_NAME}")

            # Создаем таблицы
            self.create_tables(cursor)

            cursor.close()
            temp_conn.close()

            # Подключаемся к конкретной базе
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

    def create_tables(self, cursor):
        """Создание всех необходимых таблиц"""

        # Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица услуг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2),
                duration INT,
                category VARCHAR(100)
            )
        ''')

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT,
                service_id INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'В работе',
                total_amount DECIMAL(10,2),
                notes TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
                FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
            )
        ''')

        # Таблица финансовых операций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_date DATE NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                amount DECIMAL(12,2) NOT NULL,
                payment_method VARCHAR(50),
                client_id INT,
                order_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
            )
        ''')

        # Добавляем тестовые данные
        self.add_sample_data(cursor)

    def add_sample_data(self, cursor):
        """Добавление тестовых данных"""

        # Проверяем есть ли услуги
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            services = [
                ('Замена масла', 'Полная замена моторного масла и фильтра', 2000, 60, 'Техобслуживание'),
                ('Замена тормозных колодок', 'Замена передних и задних тормозных колодок', 5000, 120, 'Ремонт'),
                ('Диагностика двигателя', 'Компьютерная диагностика двигателя', 1500, 45, 'Диагностика'),
                ('Развал-схождение', 'Регулировка углов установки колес', 3000, 90, 'Ходовая часть'),
                ('Замена аккумулятора', 'Замена автомобильного аккумулятора', 2500, 30, 'Электрика')
            ]
            cursor.executemany('''
                INSERT INTO services (name, description, price, duration, category)
                VALUES (%s, %s, %s, %s, %s)
            ''', services)

        # Проверяем есть ли клиенты
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone()[0] == 0:
            clients = [
                ('Иван', 'Иванов', '+7 999 123-45-67', 'ivan@mail.ru', 'ул. Ленина, 1'),
                ('Петр', 'Петров', '+7 999 987-65-43', 'petr@mail.ru', 'ул. Советская, 10'),
                ('Мария', 'Сидорова', '+7 999 555-44-33', 'maria@mail.ru', 'ул. Центральная, 5'),
            ]
            cursor.executemany('''
                INSERT INTO clients (first_name, last_name, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
            ''', clients)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Выполнение SQL запроса и возврат результата"""
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
                return [{'affected_rows': cursor.rowcount, 'last_insert_id': last_id}]

        except Error as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            return [{'error': str(e)}]

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("🔌 Соединение с БД закрыто")