import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class LogsTab:
    """Вкладка для просмотра логов системы"""

    def __init__(self, parent, db, user_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager

        # Пытаемся получить audit_logger
        if hasattr(db, 'audit_logger'):
            self.audit_logger = db.audit_logger
        else:
            self.audit_logger = None

        self.tab = ttk.Frame(parent)
        self.create_widgets()

        if self.audit_logger:
            self.load_logs()
        else:
            self.show_no_logger_message()

    def get_tab(self):
        return self.tab

    def show_no_logger_message(self):
        """Показать сообщение об отсутствии логгера"""
        frame = tk.Frame(self.tab, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📋 Система логирования",
                 font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=20)

        tk.Label(frame, text="Функция логирования временно отключена",
                 font=('Arial', 12), fg='gray', bg='#f0f0f0').pack(pady=10)

        tk.Label(frame, text="Для включения логов добавьте AuditLogger в database.py",
                 font=('Arial', 10), fg='gray', bg='#f0f0f0').pack()

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.tab, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📋 Журнал действий системы",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Панель фильтров
        filter_frame = tk.Frame(self.tab, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(filter_frame, text="Фильтр по действию:").pack(side=tk.LEFT, padx=(0, 10))
        self.action_filter = ttk.Combobox(filter_frame, width=25)
        self.action_filter['values'] = [
            "Все",
            "LOGIN_SUCCESS",
            "LOGIN_FAILED",
            "LOGOUT",
            "SHIFT_START",
            "SHIFT_END",
            "CREATE",
            "UPDATE",
            "DELETE",
            "STATUS_CHANGE",
            "FINANCIAL"
        ]
        self.action_filter.set("Все")
        self.action_filter.pack(side=tk.LEFT, padx=(0, 20))
        self.action_filter.bind('<<ComboboxSelected>>', lambda e: self.load_logs())

        tk.Label(filter_frame, text="Пользователь:").pack(side=tk.LEFT, padx=(0, 10))
        self.user_filter = ttk.Combobox(filter_frame, width=20)
        self.user_filter.pack(side=tk.LEFT, padx=(0, 20))
        self.user_filter.bind('<<ComboboxSelected>>', lambda e: self.load_logs())
        self.load_user_list()

        refresh_btn = tk.Button(filter_frame, text="🔄 Обновить", command=self.load_logs,
                                bg='#3498db', fg='white', padx=15)
        refresh_btn.pack(side=tk.LEFT)

        # Таблица логов
        table_frame = tk.Frame(self.tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Дата', 'Пользователь', 'Роль', 'Действие', 'Детали')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        col_widths = [50, 150, 150, 100, 180, 400]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_user_list(self):
        """Загрузка списка пользователей для фильтра"""
        users = self.user_manager.get_all_users()
        user_list = ["Все"] + [f"{u['username']} ({u['full_name']})" for u in users]
        self.user_filter['values'] = user_list
        self.user_filter.set("Все")

    def get_action_name(self, action_type):
        """Преобразование типа действия в русское название"""
        action_names = {
            'LOGIN_SUCCESS': '✅ Вход в систему',
            'LOGIN_FAILED': '❌ Ошибка входа',
            'LOGOUT': '🚪 Выход из системы',
            'SHIFT_START': '🟢 Начало смены',
            'SHIFT_END': '🔴 Окончание смены',
            'CREATE': '➕ Создание',
            'UPDATE': '✏️ Редактирование',
            'DELETE': '🗑️ Удаление',
            'STATUS_CHANGE': '🔄 Смена статуса',
            'FINANCIAL': '💰 Финансовая операция'
        }
        return action_names.get(action_type, action_type)

    def get_role_name(self, role):
        """Преобразование роли в русское название"""
        role_names = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'master': 'Мастер',
            'cashier': 'Кассир'
        }
        return role_names.get(role, role)

    def load_logs(self):
        """Загрузка логов с фильтрацией"""
        if not self.audit_logger:
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получаем фильтры
        action_filter = self.action_filter.get()
        user_filter = self.user_filter.get()

        # Определяем user_id для фильтра
        user_id = None
        if user_filter != "Все":
            username = user_filter.split(' (')[0]
            users = self.user_manager.get_all_users()
            for u in users:
                if u['username'] == username:
                    user_id = u['id']
                    break

        # Получаем логи
        action = None if action_filter == "Все" else action_filter
        logs = self.audit_logger.get_logs(limit=500, user_id=user_id, action_type=action)

        for log in logs:
            created_at = log.get('created_at')
            if created_at and hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%d.%m.%Y %H:%M:%S')

            # Получаем русские названия
            action_name = self.get_action_name(log.get('action_type', ''))
            role_name = self.get_role_name(log.get('user_role', ''))

            self.tree.insert('', tk.END, values=(
                log.get('id'),
                created_at,
                log.get('username', 'system'),
                role_name,
                action_name,
                (log.get('details', '') or '')[:150]
            ))