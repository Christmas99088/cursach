import mysql.connector
from mysql.connector import Error
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

# ---------------------------- ОСНОВНОЙ КЛАСС DATABASE ----------------------------

class Database:
    """Класс для работы с БД: прямой MySQL + HTTP API (если нужно)"""

    def __init__(self, config):
        self.config = config

        # Параметры MySQL (берём из config или значения по умолчанию)
        self.host = getattr(config, 'MYSQL_HOST', 'localhost')
        self.user = getattr(config, 'MYSQL_USER', 'root')
        self.password = getattr(config, 'MYSQL_PASSWORD', 'root')
        self.database = getattr(config, 'MYSQL_DATABASE', 'auto_service_db')
        self.port = getattr(config, 'MYSQL_PORT', 3306)

        # Параметры API
        self.server_url = getattr(config, 'SERVER_URL', 'http://localhost:8000')
        self.token = None
        self.current_user = None
        self.server = True   # флаг, что используем API, но у нас есть ещё и прямой MySQL

        # Прямое MySQL-соединение
        self.connection = None
        self._connect_mysql()

        # Создаём таблицы, если их нет (для бесперебойной работы)
        self._init_required_tables()

    def _connect_mysql(self):
        """Устанавливает прямое соединение с MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print("✅ Прямое MySQL-подключение установлено")
        except Error as e:
            print(f"❌ Ошибка подключения к MySQL: {e}")
            self.connection = None

    def _init_required_tables(self):
        """Создаёт отсутствующие таблицы, чтобы приложение не падало"""
        if not self.connection:
            return
        cursor = self.connection.cursor()
        # Таблица appointments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                car_id INT NULL,
                service_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                master_name VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE SET NULL,
                FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
            )
        """)
        # Таблица client_cars (если вдруг отсутствует)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_cars (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                brand VARCHAR(50),
                model VARCHAR(50),
                year INT,
                license_plate VARCHAR(20),
                vin VARCHAR(50),
                color VARCHAR(30),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)
        # Таблица service_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                service_date DATE NOT NULL,
                service_type VARCHAR(100),
                mileage INT,
                next_mileage INT,
                cost DECIMAL(10,2),
                master_name VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE CASCADE
            )
        """)
        self.connection.commit()
        cursor.close()
        print("✅ Все необходимые таблицы проверены/созданы")

    # ---------------------------- МЕТОДЫ API (логин, клиенты, услуги, заказы) ----------------------------
    def _make_request(self, method, endpoint, data=None, need_auth=False):
        """Универсальный метод для запросов к API (сохранён как есть)"""
        url = f"{self.server_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if need_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return None

    def login(self, username, password):
        """Авторизация через API"""
        result = self._make_request('POST', '/api/auth/login', {'username': username, 'password': password})
        if result and 'access_token' in result:
            self.token = result['access_token']
            self.current_user = result['user']
            return result['user']
        return None

    def get_clients(self):
        result = self._make_request('GET', '/api/clients', need_auth=True)
        if result:
            return [tuple(client.values()) for client in result]
        return []

    def get_clients_server(self):
        return self.get_clients()

    def add_client(self, first_name, last_name, phone="", email="", address=""):
        result = self._make_request('POST', '/api/clients', {
            'first_name': first_name, 'last_name': last_name, 'phone': phone,
            'email': email, 'address': address
        }, need_auth=True)
        return result.get('id') if result else None

    def delete_client(self, client_id):
        result = self._make_request('DELETE', f'/api/clients/{client_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Клиент удален')
        return False, "Ошибка удаления"

    def get_services(self):
        result = self._make_request('GET', '/api/services', need_auth=True)
        if result:
            return [tuple(service.values()) for service in result]
        return []

    def get_services_server(self):
        return self.get_services()

    def add_service(self, name, description, price, duration, category=""):
        result = self._make_request('POST', '/api/services', {
            'name': name, 'description': description, 'price': float(price),
            'duration': int(duration), 'category': category
        }, need_auth=True)
        return result.get('id') if result else None

    def delete_service(self, service_id):
        result = self._make_request('DELETE', f'/api/services/{service_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Услуга удалена')
        return False, "Ошибка удаления"

    def get_orders(self):
        result = self._make_request('GET', '/api/orders', need_auth=True)
        if result:
            orders = []
            for order in result:
                orders.append((
                    order.get('id'), order.get('first_name', ''), order.get('last_name', ''),
                    order.get('service_name', ''), order.get('status', 'В работе'),
                    order.get('total_amount', 0), order.get('order_date'), order.get('notes', '')
                ))
            return orders
        return []

    def get_orders_server(self):
        return self.get_orders()

    def add_order(self, client_id, service_id, total_amount, notes="", status="В работе"):
        result = self._make_request('POST', '/api/orders', {
            'client_id': client_id, 'service_id': service_id,
            'total_amount': float(total_amount), 'status': status, 'notes': notes
        }, need_auth=True)
        return result.get('id') if result else None

    def add_order_with_status(self, client_id, service_id, total_amount, status="В работе", notes=""):
        return self.add_order(client_id, service_id, total_amount, notes, status)

    def update_order_status(self, order_id, new_status, amount=None, category=None):
        data = {'status': new_status}
        if amount:
            data['amount'] = float(amount) if isinstance(amount, (int, float)) else float(amount.replace(' руб.', ''))
        if category:
            data['category'] = category
        result = self._make_request('PUT', f'/api/orders/{order_id}/status', data, need_auth=True)
        return result is not None

    def delete_order(self, order_id):
        result = self._make_request('DELETE', f'/api/orders/{order_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Заказ удален')
        return False, "Ошибка удаления"

    def get_financial_report(self, period_type="month", year=None, month=None):
        # возвращает заглушку, если нужно – можно реализовать через API
        return {'total_income': 0, 'total_expense': 0, 'profit': 0, 'total_transactions': 0, 'report_data': []}

    def get_financial_report_server(self, period_type="month", year=None, month=None):
        return self.get_financial_report(period_type, year, month)

    def add_financial_transaction(self, *args, **kwargs):
        pass

    def get_statistics(self):
        return {}

    def get_client_count(self):
        return len(self.get_clients())

    def get_service_count(self):
        return len(self.get_services())

    def get_order_count(self):
        return len(self.get_orders())

    def get_total_income(self):
        return 0

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 MySQL-соединение закрыто")


# ---------------------------- КЛАСС APPOINTMENT_MANAGER ----------------------------
class AppointmentManager:
    """Менеджер для работы с записями (appointments) через прямое MySQL-соединение"""

    def __init__(self, db):
        self.db = db   # db.connection должен быть активен

    def get_available_slots(self, date, master_name=None):
        """Возвращает список свободных временных слотов (упрощённо – все стандартные)"""
        slots = [
            {"time": "09:00", "time_end": "10:00", "master": master_name or "Любой мастер"},
            {"time": "10:00", "time_end": "11:00", "master": master_name or "Любой мастер"},
            {"time": "11:00", "time_end": "12:00", "master": master_name or "Любой мастер"},
            {"time": "12:00", "time_end": "13:00", "master": master_name or "Любой мастер"},
            {"time": "13:00", "time_end": "14:00", "master": master_name or "Любой мастер"},
            {"time": "14:00", "time_end": "15:00", "master": master_name or "Любой мастер"},
            {"time": "15:00", "time_end": "16:00", "master": master_name or "Любой мастер"},
            {"time": "16:00", "time_end": "17:00", "master": master_name or "Любой мастер"},
            {"time": "17:00", "time_end": "18:00", "master": master_name or "Любой мастер"},
        ]
        # При желании здесь можно проверять уже занятые слоты из БД
        return slots

    def create_appointment(self, client_id, car_id, service_id, appointment_date, appointment_time, master_name, notes=""):
        """Создаёт новую запись в таблице appointments"""
        if not self.db.connection:
            raise Exception("Нет подключения к БД")
        cursor = self.db.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO appointments 
                (client_id, car_id, service_id, appointment_date, appointment_time, master_name, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (client_id, car_id, service_id, appointment_date, appointment_time, master_name, notes))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.db.connection.rollback()
            raise e
        finally:
            cursor.close()

    def get_appointments(self, date=None, client_id=None, status=None):
        """Возвращает список записей с фильтрами"""
        if not self.db.connection:
            return []
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
            SELECT a.*, 
                   c.first_name, c.last_name, c.phone,
                   ct.brand, ct.model, ct.license_plate,
                   s.name as service_name
            FROM appointments a
            LEFT JOIN clients c ON a.client_id = c.id
            LEFT JOIN client_cars ct ON a.car_id = ct.id
            LEFT JOIN services s ON a.service_id = s.id
            WHERE 1=1
        """
        params = []
        if date:
            query += " AND a.appointment_date = %s"
            params.append(date)
        if client_id:
            query += " AND a.client_id = %s"
            params.append(client_id)
        if status:
            query += " AND a.status = %s"
            params.append(status)
        query += " ORDER BY a.appointment_date, a.appointment_time"
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def update_appointment_status(self, appointment_id, new_status):
        """Обновляет статус записи"""
        if not self.db.connection:
            return False
        cursor = self.db.connection.cursor()
        try:
            cursor.execute("UPDATE appointments SET status = %s WHERE id = %s", (new_status, appointment_id))
            self.db.connection.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()


# ---------------------------- КЛАССЫ ДЛЯ СОВМЕСТИМОСТИ ----------------------------
class UserManager:
    def __init__(self, db):
        self.db = db
        self.current_user = None

    def authenticate(self, username, password):
        user = self.db.login(username, password)
        if user:
            self.current_user = user
            return user
        return None

    def logout(self):
        self.current_user = None

    def check_permission(self, permission):
        if not self.current_user:
            return False
        role = self.current_user.get('role')
        if role == 'admin':
            return True
        role_permissions = {
            'manager': ['view_clients', 'edit_clients', 'view_services', 'edit_services',
                        'view_orders', 'edit_orders', 'view_finance', 'view_reports', 'export_reports'],
            'master': ['view_clients', 'view_services', 'view_orders', 'edit_orders'],
            'cashier': ['view_clients', 'view_orders', 'view_finance', 'edit_finance']
        }
        return permission in role_permissions.get(role, [])

    def get_all_users(self):
        if self.current_user:
            return [self.current_user]
        return []

    def add_user(self, *args, **kwargs):
        return None

    def update_user(self, *args, **kwargs):
        return False

    def change_password(self, *args, **kwargs):
        return False

    def delete_user(self, *args, **kwargs):
        return False


class AuditLogger:
    def __init__(self, db, user_manager):
        self.db = db
        self.user_manager = user_manager

    def log(self, action_type, entity_type=None, entity_id=None, details=None, **kwargs):
        print(f"📝 Лог: {action_type} - {details}")

    def get_logs(self, limit=100, user_id=None, action_type=None):
        """Заглушка – возвращает пустой список"""
        return []


class ShiftManager:
    def __init__(self, db, user_manager):
        self.db = db
        self.user_manager = user_manager

    def is_shift_active(self, user_id=None):
        return True

    def start_shift(self, user_id=None, note=""):
        return True, "Смена начата"

    def end_shift(self, user_id=None, note=""):
        return True, "Смена завершена"

    def get_current_shift_info(self, user_id=None):
        return None

    def get_shifts_history(self, user_id=None, days=30):
        return []