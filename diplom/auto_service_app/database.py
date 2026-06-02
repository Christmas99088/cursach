import requests
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class Database:
    """Класс для работы с сервером через API"""

    def __init__(self, config):
        self.config = config
        self.server_url = config.SERVER_URL
        self.token = None
        self.current_user = None
        self.server = True  # Всегда используем сервер

        print(f"🔌 Подключение к серверу: {self.server_url}")

    def set_token(self, token, user):
        """Установка токена после авторизации"""
        self.token = token
        self.current_user = user

    def _make_request(self, method, endpoint, data=None, need_auth=False):
        """Универсальный метод для запросов к API"""
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
            elif response.status_code == 401:
                print("❌ Не авторизован")
                return None
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.ConnectionError:
            print(f"❌ Не удалось подключиться к серверу {self.server_url}")
            print("   Убедитесь, что сервер запущен (python server/main.py)")
            return None
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return None

    def login(self, username, password):
        """Авторизация на сервере"""
        result = self._make_request('POST', '/api/auth/login', {
            'username': username,
            'password': password
        })

        if result and 'access_token' in result:
            self.token = result['access_token']
            self.current_user = result['user']
            return result['user']
        return None

    # ==================== КЛИЕНТЫ ====================

    def get_clients(self):
        """Получение всех клиентов"""
        result = self._make_request('GET', '/api/clients', need_auth=True)
        if result:
            return [tuple(client.values()) for client in result]
        return []

    def get_clients_server(self):
        return self.get_clients()

    def add_client(self, first_name, last_name, phone="", email="", address=""):
        result = self._make_request('POST', '/api/clients', {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
            'address': address
        }, need_auth=True)
        return result.get('id') if result else None

    def delete_client(self, client_id):
        result = self._make_request('DELETE', f'/api/clients/{client_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Клиент удален')
        return False, "Ошибка удаления"

    # ==================== УСЛУГИ ====================

    def get_services(self):
        result = self._make_request('GET', '/api/services', need_auth=True)
        if result:
            return [tuple(service.values()) for service in result]
        return []

    def get_services_server(self):
        return self.get_services()

    def add_service(self, name, description, price, duration, category=""):
        result = self._make_request('POST', '/api/services', {
            'name': name,
            'description': description,
            'price': float(price),
            'duration': int(duration),
            'category': category
        }, need_auth=True)
        return result.get('id') if result else None

    def delete_service(self, service_id):
        result = self._make_request('DELETE', f'/api/services/{service_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Услуга удалена')
        return False, "Ошибка удаления"

    # ==================== ЗАКАЗЫ ====================

    def get_orders(self):
        result = self._make_request('GET', '/api/orders', need_auth=True)
        if result:
            orders = []
            for order in result:
                orders.append((
                    order.get('id'),
                    order.get('first_name', ''),
                    order.get('last_name', ''),
                    order.get('service_name', ''),
                    order.get('status', 'В работе'),
                    order.get('total_amount', 0),
                    order.get('order_date'),
                    order.get('notes', '')
                ))
            return orders
        return []

    def get_orders_server(self):
        return self.get_orders()

    def add_order(self, client_id, service_id, total_amount, notes="", status="В работе"):
        result = self._make_request('POST', '/api/orders', {
            'client_id': client_id,
            'service_id': service_id,
            'total_amount': float(total_amount),
            'status': status,
            'notes': notes
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

    def update_order_status_server(self, order_id, new_status, amount=None, category=None):
        return self.update_order_status(order_id, new_status, amount, category)

    def delete_order(self, order_id):
        result = self._make_request('DELETE', f'/api/orders/{order_id}', need_auth=True)
        if result:
            return True, result.get('message', 'Заказ удален')
        return False, "Ошибка удаления"

    # ==================== ФИНАНСЫ ====================

    def get_financial_report(self, period_type="month", year=None, month=None):
        params = f"?period_type={period_type}"
        if year:
            params += f"&year={year}"
        if month:
            params += f"&month={month}"

        result = self._make_request('GET', f'/api/financial/report{params}', need_auth=True)
        if result:
            report_data = []
            for row in result.get('report_data', []):
                report_data.append((
                    row.get('transaction_type'),
                    row.get('category'),
                    row.get('count'),
                    row.get('total_amount')
                ))

            return {
                'total_income': result.get('total_income', 0),
                'total_expense': result.get('total_expense', 0),
                'profit': result.get('profit', 0),
                'total_transactions': result.get('total_transactions', 0),
                'report_data': report_data
            }
        return None

    def get_financial_report_server(self, period_type="month", year=None, month=None):
        return self.get_financial_report(period_type, year, month)

    def add_financial_transaction(self, transaction_date, transaction_type, category, amount,
                                  payment_method="cash", description="", client_id=None, order_id=None):
        data = {
            'transaction_date': transaction_date,
            'transaction_type': transaction_type,
            'category': category,
            'amount': float(amount),
            'payment_method': payment_method,
            'description': description
        }
        if client_id:
            data['client_id'] = client_id
        if order_id:
            data['order_id'] = order_id

        result = self._make_request('POST', '/api/financial/transaction', data, need_auth=True)
        return result.get('id') if result else None

    def add_financial_transaction_server(self, transaction_date, transaction_type, category, amount,
                                         payment_method="cash", description="", client_id=None, order_id=None):
        return self.add_financial_transaction(transaction_date, transaction_type, category, amount,
                                              payment_method, description, client_id, order_id)

    # ==================== СТАТИСТИКА ====================

    def get_statistics(self):
        return self._make_request('GET', '/api/statistics', need_auth=True) or {}

    def get_client_count(self):
        stats = self.get_statistics()
        return stats.get('clients_count', 0)

    def get_service_count(self):
        stats = self.get_statistics()
        return stats.get('services_count', 0)

    def get_order_count(self):
        stats = self.get_statistics()
        return stats.get('orders_count', 0)

    def get_total_income(self):
        stats = self.get_statistics()
        return stats.get('total_income', 0)

    # ==================== ДЛЯ СОВМЕСТИМОСТИ ====================

    @property
    def connection(self):
        """Для совместимости со старым кодом"""
        return None

    def close(self):
        """Закрытие соединения"""
        print("🔌 Соединение с сервером закрыто")


# ==================== КЛАССЫ ДЛЯ СОВМЕСТИМОСТИ ====================

class UserManager:
    """Менеджер пользователей для работы через API"""

    def __init__(self, db):
        self.db = db
        self.current_user = None

    def authenticate(self, username, password):
        """Аутентификация через сервер"""
        user = self.db.login(username, password)
        if user:
            self.current_user = user
            return user
        return None

    def logout(self):
        self.current_user = None

    def check_permission(self, permission):
        """Проверка прав (упрощённая)"""
        if not self.current_user:
            return False
        role = self.current_user.get('role')
        if role == 'admin':
            return True
        # Базовые права по ролям
        role_permissions = {
            'manager': ['view_clients', 'edit_clients', 'view_services', 'edit_services',
                        'view_orders', 'edit_orders', 'view_finance', 'view_reports', 'export_reports'],
            'master': ['view_clients', 'view_services', 'view_orders', 'edit_orders'],
            'cashier': ['view_clients', 'view_orders', 'view_finance', 'edit_finance']
        }
        return permission in role_permissions.get(role, [])

    def get_all_users(self):
        """Получение всех пользователей (только для админа)"""
        # Для упрощения возвращаем текущего пользователя
        if self.current_user:
            return [self.current_user]
        return []

    def add_user(self, username, password, role, full_name, email, phone):
        """Добавление пользователя (заглушка)"""
        return None

    def update_user(self, user_id, **kwargs):
        return False

    def change_password(self, user_id, new_password):
        return False

    def delete_user(self, user_id):
        return False


class AuditLogger:
    """Логгер для совместимости"""

    def __init__(self, db, user_manager):
        self.db = db
        self.user_manager = user_manager

    def log(self, action_type, entity_type=None, entity_id=None, details=None, **kwargs):
        print(f"📝 Лог: {action_type} - {details}")


class ShiftManager:
    """Менеджер смен для совместимости"""

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