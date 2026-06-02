#!/usr/bin/env python3
"""
Скрипт для создания и настройки базы данных MySQL
"""

import mysql.connector
from mysql.connector import Error


def setup_database():
    print("=" * 60)
    print("🔧 НАСТРОЙКА БАЗЫ ДАННЫХ MYSQL ДЛЯ АВТОСЕРВИСА")
    print("=" * 60)

    # Параметры подключения
    host = "localhost"
    user = "root"
    password = input("Введите пароль MySQL (оставьте пустым если нет пароля): ") or "кщще"
    database = "auto_service_db"
    auth_plugin = 'mysql_native_password'


    try:
        # Подключаемся к серверу MySQL
        print(f"\n🔄 Подключение к MySQL серверу {host}...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            auth_plugin=auth_plugin,
        )

        if connection.is_connected():
            print(f"✅ Успешно подключено к MySQL серверу")

            cursor = connection.cursor()

            # Создаём базу данных если её нет
            print(f"\n🔄 Создание базы данных '{database}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"✅ База данных '{database}' создана")

            # Используем базу данных
            cursor.execute(f"USE {database}")

            # Создаём таблицы
            print("\n🔄 Создание таблиц...")

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
            print("✅ Таблица 'clients' создана")

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
            print("✅ Таблица 'services' создана")

            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id INT,
                    service_id INT,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'В работе',  # ← ЭТО ПРОБЛЕМА!
                    total_amount DECIMAL(10,2),
                    notes TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            ''')
            print("✅ Таблица 'orders' создана")

            # Добавляем тестовые данные
            print("\n🔄 Добавление тестовых данных...")

            # Проверяем есть ли уже услуги
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
                print(f"✅ Добавлено {len(services)} тестовых услуг")

            # Добавляем тестовых клиентов
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
                print(f"✅ Добавлено {len(clients)} тестовых клиентов")

            connection.commit()

            print("\n" + "=" * 60)
            print("🎉 БАЗА ДАННЫХ УСПЕШНО НАСТРОЕНА!")
            print("\n📊 СТАТИСТИКА:")

            cursor.execute("SELECT COUNT(*) FROM clients")
            clients_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM services")
            services_count = cursor.fetchone()[0]

            print(f"   • Клиентов: {clients_count}")
            print(f"   • Услуг: {services_count}")
            print("\n📋 ПАРАМЕТРЫ ДЛЯ ПРИЛОЖЕНИЯ:")
            print(f"   MYSQL_HOST = '{host}'")
            print(f"   MYSQL_USER = '{user}'")
            print(f"   MYSQL_PASSWORD = '{password}'" if password else "   MYSQL_PASSWORD = ''")
            print(f"   MYSQL_DATABASE = '{database}'")
            print("=" * 60)

            cursor.close()
            connection.close()

    except Error as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. MySQL сервер не запущен")
        print("2. Неправильный пароль")
        print("3. Нет прав на создание базы данных")
        print("\n💡 РЕШЕНИЕ:")
        print("1. Запустите MySQL сервер")
        print("2. Проверьте пароль в MySQL Workbench")
        print("3. Используйте пользователя с правами root")


if __name__ == "__main__":
    setup_database()