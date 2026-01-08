import mysql.connector
from mysql.connector import Error
import sys
from datetime import datetime, date, timedelta  # ← ДОБАВЬТЕ ЭТОТ ИМПОРТ!
import random  # ← Тоже нужно для генерации тестовых данных


class Database:
    """Класс для работы с базой данных MySQL"""

    def __init__(self, config):
        self.config = config
        self.connection = None

        print(f"\n🔄 Подключение к базе данных MySQL...")
        print(f"   Хост: {config.MYSQL_HOST}")
        print(f"   Пользователь: {config.MYSQL_USER}")

        # Подключаемся к базе
        if not self.connect():
            print("\n❌ Не удалось подключиться к MySQL серверу!")
            print("💡 Проверьте:")
            print("   1. Запущен ли MySQL сервер")
            print("   2. Правильный ли пароль в config.py")
            sys.exit(1)

        # Создаем таблицы если их нет
        self.create_tables()

        # Добавляем тестовые данные если таблицы пустые
        self.add_sample_data()

        print("✅ База данных готова к работе!")

    def connect(self):
        """Подключение к базе данных"""
        try:
            # Сначала пробуем подключиться без указания базы
            temp_conn = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                port=self.config.MYSQL_PORT,
                auth_plugin='mysql_native_password'
            )

            cursor = temp_conn.cursor()

            # Создаем базу если её нет
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.MYSQL_DATABASE}")
            print(f"✅ База данных '{self.config.MYSQL_DATABASE}' проверена/создана")

            cursor.close()
            temp_conn.close()

            # Теперь подключаемся к конкретной базе
            self.connection = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                port=self.config.MYSQL_PORT
            )

            if self.connection.is_connected():
                print(f"✅ Успешно подключено к базе '{self.config.MYSQL_DATABASE}'")
                return True

        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def create_tables(self):
        """Создание таблиц если их нет"""
        try:
            cursor = self.connection.cursor()

            print("\n🔄 Проверка таблиц...")

            # 1. Таблица клиентов
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
            print("✅ Таблица 'clients' проверена")

            # 2. Таблица услуг
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
            print("✅ Таблица 'services' проверена")

            # 3. Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id INT,
                    service_id INT,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'В работе',
                    total_amount DECIMAL(10,2),
                    notes TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            ''')
            print("✅ Таблица 'orders' проверена")

            # 4. Финансовые операции
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
                    employee_id INT,
                    supplier_id INT,
                    account_id INT,
                    is_recurring BOOLEAN DEFAULT FALSE,
                    recurring_frequency VARCHAR(20),
                    receipt_number VARCHAR(100),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                )
            ''')
            print("✅ Таблица 'financial_transactions' создана")

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"❌ Ошибка создания таблиц: {e}")

    def add_sample_data(self):
        """Добавление тестовых данных если таблицы пустые"""
        try:
            cursor = self.connection.cursor()

            # Проверяем есть ли услуги
            cursor.execute("SELECT COUNT(*) FROM services")
            if cursor.fetchone()[0] == 0:
                print("\n🔄 Добавление тестовых услуг...")
                services = [
                    ('Замена масла', 'Полная замена моторного масла и фильтра', 2000, 60, 'Техобслуживание'),
                    ('Замена тормозных колодок', 'Замена передних и задних тормозных колодок', 5000, 120, 'Ремонт'),
                    ('Диагностика двигателя', 'Компьютерная диагностика двигателя', 1500, 45, 'Диагностика'),
                ]

                cursor.executemany('''
                    INSERT INTO services (name, description, price, duration, category)
                    VALUES (%s, %s, %s, %s, %s)
                ''', services)
                print(f"✅ Добавлено {len(services)} тестовых услуг")

            # Проверяем есть ли клиенты
            cursor.execute("SELECT COUNT(*) FROM clients")
            if cursor.fetchone()[0] == 0:
                print("🔄 Добавление тестовых клиентов...")
                clients = [
                    ('Иван', 'Иванов', '+7 999 123-45-67', 'ivan@mail.ru', 'ул. Ленина, 1'),
                    ('Петр', 'Петров', '+7 999 987-65-43', 'petr@mail.ru', 'ул. Советская, 10'),
                ]

                cursor.executemany('''
                    INSERT INTO clients (first_name, last_name, phone, email, address)
                    VALUES (%s, %s, %s, %s, %s)
                ''', clients)
                print(f"✅ Добавлено {len(clients)} тестовых клиентов")

            # Проверяем есть ли финансовые операции
            cursor.execute("SELECT COUNT(*) FROM financial_transactions")
            if cursor.fetchone()[0] == 0:
                print("🔄 Добавление тестовых финансовых операций...")

                # Используем datetime из импорта
                today = date.today()

                for i in range(20):
                    # Генерируем случайную дату за последние 90 дней
                    transaction_date = today - timedelta(days=random.randint(1, 90))
                    transaction_type = 'income' if random.random() > 0.4 else 'expense'
                    category = 'Ремонт автомобилей' if transaction_type == 'income' else 'Запчасти'
                    amount = random.randint(1000, 50000)

                    cursor.execute('''
                        INSERT INTO financial_transactions 
                        (transaction_date, transaction_type, category, amount, description)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (transaction_date, transaction_type, category, amount, f"Тестовая операция #{i + 1}"))

                print("✅ Добавлено 20 тестовых финансовых операций")

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"❌ Ошибка добавления тестовых данных: {e}")

    # ==================== МЕТОДЫ ДЛЯ КЛИЕНТОВ ====================

    def add_client(self, first_name, last_name, phone="", email="", address=""):
        """Добавление нового клиента"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO clients (first_name, last_name, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
            ''', (first_name, last_name, phone, email, address))

            self.connection.commit()
            client_id = cursor.lastrowid
            cursor.close()

            print(f"✅ Клиент добавлен: {first_name} {last_name} (ID: {client_id})")
            return client_id

        except Error as e:
            print(f"❌ Ошибка добавления клиента: {e}")
            return None

    def get_clients(self):
        """Получение всех клиентов"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM clients ORDER BY id DESC")
            clients = cursor.fetchall()
            cursor.close()

            print(f"📊 Получено {len(clients)} клиентов из базы")
            return clients

        except Error as e:
            print(f"❌ Ошибка получения клиентов: {e}")
            return []

    # ==================== МЕТОДЫ ДЛЯ УСЛУГ ====================

    def get_services(self):
        """Получение всех услуг"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM services ORDER BY id")
            services = cursor.fetchall()
            cursor.close()

            print(f"📊 Получено {len(services)} услуг из базы")
            return services

        except Error as e:
            print(f"❌ Ошибка получения услуг: {e}")
            return []

    def add_service(self, name, description, price, duration, category=""):
        """Добавление новой услуги"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO services (name, description, price, duration, category)
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, description, price, duration, category))

            self.connection.commit()
            service_id = cursor.lastrowid
            cursor.close()

            print(f"✅ Услуга добавлена: {name} (ID: {service_id})")
            return service_id

        except Error as e:
            print(f"❌ Ошибка добавления услуги: {e}")
            return None

    # ==================== МЕТОДЫ ДЛЯ ЗАКАЗОВ ====================

    def add_order(self, client_id, service_id, total_amount, notes="", status=""):
        """Добавление нового заказа"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO orders (client_id, service_id, total_amount, notes, status)
                VALUES (%s, %s, %s, %s, %s)
            ''', (client_id, service_id, total_amount, notes, status))

            self.connection.commit()
            order_id = cursor.lastrowid
            cursor.close()

            print(f"✅ Заказ добавлен (ID: {order_id})")
            return order_id

        except Error as e:
            print(f"❌ Ошибка добавления заказа: {e}")
            return None

    def get_orders(self):
        """Получение всех заказов"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    o.id,
                    COALESCE(c.first_name, '') as first_name,
                    COALESCE(c.last_name, '') as last_name,
                    COALESCE(s.name, 'Неизвестная услуга') as service_name,
                    COALESCE(o.status, 'В работе') as status,  -- ← ВСЕГДА возвращает "В работе" если NULL
                    COALESCE(o.total_amount, 0) as total_amount,
                    o.order_date,
                    COALESCE(o.notes, '') as notes
                FROM orders o
                LEFT JOIN clients c ON o.client_id = c.id
                LEFT JOIN services s ON o.service_id = s.id
                ORDER BY o.id DESC
            ''')
            orders = cursor.fetchall()
            cursor.close()

            print(f"📊 Получено {len(orders)} заказов из базы")

            # Отладка
            if orders:
                for i, order in enumerate(orders[:3]):
                    print(f"🔍 Заказ #{i + 1}: ID={order[0]}, Статус='{order[4]}'")

            return orders

        except Error as e:
            print(f"❌ Ошибка получения заказов: {e}")
            return []

    # ==================== ФИНАНСОВЫЕ МЕТОДЫ ====================

    def add_financial_transaction(self, transaction_date, transaction_type, category,
                                  amount, payment_method="cash", description="",
                                  client_id=None, order_id=None):
        """Добавление финансовой операции"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO financial_transactions 
                (transaction_date, transaction_type, category, description, amount,
                 payment_method, client_id, order_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (transaction_date, transaction_type, category, description, amount,
                  payment_method, client_id, order_id))

            self.connection.commit()
            transaction_id = cursor.lastrowid
            cursor.close()

            print(f"✅ Финансовая операция добавлена (ID: {transaction_id})")
            return transaction_id

        except Error as e:
            print(f"❌ Ошибка добавления финансовой операции: {e}")
            return None

    def get_financial_report(self, period_type="month", year=None, month=None):
        """Получение финансового отчета за период"""
        try:
            cursor = self.connection.cursor()

            # Если год и месяц не указаны, используем текущие
            current_date = datetime.now()
            if year is None:
                year = current_date.year
            if month is None:
                month = current_date.month

            # Определяем условия для периода
            conditions = []
            params = []

            if period_type == "day":
                conditions.append("DATE(transaction_date) = %s")
                params.append(f"{year}-{month:02d}-01")
            elif period_type == "month":
                conditions.append("YEAR(transaction_date) = %s")
                conditions.append("MONTH(transaction_date) = %s")
                params.extend([year, month])
            elif period_type == "year":
                conditions.append("YEAR(transaction_date) = %s")
                params.append(year)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Получаем сводку
            cursor.execute(f'''
                SELECT 
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM financial_transactions
                WHERE {where_clause}
                GROUP BY transaction_type
            ''', params)

            results = cursor.fetchall()

            # Подсчитываем итоги
            total_income = 0
            total_expense = 0
            total_transactions = 0

            for trans_type, count, total in results:
                total_transactions += count
                if trans_type == 'income':
                    total_income = total if total else 0
                elif trans_type == 'expense':
                    total_expense = total if total else 0

            profit = total_income - total_expense

            cursor.close()

            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'profit': profit,
                'total_transactions': total_transactions,
                'report_data': results
            }

        except Error as e:
            print(f"❌ Ошибка получения финансового отчета: {e}")
            return {
                'total_income': 0,
                'total_expense': 0,
                'profit': 0,
                'total_transactions': 0,
                'report_data': []
            }

    def get_monthly_financial_overview(self, year=None):
        """Получение помесячного обзора финансов за год"""
        try:
            cursor = self.connection.cursor()

            if year is None:
                year = datetime.now().year

            cursor.execute('''
                SELECT 
                    MONTH(transaction_date) as month,
                    COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) as expense,
                    COUNT(*) as transactions_count
                FROM financial_transactions
                WHERE YEAR(transaction_date) = %s
                GROUP BY MONTH(transaction_date)
                ORDER BY month
            ''', (year,))

            monthly_data = cursor.fetchall()
            cursor.close()

            # Рассчитываем годовые итоги
            yearly_income = sum(row[1] for row in monthly_data)
            yearly_expense = sum(row[2] for row in monthly_data)
            yearly_profit = yearly_income - yearly_expense

            return {
                'monthly_data': monthly_data,
                'year': year,
                'yearly_income': yearly_income,
                'yearly_expense': yearly_expense,
                'yearly_profit': yearly_profit
            }

        except Error as e:
            print(f"❌ Ошибка получения помесячного отчета: {e}")
            return {
                'monthly_data': [],
                'year': year or datetime.now().year,
                'yearly_income': 0,
                'yearly_expense': 0,
                'yearly_profit': 0
            }

    def get_top_categories(self, year=None, month=None, limit=10):
        """Получение топ категорий доходов/расходов"""
        try:
            cursor = self.connection.cursor()

            if year is None:
                year = datetime.now().year

            conditions = ["YEAR(transaction_date) = %s"]
            params = [year]

            if month:
                conditions.append("MONTH(transaction_date) = %s")
                params.append(month)

            where_clause = " AND ".join(conditions)

            # Топ категорий доходов
            cursor.execute(f'''
                SELECT 
                    category,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM financial_transactions
                WHERE {where_clause} AND transaction_type = 'income'
                GROUP BY category
                ORDER BY total_amount DESC
                LIMIT %s
            ''', params + [limit])

            top_income_categories = cursor.fetchall()

            # Топ категорий расходов
            cursor.execute(f'''
                SELECT 
                    category,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM financial_transactions
                WHERE {where_clause} AND transaction_type = 'expense'
                GROUP BY category
                ORDER BY total_amount DESC
                LIMIT %s
            ''', params + [limit])

            top_expense_categories = cursor.fetchall()

            cursor.close()

            return {
                'top_income_categories': top_income_categories,
                'top_expense_categories': top_expense_categories
            }

        except Error as e:
            print(f"❌ Ошибка получения топ категорий: {e}")
            return {
                'top_income_categories': [],
                'top_expense_categories': []
            }

    # ==================== ИСПРАВЛЕННЫЕ МЕТОДЫ ДЛЯ ЗАКАЗОВ ====================

    def add_order_with_status(self, client_id, service_id, total_amount, status="В работе", notes=""):
        """Добавление нового заказа с указанием статуса"""
        try:
            cursor = self.connection.cursor()

            print(f"📝 СОЗДАНИЕ ЗАКАЗА: клиент={client_id}, статус='{status}', сумма={total_amount}")

            # Проверяем существование клиента и услуги
            cursor.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if not cursor.fetchone():
                print(f"❌ Клиент с ID {client_id} не найден!")
                cursor.close()
                return None

            cursor.execute("SELECT id FROM services WHERE id = %s", (service_id,))
            if not cursor.fetchone():
                print(f"❌ Услуга с ID {service_id} не найдена!")
                cursor.close()
                return None

                cursor.execute('''
                        UPDATE orders SET status = %s 
                        WHERE id = %s AND (status IS NULL OR status = '')
                    ''', (status, order_id))

            print(f"✅ Дополнительная проверка: статус заказа #{order_id} гарантированно '{status}'")

            # ВАЖНО: явно указываем статус
            sql = '''
                INSERT INTO orders (client_id, service_id, total_amount, status, notes)
                VALUES (%s, %s, %s, %s, %s)
            '''
            params = (client_id, service_id, total_amount, status, notes or None)

            print(f"🔍 SQL: {sql}")
            print(f"🔍 Параметры: {params}")

            cursor.execute(sql, params)
            order_id = cursor.lastrowid

            print(f"✅ Заказ #{order_id} создан со статусом '{status}'")

            # Проверяем что сохранилось
            cursor.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            saved_status = cursor.fetchone()[0]
            print(f"✅ Проверка: сохранённый статус = '{saved_status}'")

            # Создаем финансовую операцию
            try:
                self.add_income_from_order(
                    order_id=order_id,
                    client_id=client_id,
                    amount=total_amount,
                    description=f"Заказ #{order_id}"
                )
            except:
                print("⚠️  Не удалось создать финансовую операцию")

            self.connection.commit()
            cursor.close()

            return order_id

        except Error as e:
            print(f"❌ Ошибка при создании заказа: {e}")
            return None

    def add_income_from_order(self, order_id, client_id, amount, description=""):
        """Добавление дохода от заказа"""
        try:
            cursor = self.connection.cursor()

            cursor.execute('''
                INSERT INTO financial_transactions 
                (transaction_date, transaction_type, category, amount, description, order_id, client_id)
                VALUES (CURDATE(), 'income', 'Ремонт автомобилей', %s, %s, %s, %s)
            ''', (amount, description, order_id, client_id))

            transaction_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()

            print(f"✅ Финансовая операция #{transaction_id} создана для заказа #{order_id}")
            return transaction_id

        except Error as e:
            print(f"❌ Ошибка создания финансовой операции: {e}")
            return None

    # ==================== МЕТОДЫ УДАЛЕНИЯ ====================

    def delete_client(self, client_id):
        """Удаление клиента"""
        try:
            cursor = self.connection.cursor()

            # Проверяем, есть ли у клиента заказы
            cursor.execute("SELECT COUNT(*) FROM orders WHERE client_id = %s", (client_id,))
            order_count = cursor.fetchone()[0]

            if order_count > 0:
                cursor.close()
                return False, f"Нельзя удалить клиента с {order_count} заказом(ами)"

            cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            rows_deleted = cursor.rowcount

            self.connection.commit()
            cursor.close()

            if rows_deleted > 0:
                return True, "Клиент удален"
            else:
                return False, "Клиент не найден"

        except Error as e:
            return False, f"Ошибка: {e}"

    def delete_service(self, service_id):
        """Удаление услуги"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM orders WHERE service_id = %s", (service_id,))
            order_count = cursor.fetchone()[0]

            if order_count > 0:
                cursor.close()
                return False, f"Нельзя удалить услугу, используемую в {order_count} заказ(ах)"

            cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
            rows_deleted = cursor.rowcount

            self.connection.commit()
            cursor.close()

            if rows_deleted > 0:
                return True, "Услуга удалена"
            else:
                return False, "Услуга не найдена"

        except Error as e:
            return False, f"Ошибка: {e}"

    def delete_order(self, order_id):
        """Удаление заказа"""
        try:
            cursor = self.connection.cursor()

            # Сначала удаляем финансовую операцию
            cursor.execute("DELETE FROM financial_transactions WHERE order_id = %s", (order_id,))

            # Затем удаляем заказ
            cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
            rows_deleted = cursor.rowcount

            self.connection.commit()
            cursor.close()

            if rows_deleted > 0:
                return True, "Заказ удален"
            else:
                return False, "Заказ не найден"

        except Error as e:
            return False, f"Ошибка: {e}"

    def close(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Соединение с базой данных закрыто")