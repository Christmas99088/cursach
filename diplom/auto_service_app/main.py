import tkinter as tk
from decimal import Decimal
from tkinter import ttk, messagebox, simpledialog

from datetime import datetime

# Импортируем исправленный database.py

from database import Database, UserManager, AuditLogger, ShiftManager
from config import Config
from login_dialog import LoginDialog
from permissions import require_permission, require_role



# Конфигурация базы данных
class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'  # Ваш пароль MySQL
    MYSQL_DATABASE = 'auto_service_db'
    MYSQL_PORT = 3306

    IP_ADDRESS = "http://127.0.0.1"
    SERVER_URL = "http://127.0.0.1:8000"
    PORT = 8002


class AutoServiceApp:
    def __init__(self, root):
        self.root = root

        self.clients_data = []
        self.services_data = []
        self.orders_data = []
        self.clients_tree = None
        self.services_tree = None
        self.orders_tree = None

        # Настройка главного окна
        self.root.title("Система учёта автосервиса")
        self.root.geometry("1200x700")

        # Подключение к БД
        print("🚀 Запуск приложения...")
        self.config = Config()
        self.db = Database(self.config)

        # Инициализация менеджера пользователей
        self.user_manager = UserManager(self.db)

        # Инициализация системы логирования
        from database import AuditLogger
        self.audit_logger = AuditLogger(self.db, self.user_manager)
        self.db.audit_logger = self.audit_logger

        # Показываем окно входа
        login = LoginDialog(self.root, self.user_manager)

        if not login.result:
            self.root.destroy()
            return

        # Сохраняем текущего пользователя
        self.current_user = login.result
        print(f"👤 Текущий пользователь: {self.current_user['full_name']} ({self.current_user['role']})")

        # Инициализация менеджера смен
        self.shift_manager = ShiftManager(self.db, self.user_manager)
        self.db.shift_manager = self.shift_manager

        # Проверяем активность смены
        if not self.check_and_handle_shift():
            # Если смена не начата и пользователь отказался, закрываем приложение
            return

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем данные
        self.load_all_data()

        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_user_panel(self, parent):
        """Создание панели с информацией о пользователе"""
        user_frame = tk.Frame(parent, bg='#34495e', height=45)
        user_frame.pack(fill=tk.X, pady=(0, 10))
        user_frame.pack_propagate(False)

        # Информация о пользователе
        role_names = {
            'admin': '👑 Администратор',
            'manager': '📋 Менеджер',
            'master': '🔧 Мастер',
            'cashier': '💰 Кассир'
        }

        role_text = role_names.get(self.current_user['role'], self.current_user['role'])
        user_info = f"👤 {self.current_user['full_name']} | {role_text}"

        tk.Label(user_frame, text=user_info,
                 font=('Arial', 10), bg='#34495e', fg='white').pack(side=tk.LEFT, padx=20)

        # Информация о смене (для не-админов)
        if self.current_user['role'] != 'admin':
            shift_info = self.shift_manager.get_current_shift_info()
            if shift_info:
                duration = shift_info.get('current_duration', 0)
                hours = duration // 60
                minutes = duration % 60
                shift_text = f"⏰ Смена: {hours}ч {minutes}мин"
                tk.Label(user_frame, text=shift_text,
                         font=('Arial', 9), bg='#34495e', fg='#1abc9c').pack(side=tk.LEFT, padx=15)

        # Кнопка завершения смены (для не-админов)
        if self.current_user['role'] != 'admin' and self.shift_manager.is_shift_active():
            end_shift_btn = tk.Button(user_frame, text="⏹️ Завершить смену",
                                      command=self.end_shift_dialog,
                                      bg='#e67e22', fg='white',
                                      font=('Arial', 9), padx=10)
            end_shift_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка выхода
        logout_btn = tk.Button(user_frame, text="🚪 Выход",
                               command=self.logout,
                               bg='#e74c3c', fg='white',
                               font=('Arial', 9), padx=15)
        logout_btn.pack(side=tk.RIGHT, padx=20)

    def logout(self):
            """Выход из системы"""
            if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из системы?"):
                self.user_manager.logout()
                self.root.destroy()
                # Перезапускаем приложение
                import subprocess
                import sys
                subprocess.Popen([sys.executable, __file__])

    def show_clients_tab(self):
            """Переключение на вкладку клиентов"""
            if hasattr(self, 'notebook'):
                self.notebook.select(0)

    def show_services_tab(self):
            """Переключение на вкладку услуг"""
            if hasattr(self, 'notebook'):
                self.notebook.select(1)

    def show_orders_tab(self):
            """Переключение на вкладку заказов"""
            if hasattr(self, 'notebook'):
                self.notebook.select(2)

    def show_finance_tab(self):
            """Переключение на вкладку финансов"""
            if hasattr(self, 'notebook'):
                self.notebook.select(3)

    def show_admin_tab(self):
            """Переключение на вкладку администрирования"""
            if hasattr(self, 'notebook') and self.user_manager.check_permission('manage_users'):
                self.notebook.select(4)

    def create_admin_tab(self):
            """Создание вкладки администрирования"""
            try:
                from admin_tab import AdminTab
                admin_tab = AdminTab(self.notebook, self.db, self.user_manager)
                self.notebook.add(admin_tab.get_tab(), text="⚙️ Администрирование")
            except ImportError:
                # Если файла admin_tab.py нет, создаем простую версию
                self.create_simple_admin_tab()

    def create_simple_admin_tab(self):
            """Простая версия вкладки администрирования (если нет admin_tab.py)"""
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text="⚙️ Администрирование")

            tk.Label(tab, text="Управление пользователями",
                     font=('Arial', 14, 'bold')).pack(pady=10)

            # Таблица пользователей
            columns = ('ID', 'Логин', 'ФИО', 'Роль', 'Активен')
            tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Загружаем пользователей
            users = self.user_manager.get_all_users()
            for user in users:
                tree.insert('', tk.END, values=(
                    user.get('id'),
                    user.get('username'),
                    user.get('full_name'),
                    user.get('role'),
                    'Да' if user.get('is_active') else 'Нет'
                ))

            # Кнопка обновления
            def refresh():
                for row in tree.get_children():
                    tree.delete(row)
                users = self.user_manager.get_all_users()
                for user in users:
                    tree.insert('', tk.END, values=(
                        user.get('id'),
                        user.get('username'),
                        user.get('full_name'),
                        user.get('role'),
                        'Да' if user.get('is_active') else 'Нет'
                    ))

            tk.Button(tab, text="🔄 Обновить", command=refresh,
                      bg='#3498db', fg='white', padx=15).pack(pady=5)

            tk.Label(tab, text="Для полного управления пользователями создайте файл admin_tab.py",
                     font=('Arial', 9), fg='gray').pack(pady=5)

    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя панель с информацией о пользователе
        self.create_user_panel(main_container)

        # Верхняя панель с кнопками
        self.create_top_panel(main_container)

        # Панель вкладок
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Создаем вкладки (только те, к которым есть доступ)
        if self.user_manager.check_permission('view_clients'):
            self.create_clients_tab()

        if self.user_manager.check_permission('view_services'):
            self.create_services_tab()

        if self.user_manager.check_permission('view_orders'):
            self.create_orders_tab()

        # Финансы - только для админа, менеджера и кассира
        if self.user_manager.check_permission('view_finance'):
            self.create_finance_tab()

        # Администрирование - только для админа
        if self.user_manager.check_permission('manage_users'):
            self.create_admin_tab()

        # Вкладка логов - только для админа
        if self.user_manager.check_permission('view_logs'):
            from logs_tab import LogsTab
            logs_tab = LogsTab(self.notebook, self.db, self.user_manager)
            self.notebook.add(logs_tab.get_tab(), text="📋 Логи")

        # Вкладка записи клиентов
        if self.user_manager.check_permission('view_orders'):
            from appointments_tab import AppointmentsTab
            appointments_tab = AppointmentsTab(self.notebook, self.db, self.user_manager)
            self.notebook.add(appointments_tab.get_tab(), text="📅 Запись")

        # Расширенная финансовая аналитика
        if self.user_manager.check_permission('view_reports'):
            from financial_analytics import FinancialAnalytics
            analytics_tab = FinancialAnalytics(self.notebook, self.db, self.user_manager)
            self.notebook.add(analytics_tab.get_tab(), text="📊 Аналитика")

        # Вкладка экспорта отчетов
        if self.user_manager.check_permission('export_reports'):
            from report_exporter import ReportExporter
            exporter_tab = ReportExporter(self.notebook, self.db, self.user_manager)
            self.notebook.add(exporter_tab.get_tab(), text="📄 Экспорт")

        # Вкладка истории обслуживания
        if self.user_manager.check_permission('view_orders'):
            from service_history_tab import ServiceHistoryTab
            service_history_tab = ServiceHistoryTab(self.notebook, self.db, self.user_manager)
            self.notebook.add(service_history_tab.get_tab(), text="🔧 История авто")

        # Статус бар
        self.status_bar = tk.Label(self.root, text=f"Готово | Пользователь: {self.current_user['full_name']}",
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_clients_list(self):
        """Загрузка списка клиентов"""
        try:
            clients = self.db.get_clients()
            client_list = [f"{c[1]} {c[2]} (ID:{c[0]})" for c in clients]
            self.client_combo['values'] = client_list
            if client_list:
                self.client_combo.set(client_list[0])
                # Автоматически загружаем автомобили первого клиента
                client_id = int(client_list[0].split('ID:')[1].rstrip(')'))
                self.load_client_cars(client_id)
        except Exception as e:
            print(f"Ошибка загрузки клиентов: {e}")

    def on_client_select(self, event):
        """При выборе клиента - загружаем его автомобили"""
        selection = self.client_combo.get()
        if not selection:
            return

        client_id = int(selection.split('ID:')[1].rstrip(')'))
        self.load_client_cars(client_id)

    def load_client_cars(self, client_id):
        """Загрузка автомобилей клиента"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM client_cars WHERE client_id = %s ORDER BY id DESC
            ''', (client_id,))
            cars = cursor.fetchall()
            cursor.close()

            if cars:
                car_list = [f"{c['brand']} {c['model']} ({c['license_plate']}) - ID:{c['id']}" for c in cars]
                self.car_combo['values'] = car_list
                self.car_combo.set(car_list[0])
                self.current_car_id = cars[0]['id']
                self.load_car_history(self.current_car_id)

                # Показываем информацию
                car = cars[0]
                self.info_label.config(
                    text=f"🚗 {car['brand']} {car['model']} | {car['year'] or '?'} г. | {car['license_plate']} | VIN: {car['vin'] or 'не указан'}",
                    fg='#2c3e50'
                )
            else:
                self.car_combo['values'] = []
                self.car_combo.set('')
                self.current_car_id = None
                self.info_label.config(text="У клиента нет автомобилей. Нажмите 'Добавить автомобиль'!", fg='orange')
                self.tree.delete(*self.tree.get_children())

        except Exception as e:
            print(f"Ошибка загрузки авто: {e}")

    def on_car_select(self, event):
        """При выборе автомобиля"""
        selection = self.car_combo.get()
        if selection:
            car_id = int(selection.split('ID:')[1])
            self.current_car_id = car_id
            self.load_car_history(car_id)

            # Обновляем информацию
            try:
                cursor = self.db.connection.cursor(dictionary=True)
                cursor.execute('SELECT * FROM client_cars WHERE id = %s', (car_id,))
                car = cursor.fetchone()
                cursor.close()
                if car:
                    self.info_label.config(
                        text=f"🚗 {car['brand']} {car['model']} | {car['year'] or '?'} г. | {car['license_plate']} | VIN: {car['vin'] or 'не указан'}",
                        fg='#2c3e50'
                    )
            except:
                pass

    def load_car_history(self, car_id):
        """Загрузка истории обслуживания автомобиля"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM service_history 
                WHERE car_id = %s 
                ORDER BY service_date DESC
            ''', (car_id,))
            history = cursor.fetchall()
            cursor.close()

            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Заполняем
            for record in history:
                # Форматируем дату
                service_date = record.get('service_date')
                if service_date and hasattr(service_date, 'strftime'):
                    date_str = service_date.strftime('%d.%m.%Y')
                else:
                    date_str = str(service_date) if service_date else '-'

                # Форматируем стоимость
                cost = record.get('cost', 0)
                cost_str = f"{cost:,.0f}" if cost else '-'

                self.tree.insert('', tk.END, values=(
                    record.get('id', ''),
                    date_str,
                    record.get('service_type', '-'),
                    record.get('mileage', '-'),
                    record.get('next_mileage', '-'),
                    cost_str,
                    record.get('master_name', '-')
                ))

            if not history:
                self.tree.insert('', tk.END, values=(
                '', 'Нет записей', 'Добавьте первое обслуживание кнопкой выше', '', '', '', ''))

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")



    # ... остальные методы класса ...

    def create_finance_tab(self):
        """Создание вкладки финансового учета (упрощенная версия)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💰 Финансы")

        # Заголовок
        tk.Label(tab, text="Финансовый учет", font=('Arial', 14, 'bold')).pack(pady=10)

        # Фильтры
        filter_frame = tk.Frame(tab, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(filter_frame, text="Год:").pack(side=tk.LEFT, padx=(0, 10))

        current_year = datetime.now().year
        self.finance_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(filter_frame, textvariable=self.finance_year_var,
                                  values=[str(y) for y in range(current_year - 2, current_year + 1)],
                                  state="readonly", width=10)
        year_combo.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(filter_frame, text="Месяц:").pack(side=tk.LEFT, padx=(0, 10))

        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        self.finance_month_var = tk.StringVar(value=months[datetime.now().month - 1])
        month_combo = ttk.Combobox(filter_frame, textvariable=self.finance_month_var,
                                   values=months, state="readonly", width=12)
        month_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Кнопка загрузки отчета
        load_btn = tk.Button(filter_frame, text="Загрузить отчет",
                             command=self.load_finance_report,
                             bg='#3498db', fg='white')
        load_btn.pack(side=tk.LEFT)

        # Статистика
        stats_frame = tk.Frame(tab, bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        # Карточки статистики
        self.income_label = self.create_finance_card(stats_frame, "💰 Доход", "0 руб.", "#2ecc71")
        self.income_label.pack(side=tk.LEFT, padx=5, expand=True)

        self.expense_label = self.create_finance_card(stats_frame, "💸 Расход", "0 руб.", "#e74c3c")
        self.expense_label.pack(side=tk.LEFT, padx=5, expand=True)

        self.profit_label = self.create_finance_card(stats_frame, "📈 Прибыль", "0 руб.", "#3498db")
        self.profit_label.pack(side=tk.LEFT, padx=5, expand=True)

        # Таблица доходов
        income_frame = tk.LabelFrame(tab, text="Доходы", padx=10, pady=10)
        income_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('Категория', 'Сумма', 'Операций')
        self.income_tree = ttk.Treeview(income_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.income_tree.heading(col, text=col)
            self.income_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(income_frame, orient=tk.VERTICAL, command=self.income_tree.yview)
        self.income_tree.configure(yscrollcommand=scrollbar.set)

        self.income_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Таблица расходов
        expense_frame = tk.LabelFrame(tab, text="Расходы", padx=10, pady=10)
        expense_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.expense_tree = ttk.Treeview(expense_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=150)

        scrollbar2 = ttk.Scrollbar(expense_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar2.set)

        self.expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        # Загружаем начальные данные
        self.load_finance_report()

    def create_finance_card(self, parent, title, value, color):
        """Создание карточки финансовой статистики"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)

        tk.Label(card, text=title, font=('Arial', 10, 'bold'),
                 bg='white', fg='#333').pack(pady=(10, 5))

        value_label = tk.Label(card, text=value, font=('Arial', 14, 'bold'),
                               bg='white', fg=color)
        value_label.pack(pady=(0, 10))

        # Сохраняем ссылку на метку для обновления
        card.value_label = value_label

        return card

    def load_finance_report(self):
        """Загрузка финансового отчета"""
        try:
            # Получаем выбранный год и месяц
            year = int(self.finance_year_var.get())
            month_name = self.finance_month_var.get()

            # Преобразуем название месяца в номер
            months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            month = months.index(month_name) + 1 if month_name in months else datetime.now().month

            # Получаем отчет из базы
            if self.db.server:
                report = self.db.get_financial_report_server("month", year, month)
            else:
                report = self.db.get_financial_report("month", year, month)

            if report:
                # Обновляем статистику
                self.income_label.value_label.config(
                    text=f"{report['total_income']:,.2f} руб.".replace(',', ' ')
                )
                self.expense_label.value_label.config(
                    text=f"{report['total_expense']:,.2f} руб.".replace(',', ' ')
                )
                self.profit_label.value_label.config(
                    text=f"{report['profit']:,.2f} руб.".replace(',', ' ')
                )

                # Меняем цвет прибыли
                if report['profit'] > 0:
                    self.profit_label.value_label.config(fg="#27ae60")  # зеленый
                elif report['profit'] < 0:
                    self.profit_label.value_label.config(fg="#e74c3c")  # красный
                else:
                    self.profit_label.value_label.config(fg="#7f8c8d")  # серый

                # Обновляем таблицы
                self.update_finance_tables(report)

                print(f"✅ Финансовый отчет за {month_name} {year} загружен")

        except Exception as e:
            print(f"❌ Ошибка загрузки финансового отчета: {e}")

    # В классе AutoServiceApp заменить метод update_finance_tables:

    def update_finance_tables(self, report):
        """Обновление таблиц доходов и расходов (все категории отдельно)"""
        # Очищаем таблицы
        for tree in [self.income_tree, self.expense_tree]:
            for row in tree.get_children():
                tree.delete(row)

        # Группируем данные по конкретным категориям
        income_data = {}
        expense_data = {}

        # Обрабатываем данные отчета
        for row in report['report_data']:
            if len(row) >= 3:  # Проверяем структуру данных
                trans_type = row[0]
                category = row[1] if len(row) > 1 else "Без категории"
                count = row[2] if len(row) > 2 else 0
                total = row[3] if len(row) > 3 else 0

                # Для серверной версии данные могут приходить в другом формате
                if isinstance(category, dict):  # Если данные пришли в формате словаря (сервер)
                    # Извлекаем данные из словаря
                    category_value = category.get('category', 'Без категории') if isinstance(category, dict) else str(
                        category)
                    count_value = category.get('count', 0) if isinstance(category, dict) else count
                    total_value = category.get('total_amount', 0) if isinstance(category, dict) else total
                else:
                    category_value = str(category) if category else "Без категории"
                    count_value = int(count) if count else 0
                    total_value = float(total) if total else 0

                if trans_type == 'income':
                    if category_value not in income_data:
                        income_data[category_value] = {'total': 0, 'count': 0}
                    income_data[category_value]['total'] += total_value
                    income_data[category_value]['count'] += count_value
                elif trans_type == 'expense':
                    if category_value not in expense_data:
                        expense_data[category_value] = {'total': 0, 'count': 0}
                    expense_data[category_value]['total'] += total_value
                    expense_data[category_value]['count'] += count_value
            else:
                # Если структура простая (только тип, количество, сумма)
                trans_type, count, total = row if len(row) >= 3 else (row[0], 0, 0)
                category = "Общие"  # Используем общую категорию для простых данных

                if trans_type == 'income':
                    if category not in income_data:
                        income_data[category] = {'total': 0, 'count': 0}
                    income_data[category]['total'] += float(total) if total else 0
                    income_data[category]['count'] += int(count) if count else 0
                elif trans_type == 'expense':
                    if category not in expense_data:
                        expense_data[category] = {'total': 0, 'count': 0}
                    expense_data[category]['total'] += float(total) if total else 0
                    expense_data[category]['count'] += int(count) if count else 0

        # Заполняем таблицу доходов
        for category, data in income_data.items():
            self.income_tree.insert('', tk.END, values=(
                category,
                f"{data['total']:,.2f} руб.".replace(',', ' '),
                data['count']
            ))

        # Заполняем таблицу расходов
        for category, data in expense_data.items():
            self.expense_tree.insert('', tk.END, values=(
                category,
                f"{data['total']:,.2f} руб.".replace(',', ' '),
                data['count']
            ))

        # Если таблицы пустые, добавляем заглушку
        if not income_data:
            self.income_tree.insert('', tk.END, values=(
                "Нет данных о доходах",
                "0.00 руб.",
                "0"
            ))

        if not expense_data:
            self.expense_tree.insert('', tk.END, values=(
                "Нет данных о расходах",
                "0.00 руб.",
                "0"
            ))

    # ... остальные методы класса ...

    def create_top_panel(self, parent):
        """Создание верхней панели управления"""
        top_frame = tk.Frame(parent, bg='#2c3e50', height=50)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        top_frame.pack_propagate(False)

        # Заголовок
        title_label = tk.Label(top_frame, text="🚗 АВТОСЕРВИС",
                               font=('Arial', 16, 'bold'),
                               bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT, padx=20)

        # Кнопки управления
        buttons_frame = tk.Frame(top_frame, bg='#2c3e50')
        buttons_frame.pack(side=tk.RIGHT, padx=20)

        buttons = []

        if self.user_manager.check_permission('view_clients'):
            buttons.append(("👥 Клиенты", self.show_clients_tab))

        if self.user_manager.check_permission('view_services'):
            buttons.append(("🛠️ Услуги", self.show_services_tab))

        if self.user_manager.check_permission('view_orders'):
            buttons.append(("📋 Заказы", self.show_orders_tab))

        if self.user_manager.check_permission('view_finance'):
            buttons.append(("💰 Финансы", self.show_finance_tab))

        if self.user_manager.check_permission('manage_users'):
            buttons.append(("⚙️ Админ", self.show_admin_tab))

        buttons.append(("🔄 Обновить", self.load_all_data))

        for text, command in buttons:
            btn = tk.Button(buttons_frame, text=text, command=command,
                            bg='#3498db', fg='white',
                            font=('Arial', 10), padx=15, pady=5)
            btn.pack(side=tk.LEFT, padx=5)

    def create_clients_tab(self):
        """Создание вкладки клиентов"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Клиенты")

        # Панель поиска
        search_frame = tk.Frame(tab, bg='#f0f0f0')
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(search_frame, text="Поиск:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 10))
        self.client_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.client_search_var, width=40)
        search_entry.pack(side=tk.LEFT)

        search_btn = tk.Button(search_frame, text="Найти", command=self.search_clients)
        search_btn.pack(side=tk.LEFT, padx=10)

        # Таблица клиентов
        columns = ('ID', 'Имя', 'Фамилия', 'Телефон', 'Email', 'Адрес', 'Дата регистрации')
        self.clients_tree = ttk.Treeview(tab, columns=columns, show='headings', height=20)

        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Кнопки под таблицей
        button_frame = tk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(button_frame, text="Обновить список", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Добавить клиента", command=self.add_new_client_dialog).pack(side=tk.LEFT, padx=5)

        if self.user_manager.check_permission('delete_clients'):
            tk.Button(button_frame, text="Удалить", command=self.delete_selected_client,
                      bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)

    def create_services_tab(self):
        """Создание вкладки услуг"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="🛠️ Услуги")

        # Таблица услуг
        columns = ('ID', 'Название', 'Описание', 'Цена', 'Длительность', 'Категория')
        self.services_tree = ttk.Treeview(tab, columns=columns, show='headings', height=25)

        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=120)

        # Прокрутка
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)

        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Кнопки под таблицей
        button_frame = tk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(button_frame, text="Обновить список", command=self.load_services).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Добавить услугу", command=self.add_new_service_dialog).pack(side=tk.LEFT, padx=5)

    def create_orders_tab(self):
        """Создание вкладки заказов"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Заказы")

        # Таблица заказов
        columns = ('ID', 'Клиент', 'Услуга', 'Сумма', 'Статус', 'Дата заказа', 'Примечания')
        self.orders_tree = ttk.Treeview(tab, columns=columns, show='headings', height=20)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120)

        # Прокрутка
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Кнопки под таблицей
        button_frame = tk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(button_frame, text="Обновить список", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Добавить заказ", command=self.add_new_order_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Изменить статус", command=self.change_order_status).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Добавить расходники", command=self.add_new_rashodnik).pack(side=tk.BOTTOM, padx=5)

    # ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ ====================

    def load_all_data(self):
        """Загрузка всех данных из БД"""
        self.status_bar.config(text="Загрузка данных...")
        print("\n📥 Загрузка данных из базы...")

        self.load_clients()
        self.load_services()
        self.load_orders()

        self.status_bar.config(
            text=f"Готово | Клиенты: {len(self.clients_data)} | Услуги: {len(self.services_data)} | Заказы: {len(self.orders_data)}")

    def load_clients(self):
        """Загрузка клиентов из БД с форматированием телефона"""
        try:
            from phone_formatter import PhoneFormatter

            # Очищаем таблицу
            for row in self.clients_tree.get_children():
                self.clients_tree.delete(row)

            # Получаем данные из БД
            if self.db.server:
                clients = self.db.get_clients_server()
            else:
                clients = self.db.get_clients()

            self.clients_data = clients

            print(f"📋 Загружено {len(clients)} клиентов")

            # Заполняем таблицу
            for client in clients:
                client_list = list(client)
                # Форматируем телефон для отображения (индекс 3 - это телефон)
                if len(client_list) > 3 and client_list[3]:
                    client_list[3] = PhoneFormatter.format_for_display(str(client_list[3]))
                self.clients_tree.insert('', tk.END, values=client_list)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {e}")
            print(f"❌ Ошибка загрузки клиентов: {e}")

    def load_services(self):
        """Загрузка услуг из БД"""
        try:
            # Очищаем таблицу только если она существует
            if self.services_tree is not None:
                for row in self.services_tree.get_children():
                    self.services_tree.delete(row)

            # Получаем данные из БД
            if self.db.server:
                services = self.db.get_services_server()
            else:
                services = self.db.get_services()
            self.services_data = services

            print(f"📋 Загружено {len(services)} услуг")

            # Заполняем таблицу только если она существует
            if self.services_tree is not None:
                for service in services:
                    formatted_price = f"{service[3]:.2f}" if service[3] else "0.00"
                    formatted_values = (
                        service[0],  # ID
                        service[1],  # Название
                        service[2][:50] + "..." if service[2] and len(service[2]) > 50 else service[2],
                        formatted_price,
                        service[4],
                        service[5]
                    )
                    self.services_tree.insert('', tk.END, values=formatted_values)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить услуги: {e}")
            print(f"❌ Ошибка загрузки услуг: {e}")

    def load_orders(self):
        """Загрузка заказов из БД"""
        try:
            # Очищаем таблицу
            for row in self.orders_tree.get_children():
                self.orders_tree.delete(row)

            # Получаем данные из БД
            if self.db.server:
                orders = self.db.get_orders_server()
            else:
                orders = self.db.get_orders()
            self.orders_data = orders

            print(f"📋 Получено {len(orders)} заказов из базы")

            # Отладочная печать
            if orders and len(orders) > 0:
                print(f"🔍 Пример данных заказа: {orders[0]}")
                print(f"🔍 Количество полей в заказе: {len(orders[0])}")

            # Заполняем таблицу
            for order in orders:
                try:
                    # Проверяем структуру заказа
                    if len(order) >= 7:  # Минимум 7 полей
                        order_id = order[0]
                        first_name = order[1] if len(order) > 1 else ""
                        last_name = order[2] if len(order) > 2 else ""
                        service_name = order[3] if len(order) > 3 else ""
                        status = order[4] if len(order) > 4 else ""
                        total_amount = order[5] if len(order) > 5 else 0
                        order_date = order[6] if len(order) > 6 else None

                        # Формируем строку клиента
                        client_name = f"{first_name} {last_name}".strip()
                        if not client_name:
                            client_name = "Неизвестный клиент"

                        # Форматируем дату
                        if order_date:
                            if isinstance(order_date, datetime):
                                formatted_date = order_date.strftime('%d.%m.%Y %H:%M')
                            else:
                                formatted_date = str(order_date)
                        else:
                            formatted_date = ""

                        # Форматируем сумму
                        try:
                            amount_value = float(total_amount) if total_amount else 0
                            formatted_amount = f"{amount_value:.2f} руб."
                        except:
                            formatted_amount = "0.00 руб."

                        # Вставляем в таблицу
                        self.orders_tree.insert('', tk.END, values=(
                            order_id,
                            client_name,
                            service_name,
                            formatted_amount,
                            status,
                            formatted_date,
                            ""  # Примечания - пустое поле
                        ))
                    else:
                        print(f"⚠️ Заказ с некорректной структурой: {order}")

                except Exception as e:
                    print(f"❌ Ошибка обработки заказа {order}: {e}")
                    continue

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {e}")
            print(f"❌ Ошибка загрузки заказов: {e}")

    def search_clients(self):
        """Поиск клиентов"""
        search_text = self.client_search_var.get().lower()

        if not search_text:
            self.load_clients()
            return

        # Фильтруем локальные данные
        filtered_clients = []
        for client in self.clients_data:
            # Проверяем все строковые поля
            client_text = ' '.join(str(x).lower() for x in client if x)
            if search_text in client_text:
                filtered_clients.append(client)

        # Очищаем таблицу
        for row in self.clients_tree.get_children():
            self.clients_tree.delete(row)

        # Показываем результаты
        for client in filtered_clients:
            self.clients_tree.insert('', tk.END, values=client)

    # ==================== ДИАЛОГИ ДОБАВЛЕНИЯ ====================

    def delete_selected_client(self):
        """Удаление выбранного клиента"""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите клиента для удаления")
            return

        # Получаем данные выбранного клиента
        item = selection[0]
        values = self.clients_tree.item(item, 'values')
        client_id = values[0]
        client_name = f"{values[1]} {values[2]}"

        # Подтверждение удаления
        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить клиента:\n\n"
            f"ID: {client_id}\n"
            f"Имя: {client_name}\n\n"
            f"⚠️ Внимание! Если у клиента есть заказы, удаление будет запрещено.",
            icon='warning'
        )

        if not result:
            return

        # Выполняем удаление
        success, message = self.db.delete_client(client_id)

        if success:
            messagebox.showinfo("Успех", message)
            self.load_clients()  # Обновляем таблицу
            self.status_bar.config(text=f"✅ {message}")
        else:
            messagebox.showerror("Ошибка", message)

    @require_permission('edit_clients')
    def add_new_client_dialog(self):
        """Диалог добавления нового клиента (с автоматическим форматированием телефона)"""

        from phone_formatter import PhoneFormatter

        dialog = tk.Toplevel(self.root)
        dialog.title("Новый клиент")
        dialog.geometry("450x520")
        dialog.transient(self.root)
        dialog.grab_set()

        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (520 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Заголовок
        header_frame = tk.Frame(dialog, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="➕ Добавление нового клиента",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Основной контейнер
        main_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Подсказка об обязательных полях
        hint_frame = tk.Frame(main_frame, bg='#fff3cd', relief=tk.SOLID, bd=1)
        hint_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(hint_frame, text="⚠️ Поля, отмеченные *, обязательны для заполнения",
                 font=('Arial', 9), fg='#856404', bg='#fff3cd').pack(padx=10, pady=5)

        # Создаем поля
        fields_frame = tk.Frame(main_frame, bg='#f0f0f0')
        fields_frame.pack(fill=tk.BOTH, expand=True)

        entries = {}

        # Поле Имя (обязательное)
        label_frame = tk.Frame(fields_frame, bg='#f0f0f0')
        label_frame.pack(anchor='w', pady=(0, 2))
        tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Label(label_frame, text="Имя:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(2, 0))

        entries['first_name'] = tk.Entry(fields_frame, width=35, font=('Arial', 10))
        entries['first_name'].pack(pady=(0, 10), anchor='w')

        # Поле Фамилия (обязательное)
        label_frame = tk.Frame(fields_frame, bg='#f0f0f0')
        label_frame.pack(anchor='w', pady=(0, 2))
        tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Label(label_frame, text="Фамилия:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(2, 0))

        entries['last_name'] = tk.Entry(fields_frame, width=35, font=('Arial', 10))
        entries['last_name'].pack(pady=(0, 10), anchor='w')

        # Поле Телефон (обязательное, с автоматическим форматированием)
        phone_frame = tk.Frame(fields_frame, bg='#f0f0f0')
        phone_frame.pack(anchor='w', pady=(0, 10))

        label_frame = tk.Frame(phone_frame, bg='#f0f0f0')
        label_frame.pack(anchor='w', pady=(0, 2))
        tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Label(label_frame, text="Телефон:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(2, 0))

        # Создаем поле с форматированием
        entries['phone'] = tk.Entry(phone_frame, width=35, font=('Arial', 11))
        entries['phone'].pack(anchor='w')
        entries['phone'].insert(0, "+7")
        entries['phone'].bind('<KeyRelease>', PhoneFormatter.on_key_release)

        # Подсказка для телефона
        phone_hint = tk.Label(phone_frame, text="📱 Автоматический формат: +7 999 123-45-67",
                              font=('Arial', 8), fg='gray', bg='#f0f0f0')
        phone_hint.pack(anchor='w', pady=(2, 0))

        # Поле Email (необязательное)
        tk.Label(fields_frame, text="Email:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 2))
        entries['email'] = tk.Entry(fields_frame, width=35, font=('Arial', 10))
        entries['email'].pack(pady=(0, 10), anchor='w')

        # Поле Адрес (необязательное)
        tk.Label(fields_frame, text="Адрес:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 2))
        entries['address'] = tk.Entry(fields_frame, width=35, font=('Arial', 10))
        entries['address'].pack(pady=(0, 10), anchor='w')

        def save_client():
            # Проверяем обязательные поля
            first_name = entries['first_name'].get().strip()
            last_name = entries['last_name'].get().strip()
            phone_raw = entries['phone'].get().strip()

            empty_fields = []
            if not first_name:
                empty_fields.append("Имя")
            if not last_name:
                empty_fields.append("Фамилия")
            if not phone_raw or phone_raw == "+7":
                empty_fields.append("Телефон")

            if empty_fields:
                messagebox.showwarning("Внимание", f"Заполните обязательные поля:\n• " + "\n• ".join(empty_fields))
                return

            # Очищаем телефон от форматирования
            clean_phone = PhoneFormatter.clean_phone(phone_raw)

            # Проверяем корректность телефона
            is_valid, msg = PhoneFormatter.validate_phone(phone_raw)
            if not is_valid:
                messagebox.showwarning("Внимание", f"Неверный формат телефона:\n{msg}\n\nПример: +7 999 123-45-67")
                return

            try:
                client_id = self.db.add_client(
                    first_name=first_name,
                    last_name=last_name,
                    phone=clean_phone,
                    email=entries['email'].get().strip(),
                    address=entries['address'].get().strip()
                )

                if client_id:
                    messagebox.showinfo("Успех", f"Клиент добавлен (ID: {client_id})")
                    self.load_clients()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить клиента")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=(20, 0))

        tk.Button(btn_frame, text="Сохранить", command=save_client,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                  padx=30, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', font=('Arial', 10),
                  padx=30, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=10)

    @require_permission('edit_services')
    def add_new_service_dialog(self):
        """Диалог добавления новой услуги (с обязательными полями)"""

        dialog = tk.Toplevel(self.root)
        dialog.title("Новая услуга")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()

        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Заголовок
        header_frame = tk.Frame(dialog, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🔧 Добавление новой услуги",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Основной контейнер
        main_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Подсказка об обязательных полях
        hint_frame = tk.Frame(main_frame, bg='#fff3cd', relief=tk.SOLID, bd=1)
        hint_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(hint_frame, text="⚠️ Поля, отмеченные *, обязательны для заполнения",
                 font=('Arial', 9), fg='#856404', bg='#fff3cd').pack(padx=10, pady=5)

        # Создаем поля
        fields_frame = tk.Frame(main_frame, bg='#f0f0f0')
        fields_frame.pack(fill=tk.BOTH, expand=True)

        entries = {}

        # Название (обязательное)
        label_frame = tk.Frame(fields_frame, bg='#f0f0f0')
        label_frame.pack(anchor='w', pady=(0, 2))
        tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Label(label_frame, text="Название услуги:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(2, 0))

        entries['name'] = tk.Entry(fields_frame, width=40, font=('Arial', 10))
        entries['name'].pack(pady=(0, 10), anchor='w')

        # Категория
        tk.Label(fields_frame, text="Категория:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 2))
        entries['category'] = tk.Entry(fields_frame, width=40, font=('Arial', 10))
        entries['category'].pack(pady=(0, 10), anchor='w')

        # Цена (обязательное)
        label_frame = tk.Frame(fields_frame, bg='#f0f0f0')
        label_frame.pack(anchor='w', pady=(0, 2))
        tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Label(label_frame, text="Цена (руб.):", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(2, 0))

        entries['price'] = tk.Entry(fields_frame, width=40, font=('Arial', 10))
        entries['price'].pack(pady=(0, 10), anchor='w')

        # Длительность
        tk.Label(fields_frame, text="Длительность (мин):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w',
                                                                                                  pady=(0, 2))
        entries['duration'] = tk.Entry(fields_frame, width=40, font=('Arial', 10))
        entries['duration'].pack(pady=(0, 10), anchor='w')

        # Описание
        tk.Label(fields_frame, text="Описание:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 2))
        entries['description'] = tk.Text(fields_frame, width=40, height=4, font=('Arial', 10))
        entries['description'].pack(pady=(0, 10), anchor='w')

        def save_service():
            name = entries['name'].get().strip()
            price_str = entries['price'].get().strip()

            empty_fields = []
            if not name:
                empty_fields.append("Название услуги")
            if not price_str:
                empty_fields.append("Цена")

            if empty_fields:
                messagebox.showwarning("Внимание", f"Заполните обязательные поля:\n• " + "\n• ".join(empty_fields))
                return

            try:
                price = float(price_str)
                duration = int(entries['duration'].get().strip()) if entries['duration'].get().strip() else 60
                category = entries['category'].get().strip()
                description = entries['description'].get("1.0", tk.END).strip()

                service_id = self.db.add_service(
                    name=name,
                    description=description,
                    price=price,
                    duration=duration,
                    category=category
                )

                if service_id:
                    messagebox.showinfo("Успех", f"Услуга добавлена (ID: {service_id})")
                    self.load_services()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить услугу")

            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=(20, 0))

        tk.Button(btn_frame, text="Сохранить", command=save_service,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                  padx=30, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', font=('Arial', 10),
                  padx=30, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=10)


    def add_new_order_dialog(self):
        """Диалог добавления нового заказа"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новый заказ")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Создание нового заказа", font=('Arial', 12, 'bold')).pack(pady=10)

        # Поля формы
        fields_frame = tk.Frame(dialog)
        fields_frame.pack(padx=20, pady=10)

        # Выбор клиента
        tk.Label(fields_frame, text="Клиент*:").grid(row=0, column=0, sticky=tk.W, pady=5)

        if self.db.server:
            clients = self.db.get_clients_server()
        else:
            clients = self.db.get_clients()
        client_options = [f"{c[0]}: {c[1]} {c[2]} ({c[3]})" for c in clients]

        client_var = tk.StringVar()
        client_combo = ttk.Combobox(fields_frame, textvariable=client_var,
                                    values=client_options, width=35)
        client_combo.grid(row=0, column=1, padx=10, pady=5)

        # Выбор услуги
        tk.Label(fields_frame, text="Услуга*:").grid(row=1, column=0, sticky=tk.W, pady=5)

        if self.db.server:
            services = self.db.get_services_server()
        else:
            services = self.db.get_services()
        service_options = [f"{s[0]}: {s[1]} - {s[3]} руб." for s in services]

        service_var = tk.StringVar()
        service_combo = ttk.Combobox(fields_frame, textvariable=service_var,
                                     values=service_options, width=35)
        service_combo.grid(row=1, column=1, padx=10, pady=5)

        # Сумма
        tk.Label(fields_frame, text="Сумма (руб.):").grid(row=2, column=0, sticky=tk.W, pady=5)
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(fields_frame, textvariable=amount_var, width=30)
        amount_entry.grid(row=2, column=1, padx=10, pady=5)

        # Статус
        tk.Label(fields_frame, text="Статус:").grid(row=3, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value="В работе")
        status_combo = ttk.Combobox(fields_frame, textvariable=status_var,
                                    values=["Новый", "В работе", "Завершено", "Отменено"],
                                    state="readonly", width=20)
        status_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # Примечания
        tk.Label(fields_frame, text="Примечания:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(fields_frame, width=30, height=4)
        notes_text.grid(row=4, column=1, padx=10, pady=5)

        def calculate_amount():
            """Автоматический расчет суммы при выборе услуги"""
            service_text = service_var.get()
            if service_text and "руб." in service_text:
                try:
                    # Извлекаем цену из строки "ID: Название - Цена руб."
                    price_str = service_text.split(" - ")[1].replace(" руб.", "")
                    amount_var.set(price_str)
                except:
                    pass

        # Привязываем расчет суммы к выбору услуги
        service_combo.bind("<<ComboboxSelected>>", lambda e: calculate_amount())

        def save_order():
            # Проверяем обязательные поля
            if not client_var.get() or not service_var.get() or not amount_var.get():
                messagebox.showwarning("Внимание", "Заполните все обязательные поля")
                return

            try:
                # Извлекаем ID клиента и услуги
                client_id = int(client_var.get().split(":")[0])
                service_id = int(service_var.get().split(":")[0])
                total_amount = float(amount_var.get())
                status = status_var.get()


                # Сохраняем в БД
                order_id = self.db.add_order(
                    client_id=client_id,
                    service_id=service_id,
                    total_amount=total_amount,
                    notes=notes_text.get("1.0", tk.END).strip(),
                    status=status
                )

                if order_id:
                    messagebox.showinfo("Успех", f"Заказ создан с ID: {order_id}")
                    self.load_orders()  # Обновляем таблицу

                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать заказ")

            except ValueError as e:
                messagebox.showerror("Ошибка", f"Проверьте правильность данных: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save_order,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=10)

    def add_new_rashodnik(self):
        """Диалог добавления новой услуги"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая услуга")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Добавление новой услуги", font=('Arial', 12, 'bold')).pack(pady=10)

        # Поля формы
        fields_frame = tk.Frame(dialog)
        fields_frame.pack(padx=20, pady=10)

        labels = ["Категория:", "Цена* (руб.):"]
        entries = []

        for i, label_text in enumerate(labels):
            tk.Label(fields_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(fields_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save():
            try:

                    self.db.add_financial_transaction_server(datetime.now().strftime('%Y-%m-%d'), "expense",
                                                  entries[0].get(), Decimal(str(entries[1].get())),


                dialog.destroy())

            except Exception as e:
                messagebox.showerror("Ошибка", e)

        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=10)

    @require_permission('edit_orders')
    def change_order_status(self):
        """Изменение статуса заказа"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите заказ для изменения статуса")
            return

        # Получаем ID выбранного заказа
        item = self.orders_tree.item(selection[0])
        values = item['values']

        order_id = values[0]
        current_status = values[4]
        amount = values[3]  # Сумма
        category = values[2]  # Услуга/категория

        # Диалог выбора нового статуса
        new_status = simpledialog.askstring(
            "Изменение статуса",
            f"Текущий статус: {current_status}\n\n"
            f"Выберите новый статус:\n"
            f"- В работе\n"
            f"- Завершено\n"
            f"- Отменено\n\n"
            f"Введите новый статус:",
            initialvalue=current_status
        )

        if new_status and new_status != current_status:
            # Проверка на запрет изменения завершённого заказа
            if current_status == "Завершено":
                messagebox.showerror("Предупреждение", "Нельзя изменить завершённый заказ")
                return

            try:
                print(f"🔄 Изменение статуса заказа {order_id} на '{new_status}'")

                # Обновляем статус (метод сам добавит запись в историю авто)
                result = self.db.update_order_status(order_id, new_status, amount, category)

                if result:
                    messagebox.showinfo("Успех", f"Статус заказа #{order_id} изменен на '{new_status}'")
                    # Если заказ завершен, показываем доп. информацию
                    if new_status == "Завершено":
                        messagebox.showinfo("Информация",
                                            "Заказ завершен!\n\n"
                                            "✓ Финансовая операция добавлена\n"
                                            "✓ Запись добавлена в историю автомобиля\n"
                                            "✓ Если у клиента нет автомобиля - запись не создана")
                    self.load_orders()  # Обновляем таблицу
                    self.status_bar.config(text=f"✅ Статус заказа #{order_id} изменен на '{new_status}'")
                else:
                    messagebox.showerror("Ошибка", "Не удалось изменить статус заказа")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")

    def check_and_handle_shift(self):
        """Проверка и обработка смены"""
        # Администратору не нужна смена
        if self.current_user['role'] == 'admin':
            return True

        # Проверяем, активна ли смена
        if self.shift_manager.is_shift_active():
            # Смена активна - показываем информацию
            shift_info = self.shift_manager.get_current_shift_info()
            if shift_info:
                print(f"⏰ Активная смена с {shift_info['shift_start']}")
            return True

        # Смена не активна - запрашиваем начало
        return self.show_shift_dialog()

    def show_shift_dialog(self):
        """Диалог начала смены (упрощённый)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Начало смены")
        dialog.geometry("400x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Заголовок
        header_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        role_names = {
            'admin': '👑 Администратор',
            'manager': '📋 Менеджер',
            'master': '🔧 Мастер',
            'cashier': '💰 Кассир'
        }
        role_text = role_names.get(self.current_user['role'], self.current_user['role'])

        tk.Label(header_frame, text="⏰ Начало рабочей смены",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        tk.Label(header_frame, text=f"{self.current_user['full_name']} | {role_text}",
                 font=('Arial', 10), bg='#2c3e50', fg='#bdc3c7').pack()

        # Основной контент
        content_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Информация
        info_frame = tk.Frame(content_frame, bg='#fff3cd', relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        tk.Label(info_frame, text=f"Текущее время: {current_time}",
                 font=('Arial', 11), fg='#856404', bg='#fff3cd').pack(pady=10)

        tk.Label(info_frame, text="Для начала работы необходимо начать смену",
                 font=('Arial', 9), fg='#856404', bg='#fff3cd').pack(pady=(0, 10))

        # Комментарий
        tk.Label(content_frame, text="Комментарий (необязательно):",
                 font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))

        note_text = tk.Text(content_frame, height=2, width=40, font=('Arial', 10))
        note_text.pack(pady=(0, 15))

        # Кнопки
        btn_frame = tk.Frame(content_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X)

        start_btn = tk.Button(btn_frame, text="✅ Начать смену",
                              command=lambda: self.start_shift_and_continue(dialog,
                                                                            note_text.get("1.0", tk.END).strip()),
                              bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                              padx=25, pady=8)
        start_btn.pack(side=tk.LEFT, padx=5, expand=True)

        close_btn = tk.Button(btn_frame, text="❌ Выйти",
                              command=lambda: self.exit_without_shift(dialog),
                              bg='#e74c3c', fg='white', font=('Arial', 10),
                              padx=25, pady=8)
        close_btn.pack(side=tk.RIGHT, padx=5, expand=True)

        # Ждём ответа
        self.root.wait_window(dialog)
        return getattr(self, '_shift_started', False)

    def start_shift_and_continue(self, dialog, note):
        """Начать смену и продолжить работу"""
        success, message = self.shift_manager.start_shift(note=note)

        if success:
            messagebox.showinfo("Успех", message)
            self._shift_started = True
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", message)
            self._shift_started = False
            dialog.destroy()

    def exit_without_shift(self, dialog):
        """Выход без начала смены"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из приложения?"):
            self._shift_started = False
            dialog.destroy()
            self.root.destroy()
        else:
            self._shift_started = False
            dialog.destroy()

    def end_shift_dialog(self):
        """Диалог завершения смены (упрощённый)"""
        # Проверяем активность смены
        if not self.shift_manager.is_shift_active():
            messagebox.showwarning("Внимание", "Нет активной смены")
            return

        shift_info = self.shift_manager.get_current_shift_info()
        if shift_info:
            duration = shift_info.get('current_duration', 0)
            hours = duration // 60
            minutes = duration % 60

        dialog = tk.Toplevel(self.root)
        dialog.title("Завершение смены")
        dialog.geometry("400x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Центрируем
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Заголовок
        header_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="⏹️ Завершение смены",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Основной контент
        content_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Информация о длительности
        if shift_info:
            info_frame = tk.Frame(content_frame, bg='#d4edda', relief=tk.SOLID, bd=1)
            info_frame.pack(fill=tk.X, pady=(0, 15))

            tk.Label(info_frame, text=f"Длительность смены: {hours} ч {minutes} мин",
                     font=('Arial', 11, 'bold'), fg='#155724', bg='#d4edda').pack(pady=10)

        # Комментарий
        tk.Label(content_frame, text="Комментарий (необязательно):",
                 font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))

        note_text = tk.Text(content_frame, height=2, width=40, font=('Arial', 10))
        note_text.pack(pady=(0, 15))

        # Кнопки
        btn_frame = tk.Frame(content_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X)

        def end_shift():
            note = note_text.get("1.0", tk.END).strip()
            success, message = self.shift_manager.end_shift(note=note)

            if success:
                messagebox.showinfo("Успех", message)
                dialog.destroy()
                self.create_widgets()  # Обновляем интерфейс
            else:
                messagebox.showerror("Ошибка", message)

        tk.Button(btn_frame, text="✅ Завершить смену", command=end_shift,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                  padx=25, pady=8).pack(side=tk.LEFT, padx=5, expand=True)

        tk.Button(btn_frame, text="❌ Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', font=('Arial', 10),
                  padx=25, pady=8).pack(side=tk.RIGHT, padx=5, expand=True)

    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.user_manager.logout()
            self.db.close()
            self.root.destroy()

    def create_statistics_tab(self):
        pass





# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================

if __name__ == "__main__":
    #db = Database(Config())
    #c = Config()
    #c.IP_ADDRESS = ""
    #db2 = Database(c)
    #db.add_service_server('Замена масла', 'Полная замена моторного масла и фильтра', '2000.00', '60', 'Техобслуживание')
    #print("get_services_server ",db.get_services_server())
    #db.add_order_server(1, 3, 2000)
    #print("get_orders_server ", db.get_orders_server())
    #db.add_financial_transaction_server("2026-01-06","expense","Запчасти", "43239.00", "", "ТЕСТ #21")
    #print("get_financial_report_server ", db.get_financial_report_server())
    #print("get_monthly_financial_overview_server ", db.get_monthly_financial_overview_server())
    #print("get_top_categories_server ", db.get_top_categories_server())
    #db.add_order_with_status_server(1,3,1488,)
    #print(db.delete_service_server(2))
    #print(db.delete_client_server(2))
    #print(db.delete_order_server(2))

    root = tk.Tk()

    #print(db2.get_clients())
    #print(db.get_clients_server())

    #print(db.get_orders_server())
    #print(db2.get_orders())



    # Настройка иконки (если есть)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    app = AutoServiceApp(root)
    root.mainloop()
