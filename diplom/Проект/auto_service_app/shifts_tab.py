import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ShiftsTab:
    """Вкладка истории смен"""

    def __init__(self, parent, db, user_manager, shift_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager
        self.shift_manager = shift_manager

        self.tab = ttk.Frame(parent)
        self.create_widgets()
        self.load_shifts()

    def get_tab(self):
        return self.tab

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.tab, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📅 История смен",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Фильтры
        filter_frame = tk.Frame(self.tab, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(filter_frame, text="Период (дней):").pack(side=tk.LEFT, padx=(0, 10))
        self.days_var = tk.StringVar(value="30")
        days_combo = ttk.Combobox(filter_frame, textvariable=self.days_var,
                                  values=["7", "14", "30", "60", "90"], width=8)
        days_combo.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(filter_frame, text="Пользователь:").pack(side=tk.LEFT, padx=(0, 10))
        self.user_filter = ttk.Combobox(filter_frame, width=20)
        self.user_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.load_user_list()

        apply_btn = tk.Button(filter_frame, text="Применить", command=self.load_shifts,
                              bg='#3498db', fg='white', padx=15)
        apply_btn.pack(side=tk.LEFT)

        refresh_btn = tk.Button(filter_frame, text="🔄 Обновить", command=self.load_shifts,
                                bg='#27ae60', fg='white', padx=15)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Таблица смен
        table_frame = tk.Frame(self.tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Пользователь', 'Роль', 'Начало', 'Конец', 'Длительность', 'Статус')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        col_widths = [50, 150, 100, 150, 150, 100, 80]
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
        user_list = ["Все"] + [f"{u['full_name']} ({u['username']})" for u in users]
        self.user_filter['values'] = user_list
        self.user_filter.set("Все")

    def load_shifts(self):
        """Загрузка истории смен"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        days = int(self.days_var.get())
        user_filter = self.user_filter.get()

        # Определяем user_id для фильтра
        user_id = None
        if user_filter != "Все":
            username = user_filter.split('(')[-1].replace(')', '')
            users = self.user_manager.get_all_users()
            for u in users:
                if u['username'] == username:
                    user_id = u['id']
                    break

        shifts = self.shift_manager.get_shifts_history(user_id, days)

        for shift in shifts:
            # Форматируем длительность
            duration = shift.get('duration_minutes', 0)
            if duration:
                hours = duration // 60
                minutes = duration % 60
                duration_str = f"{hours}ч {minutes}мин"
            else:
                duration_str = "-"

            # Статус на русском
            status = "✅ Активна" if shift.get('status') == 'active' else "🔴 Завершена"

            self.tree.insert('', tk.END, values=(
                shift.get('id'),
                shift.get('full_name'),
                self.get_role_name(shift.get('role', '')),
                shift.get('shift_start').strftime('%d.%m.%Y %H:%M') if shift.get('shift_start') else '-',
                shift.get('shift_end').strftime('%d.%m.%Y %H:%M') if shift.get('shift_end') else '-',
                duration_str,
                status
            ))

        # Информация о текущей смене
        current_shift = self.shift_manager.get_current_shift_info()
        if current_shift and (user_id is None or user_id == self.user_manager.current_user.get('id')):
            info_frame = tk.Frame(self.tab, bg='#d4edda', relief=tk.SOLID, bd=1)
            info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            duration = current_shift.get('current_duration', 0)
            hours = duration // 60
            minutes = duration % 60

            tk.Label(info_frame, text="⏰ ТЕКУЩАЯ СМЕНА",
                     font=('Arial', 10, 'bold'), fg='#155724', bg='#d4edda').pack(pady=(5, 0))
            tk.Label(info_frame, text=f"Длительность: {hours} ч {minutes} мин",
                     font=('Arial', 10), fg='#155724', bg='#d4edda').pack(pady=(0, 5))

    def get_role_name(self, role):
        roles = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'master': 'Мастер',
            'cashier': 'Кассир'
        }
        return roles.get(role, role)