import tkinter as tk
from decimal import Decimal
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import datetime

# Импортируем исправленный database.py
from database import Database


# Конфигурация базы данных
class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'кщще'  # Ваш пароль MySQL
    MYSQL_DATABASE = 'auto_service_db'
    MYSQL_PORT = 3306

    IP_ADDRESS = "http://127.0.0.1"
    PORT = 8002


class AutoServiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта автосервиса")
        self.root.geometry("1200x700")

        # Подключение к БД
        print("🚀 Запуск приложения...")
        self.db = Database(Config())

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем данные из БД
        self.load_all_data()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя панель с кнопками
        self.create_top_panel(main_container)

        # Панель вкладок
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Создаем вкладки
        self.create_clients_tab()
        self.create_services_tab()
        self.create_orders_tab()
        self.create_finance_tab()  # ← Добавляем финансовую вкладку

        # Статус бар
        self.status_bar = tk.Label(self.root, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)



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
                               bg='#2c3e50',
                               fg='white')
        title_label.pack(side=tk.LEFT, padx=20)

        # Кнопки управления
        buttons_frame = tk.Frame(top_frame, bg='#2c3e50')
        buttons_frame.pack(side=tk.RIGHT, padx=20)

        # Кнопки с командами
        buttons = [
            ("🔄 Обновить", self.load_all_data),
            ("➕ Клиент", self.add_new_client_dialog),
            ("➕ Услуга", self.add_new_service_dialog),
            ("➕ Заказ", self.add_new_order_dialog),
        ]

        for text, command in buttons:
            btn = tk.Button(buttons_frame, text=text, command=command,
                            bg='#3498db',
                            fg='white',
                            font=('Arial', 10),
                            padx=15,
                            pady=5)
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

        # Прокрутка
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Кнопки под таблицей
        button_frame = tk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(button_frame, text="Обновить список", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Добавить клиента", command=self.add_new_client_dialog).pack(side=tk.LEFT, padx=5)

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
        """Загрузка клиентов из БД"""
        try:
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
                self.clients_tree.insert('', tk.END, values=client)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {e}")
            print(f"❌ Ошибка загрузки клиентов: {e}")

    def load_services(self):
        """Загрузка услуг из БД"""
        try:
            # Очищаем таблицу
            for row in self.services_tree.get_children():
                self.services_tree.delete(row)

            # Получаем данные из БД
            if self.db.server:
                services = self.db.get_services_server()
            else:
                services = self.db.get_services()
            self.services_data = services

            print(f"📋 Загружено {len(services)} услуг")

            # Заполняем таблицу
            for service in services:
                # Форматируем цену
                formatted_price = f"{service[3]:.2f}" if service[3] else "0.00"
                formatted_values = (
                    service[0],  # ID
                    service[1],  # Название
                    service[2][:50] + "..." if service[2] and len(service[2]) > 50 else service[2],  # Описание
                    formatted_price,  # Цена
                    service[4],  # Длительность
                    service[5]  # Категория
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

    def add_new_client_dialog(self):
        """Диалог добавления нового клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новый клиент")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Добавление нового клиента", font=('Arial', 12, 'bold')).pack(pady=10)

        # Поля формы
        fields_frame = tk.Frame(dialog)
        fields_frame.pack(padx=20, pady=10)

        labels = ["Имя*:", "Фамилия*:", "Телефон:", "Email:", "Адрес:"]
        entries = []

        for i, label_text in enumerate(labels):
            tk.Label(fields_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(fields_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save_client():
            # Проверяем обязательные поля
            if not entries[0].get() or not entries[1].get():
                messagebox.showwarning("Внимание", "Заполните Имя и Фамилию")
                return

            try:
                # Сохраняем в БД
                client_id = self.db.add_client(
                    first_name=entries[0].get(),
                    last_name=entries[1].get(),
                    phone=entries[2].get(),
                    email=entries[3].get(),
                    address=entries[4].get()
                )

                if client_id:
                    messagebox.showinfo("Успех", f"Клиент добавлен с ID: {client_id}")
                    self.load_clients()  # Обновляем таблицу
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить клиента")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save_client,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=10)

    def add_new_service_dialog(self):
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

        labels = ["Название*:", "Категория:", "Цена* (руб.):", "Длительность (мин):", "Описание:"]
        entries = []

        for i, label_text in enumerate(labels[:4]):
            tk.Label(fields_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(fields_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        # Описание (многострочное)
        tk.Label(fields_frame, text=labels[4]).grid(row=4, column=0, sticky=tk.NW, pady=5)
        desc_text = tk.Text(fields_frame, width=30, height=4)
        desc_text.grid(row=4, column=1, padx=10, pady=5)
        entries.append(desc_text)

        def save_service():
            # Проверяем обязательные поля
            if not entries[0].get() or not entries[2].get():
                messagebox.showwarning("Внимание", "Заполните Название и Цену")
                return

            try:
                price = float(entries[2].get())
                duration = int(entries[3].get()) if entries[3].get() else 60

                # Сохраняем в БД
                if self.db.server:
                    service_id = self.db.add_service_server(
                        name=entries[0].get(),
                        description=entries[4].get("1.0", tk.END).strip(),
                        price=price,
                        duration=duration,
                        category=entries[1].get()
                    )
                else:
                    service_id = self.db.add_service(
                        name=entries[0].get(),
                        description=entries[4].get("1.0", tk.END).strip(),
                        price=price,
                        duration=duration,
                        category=entries[1].get()
                    )

                if service_id:
                    messagebox.showinfo("Успех", f"Услуга добавлена с ID: {service_id}")
                    self.load_services()  # Обновляем таблицу
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить услугу")

            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save_service,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=10)

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
                if self.db.server:
                    order_id = self.db.add_order_server(
                        client_id=client_id,
                        service_id=service_id,
                        total_amount=total_amount,
                        notes=notes_text.get("1.0", tk.END).strip(),
                        status=status
                    )
                else:
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
                if self.db.server:
                    self.db.add_financial_transaction_server(datetime.now().strftime('%Y-%m-%d'), "expense",
                                                  entries[0].get(), Decimal(str(entries[1].get())))
                else:
                    self.db.add_financial_transaction(datetime.now().strftime('%Y-%m-%d'), "expense",
                                                             entries[0].get(), Decimal(str(entries[1].get())))
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", e)

        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=10)



    def change_order_status(self):
        """Изменение статуса заказа"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите заказ для изменения статуса")
            return

        # Получаем ID выбранного заказа
        item = self.orders_tree.item(selection[0])
        amount = item['values'][3]
        category = item['values'][2]

        order_id = item['values'][0]
        current_status = item['values'][4]

        # Диалог выбора нового статуса
        new_status = simpledialog.askstring(
            "Изменение статуса",
            f"Текущий статус: {current_status}\nВведите новый статус:",
            initialvalue=current_status
        )


        if new_status and new_status != current_status:
            try:
                # Обновляем статус в БД
                if current_status == "Завершено":
                    messagebox.showerror("Предупреждение", f"Нельзя изменить завершённый заказ")
                    return
                print(f"🔄 Изменение статуса заказа {order_id} на '{new_status}'")

                if self.db.server:
                    self.db.update_order_status_server(order_id, new_status, amount, category)
                else:
                    self.db.update_order_status(order_id, new_status, amount, category)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")

    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
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
