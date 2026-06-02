import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from finance_tab import FinanceTab
from permissions import require_permission


class Config:
    """Настройки приложения"""
    APP_TITLE = "🚗 Система учёта автосервиса"
    APP_SIZE = "1200x700"
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"  # Ваш пароль MySQL
    MYSQL_DATABASE = "auto_service_db"
    MYSQL_PORT = 3306


class AddClientDialog:
    """Диалоговое окно добавления клиента"""

    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить клиента")
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов диалога"""
        ttk.Label(self.dialog, text="Создание нового заказа",
                  font=("Arial", 12, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Клиент
        ttk.Label(form_frame, text="Клиент:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(form_frame, textvariable=self.client_var, width=30)
        self.client_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # Услуга
        ttk.Label(form_frame, text="Услуга:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.service_var = tk.StringVar()
        self.service_combo = ttk.Combobox(form_frame, textvariable=self.service_var, width=30)
        self.service_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.service_combo.bind('<<ComboboxSelected>>', self.on_service_selected)

        # Сумма
        ttk.Label(form_frame, text="Сумма (руб.):*").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var, width=30).grid(
            row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # ★★★★ ДОБАВЬТЕ СТАТУС ★★★★
        ttk.Label(form_frame, text="Статус:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="В работе")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
                                    values=["Новый", "В работе", "Завершено", "Отменено"],
                                    width=30, state="readonly")
        status_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        # Примечания (сдвиньте на строку ниже)
        ttk.Label(form_frame, text="Примечания:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=30, height=4)
        self.notes_text.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="Сохранить",
                   command=self.save_order).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def save_client(self):
        """Сохранение клиента"""
        try:
            first_name = self.entries['first_name'].get().strip()
            last_name = self.entries['last_name'].get().strip()
            phone = self.entries['phone'].get().strip()
            email = self.entries['email'].get().strip()
            address = self.entries['address'].get().strip()

            if not first_name or not last_name:
                messagebox.showerror("Ошибка", "Имя и фамилия обязательны")
                return

            client_id = self.app.db.add_client(first_name, last_name, phone, email, address)

            if client_id:
                messagebox.showinfo("Успех", f"Клиент добавлен! ID: {client_id}")
                self.dialog.destroy()
                self.app.show_clients_page()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить клиента")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")


class AddServiceDialog:
    """Диалоговое окно добавления услуги"""

    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить услугу")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов диалога"""
        ttk.Label(self.dialog, text="Добавление новой услуги",
                  font=("Arial", 12, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        fields = [
            ("Название:*", "name"),
            ("Описание:", "description"),
            ("Цена (руб.):*", "price"),
            ("Длительность (мин):", "duration"),
            ("Категория:", "category")
        ]

        self.entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)

            if field == "description":
                text_widget = tk.Text(form_frame, width=30, height=4)
                text_widget.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
                self.entries[field] = text_widget
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
                self.entries[field] = entry

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="Сохранить",
                   command=self.save_service).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def save_service(self):
        """Сохранение услуги"""
        try:
            name = self.entries['name'].get().strip()
            description = self.entries['description'].get("1.0", tk.END).strip()
            price_str = self.entries['price'].get().strip()
            duration_str = self.entries['duration'].get().strip()
            category = self.entries['category'].get().strip()

            if not name or not price_str:
                messagebox.showerror("Ошибка", "Название и цена обязательны")
                return

            try:
                price = float(price_str)
                duration = int(duration_str) if duration_str else 0
            except ValueError:
                messagebox.showerror("Ошибка", "Цена и длительность должны быть числами")
                return

            service_id = self.app.db.add_service(name, description, price, duration, category)

            if service_id:
                messagebox.showinfo("Успех", f"Услуга добавлена! ID: {service_id}")
                self.dialog.destroy()
                self.app.show_services_page()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить услугу")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")


class AddOrderDialog:
    """Диалоговое окно создания заказа"""

    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать заказ")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.clients = []
        self.services = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Создание виджетов диалога"""
        ttk.Label(self.dialog, text="Создание нового заказа",
                  font=("Arial", 12, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Клиент
        ttk.Label(form_frame, text="Клиент:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(form_frame, textvariable=self.client_var, width=30)
        self.client_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # Услуга
        ttk.Label(form_frame, text="Услуга:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.service_var = tk.StringVar()
        self.service_combo = ttk.Combobox(form_frame, textvariable=self.service_var, width=30)
        self.service_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.service_combo.bind('<<ComboboxSelected>>', self.on_service_selected)

        # Сумма
        ttk.Label(form_frame, text="Сумма (руб.):*").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var, width=30).grid(
            row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(form_frame, text="Статус:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="В работе")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
                                    values=["Новый", "В работе", "Завершено", "Отменено"],
                                    width=30, state="readonly")
        status_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        # Примечания
        ttk.Label(form_frame, text="Примечания:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=30, height=4)
        self.notes_text.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="Сохранить",
                   command=self.save_order).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def load_data(self):
        """Загрузка клиентов и услуг"""
        try:
            # Клиенты
            self.clients = self.app.db.get_clients()
            client_values = [f"{c[1]} {c[2]} (ID: {c[0]})" for c in self.clients]
            self.client_combo['values'] = client_values

            # Услуги
            self.services = self.app.db.get_services()
            service_values = [f"{s[1]} - {s[3]} руб." for s in self.services]
            self.service_combo['values'] = service_values

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def on_service_selected(self, event):
        """При выборе услуги устанавливаем цену"""
        try:
            service_text = self.service_var.get()
            if not service_text:
                return

            # Извлекаем цену из текста
            price = service_text.split(' - ')[1].split(' руб.')[0]
            self.amount_var.set(price)

        except Exception:
            pass

    def save_order(self):
        """Сохранение заказа"""
        try:
            client_text = self.client_var.get()
            service_text = self.service_var.get()
            amount_str = self.amount_var.get()

            # ★★★★ ПОЛУЧАЕМ СТАТУС ★★★★
            status = self.status_var.get()
            print(f"🔥 Статус из диалога: '{status}'")

            notes = self.notes_text.get("1.0", tk.END).strip()

            if not all([client_text, service_text, amount_str]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return

            # Извлекаем ID клиента
            client_id = int(client_text.split('(ID: ')[1].rstrip(')'))

            # Находим ID услуги
            service_name = service_text.split(' - ')[0]
            service_id = None
            for s in self.services:
                if s[1] == service_name:
                    service_id = s[0]
                    break

            if not service_id:
                messagebox.showerror("Ошибка", "Не удалось определить услугу")
                return

            # Сумма
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом")
                return

            # ★★★★ ИСПОЛЬЗУЙТЕ add_order_with_status ★★★★
            order_id = self.app.db.add_order_with_status(
                client_id=client_id,
                service_id=service_id,
                total_amount=amount,
                status=status,  # ← передаём статус
                notes=notes
            )

            if order_id:
                messagebox.showinfo("Успех", f"Заказ создан! ID: {order_id}\nСтатус: {status}")
                self.dialog.destroy()
                self.app.show_orders_page()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")


class AutoServiceApp:
    """Главный класс приложения"""

    def __init__(self, root):
        self.root = root
        self.config = Config()

        print("=" * 60)
        print("🚀 ЗАПУСК СИСТЕМЫ УЧЁТА АВТОСЕРВИСА")
        print("=" * 60)

        # Инициализируем базу данных
        try:
            print("\n🔌 Подключение к базе данных MySQL...")
            self.db = Database(self.config)
            print("✅ База данных подключена успешно!")
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            messagebox.showerror("Ошибка",
                                 f"Не удалось подключиться к базе данных!\n\n"
                                 f"Ошибка: {str(e)}\n\n"
                                 f"Проверьте:\n"
                                 f"1. Запущен ли MySQL сервер\n"
                                 f"2. Правильный ли пароль в config.py\n"
                                 f"3. Создана ли база данных (запустите setup_database.py)")
            return

        # Настройка главного окна
        self.root.title(self.config.APP_TITLE)
        self.root.geometry(self.config.APP_SIZE)

        # Создаём интерфейс
        self.create_gui()

        print("\n✅ ПРИЛОЖЕНИЕ ЗАПУЩЕНО УСПЕШНО!")
        print("=" * 60)

    def create_gui(self):
        """Создание графического интерфейса"""

        def create_gui(self):
            """Создание графического интерфейса"""
            # Настройка стилей
            style = ttk.Style()
            style.configure("Danger.TButton",
                            background="#e74c3c",
                            foreground="white",
                            padding=5)
            style.map("Danger.TButton",
                      background=[('active', '#c0392b')])

            # Панель навигации
            # ... остальной код ...
        # Панель навигации
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(nav_frame, text=self.config.APP_TITLE,
                  font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        # Кнопки навигации
        nav_buttons = ttk.Frame(nav_frame)
        nav_buttons.pack(side=tk.RIGHT)

        buttons = [
            ("📊 Дашборд", self.show_dashboard_page),
            ("👥 Клиенты", self.show_clients_page),
            ("🔧 Услуги", self.show_services_page),
            ("📋 Заказы", self.show_orders_page),
        ]

        for text, command in buttons:
            ttk.Button(nav_buttons, text=text,
                       command=command, width=15).pack(side=tk.LEFT, padx=2)

        # Основная область
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Показываем дашборд при запуске
        self.show_dashboard_page()

    def clear_main_frame(self):
        """Очистка основной области"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard_page(self):
        """Показать страницу дашборда"""
        self.clear_main_frame()

        # Заголовок
        ttk.Label(self.main_frame, text="📊 ДАШБОРД",
                  font=("Arial", 14, "bold")).pack(pady=20)

        # Получаем статистику
        clients_count = self.db.get_client_count()
        services_count = self.db.get_service_count()
        orders_count = self.db.get_order_count()
        total_income = self.db.get_total_income()

        # Статистика
        stats_frame = ttk.LabelFrame(self.main_frame, text="📈 ОБЩАЯ СТАТИСТИКА")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.X, padx=10, pady=10)

        stats_data = [
            ("👥 Клиентов", str(clients_count)),
            ("🔧 Услуг", str(services_count)),
            ("📋 Заказов", str(orders_count)),
            ("💰 Доход", f"{total_income} руб.")
        ]

        for i, (title, value) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_container)
            stat_frame.grid(row=0, column=i, padx=20, pady=10)

            ttk.Label(stat_frame, text=value,
                      font=("Arial", 18, "bold")).pack()
            ttk.Label(stat_frame, text=title).pack()

        # Последние заказы
        orders_frame = ttk.LabelFrame(self.main_frame, text="📋 ПОСЛЕДНИЕ ЗАКАЗЫ")
        orders_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Таблица заказов
        columns = ("ID", "Клиент", "Услуга", "Статус", "Сумма", "Дата")
        tree = ttk.Treeview(orders_frame, columns=columns, show="headings", height=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Загружаем заказы
        orders = self.db.get_orders()
        for order in orders[:15]:  # Последние 15 заказов
            tree.insert("", tk.END, values=order)

        scrollbar = ttk.Scrollbar(orders_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_clients_page(self):
        """Показать страницу клиентов"""
        self.clear_main_frame()

        # Заголовок и кнопки
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="👥 УПРАВЛЕНИЕ КЛИЕНТАМИ",
                  font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        # Кнопки справа
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)

        # ★★★★ ДОБАВЬТЕ КНОПКУ УДАЛЕНИЯ ★★★★
        ttk.Button(buttons_frame, text="🗑️ Удалить",
                   command=self.delete_selected_client,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="➕ Добавить клиента",
                   command=lambda: AddClientDialog(self.root, self)).pack(side=tk.LEFT, padx=5)

        # Остальной код без изменений...
        # ...

        # Таблица клиентов
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Имя", "Фамилия", "Телефон", "Email", "Дата регистрации")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Загружаем клиентов
        clients = self.db.get_clients()
        for client in clients:
            tree.insert("", tk.END, values=client)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_services_page(self):
        """Показать страницу услуг"""
        self.clear_main_frame()

        # Заголовок и кнопки
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="🔧 КАТАЛОГ УСЛУГ",
                  font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        # Кнопки справа
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)

        # ★★★★ ДОБАВЬТЕ КНОПКУ УДАЛЕНИЯ ★★★★
        ttk.Button(buttons_frame, text="🗑️ Удалить",
                   command=self.delete_selected_service,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="➕ Добавить услугу",
                   command=lambda: AddServiceDialog(self.root, self)).pack(side=tk.LEFT, padx=5)

        # Остальной код без изменений...
        # ...

        # Таблица услуг
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Название", "Описание", "Цена", "Длительность", "Категория")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Загружаем услуги
        services = self.db.get_services()
        for service in services:
            tree.insert("", tk.END, values=service)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_orders_page(self):
        """Показать страницу заказов"""
        self.clear_main_frame()

        # Заголовок и кнопки
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="📋 УПРАВЛЕНИЕ ЗАКАЗАМИ",
                  font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        # Кнопки справа
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)

        # ★★★★ ДОБАВЬТЕ КНОПКУ УДАЛЕНИЯ ★★★★
        ttk.Button(buttons_frame, text="🗑️ Удалить",
                   command=self.delete_selected_order,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="➕ Создать заказ",
                   command=lambda: AddOrderDialog(self.root, self)).pack(side=tk.LEFT, padx=5)

        # Таблица заказов
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Клиент", "Услуга", "Статус", "Сумма", "Дата заказа")
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                        height=20)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120)

        # Загружаем заказы
        orders = self.db.get_orders()
        for order in orders:
            try:
                order_id = order[0]
                first_name = order[1] or ""
                last_name = order[2] or ""
                service_name = order[3] or ""

                # ★★★★ ИСПРАВЬТЕ ЭТУ СТРОКУ ★★★★
                # status = order[4] or "В работе"  ← БЫЛО (НЕПРАВИЛЬНО)
                status = order[4]
                if status is None or str(status).strip() == "":
                    status = "В работе"  # ← ТОЛЬКО если действительно пусто

                    print(f"⚠️  Заказ #{order_id}: статус пустой, установлен 'В работе'")
                else:
                    print(f"✅ Заказ #{order_id}: статус из БД = '{status}'")

                total_amount = order[5] or 0
                order_date = order[6]

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
                self.orders_tree.insert("", tk.END, values=(
                    order_id,
                    client_name,
                    service_name,
                    status,  # ← Исправленный статус
                    formatted_amount,
                    formatted_date
                ))

            except Exception as e:
                print(f"❌ Ошибка обработки заказа {order}: {e}")
                continue

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_finance_tab(self):
        finance_tab = FinanceTab(self.notebook, self.db)
        tab = finance_tab.get_tab()
        self.notebook.add(tab, text="💰 Финансы")

    # ==================== МЕТОДЫ УДАЛЕНИЯ ====================

    def delete_selected_client(self):
        """Удаление выбранного клиента"""
        if not hasattr(self, 'clients_tree') or not self.clients_tree.selection():
            messagebox.showwarning("Внимание", "Выберите клиента для удаления")
            return

        item = self.clients_tree.selection()[0]
        values = self.clients_tree.item(item, 'values')
        client_id = values[0]
        client_name = f"{values[1]} {values[2]}"

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить клиента:\nID: {client_id}\nИмя: {client_name}?"
        )

        if not confirm:
            return

        success, message = self.db.delete_client(client_id)

        if success:
            self.clients_tree.delete(item)
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)


    def delete_selected_service(self):
        """Удаление выбранной услуги"""
        if not hasattr(self, 'services_tree') or not self.services_tree.selection():
            messagebox.showwarning("Внимание", "Выберите услугу для удаления")
            return

        item = self.services_tree.selection()[0]
        values = self.services_tree.item(item, 'values')
        service_id = values[0]
        service_name = values[1]

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить услугу:\nID: {service_id}\nНазвание: {service_name}?"
        )

        if not confirm:
            return

        success, message = self.db.delete_service(service_id)

        if success:
            self.services_tree.delete(item)
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)

    def delete_selected_order(self):
        """Удаление выбранного заказа"""
        if not hasattr(self, 'orders_tree') or not self.orders_tree.selection():
            messagebox.showwarning("Внимание", "Выберите заказ для удаления")
            return

        item = self.orders_tree.selection()[0]
        values = self.orders_tree.item(item, 'values')
        order_id = values[0]
        client_name = values[1]
        service_name = values[2]

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ:\nID: {order_id}\nКлиент: {client_name}\nУслуга: {service_name}\n\nЭто действие нельзя отменить!"
        )

        if not confirm:
            return

        success, message = self.db.delete_order(order_id)

        if success:
            self.orders_tree.delete(item)
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)




