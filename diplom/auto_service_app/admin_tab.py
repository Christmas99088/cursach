import tkinter as tk
from tkinter import ttk, messagebox


class AdminTab:
    """Вкладка администрирования для управления пользователями"""

    def __init__(self, parent, db, user_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager

        self.tab = ttk.Frame(parent)
        self.create_widgets()
        self.load_users()

    def get_tab(self):
        return self.tab

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.tab, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="⚙️ Управление пользователями",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Кнопки
        button_frame = tk.Frame(self.tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="➕ Добавить пользователя",
                  command=self.add_user_dialog,
                  bg='#27ae60', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="✏️ Редактировать",
                  command=self.edit_user_dialog,
                  bg='#3498db', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="🔑 Сменить пароль",
                  command=self.change_password_dialog,
                  bg='#f39c12', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="🗑️ Удалить",
                  command=self.delete_user,
                  bg='#e74c3c', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        # Таблица пользователей
        table_frame = tk.Frame(self.tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Логин', 'ФИО', 'Роль', 'Email', 'Телефон', 'Активен', 'Последний вход')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        col_widths = [50, 100, 150, 100, 150, 100, 70, 130]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



    def load_users(self):
        """Загрузка списка пользователей"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = self.user_manager.get_all_users()

        for user in users:
            last_login = ""
            if user.get('last_login'):
                if hasattr(user['last_login'], 'strftime'):
                    last_login = user['last_login'].strftime('%d.%m.%Y %H:%M')
                else:
                    last_login = str(user['last_login'])

            self.tree.insert('', tk.END, values=(
                user.get('id', ''),
                user.get('username', ''),
                user.get('full_name', ''),
                self.get_role_name(user.get('role', '')),
                user.get('email', '') or '',
                user.get('phone', '') or '',
                'Да' if user.get('is_active') else 'Нет',
                last_login or 'Никогда'
            ))

    def get_role_name(self, role):
        roles = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'master': 'Мастер',
            'cashier': 'Кассир'
        }
        return roles.get(role, role)

    def add_user_dialog(self):
        """Диалог добавления пользователя"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить пользователя")
        dialog.geometry("400x480")
        dialog.transient(self.tab)
        dialog.grab_set()

        tk.Label(dialog, text="Новый пользователь",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        frame = tk.Frame(dialog)
        frame.pack(padx=20, pady=10)

        fields = [
            ('Логин:*', 'username'),
            ('Пароль:*', 'password'),
            ('ФИО:*', 'full_name'),
            ('Роль:*', 'role'),
            ('Email:', 'email'),
            ('Телефон:', 'phone')
        ]

        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)

            if key == 'role':
                entry = ttk.Combobox(frame, values=['admin', 'manager', 'master', 'cashier'], width=27)
                entry.set('manager')
            else:
                entry = tk.Entry(frame, width=30)

            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[key] = entry

        def save():
            username = entries['username'].get().strip()
            password = entries['password'].get()
            full_name = entries['full_name'].get().strip()
            role = entries['role'].get()
            email = entries['email'].get().strip()
            phone = entries['phone'].get().strip()

            if not all([username, password, full_name, role]):
                messagebox.showwarning("Внимание", "Заполните все обязательные поля")
                return

            user_id = self.user_manager.add_user(username, password, role, full_name, email, phone)

            if user_id:
                messagebox.showinfo("Успех", f"Пользователь {username} создан")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save,
                  bg='#27ae60', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    def edit_user_dialog(self):
        """Диалог редактирования пользователя"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        values = self.tree.item(selection[0])['values']
        user_id = values[0]

        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать пользователя")
        dialog.geometry("400x400")
        dialog.transient(self.tab)
        dialog.grab_set()

        tk.Label(dialog, text=f"Редактирование: {values[1]}",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        frame = tk.Frame(dialog)
        frame.pack(padx=20, pady=10)

        fields = [
            ('ФИО:', 'full_name', values[2]),
            ('Роль:', 'role', values[3]),
            ('Email:', 'email', values[4]),
            ('Телефон:', 'phone', values[5]),
            ('Активен:', 'is_active', values[6])
        ]

        entries = {}

        for i, (label, key, default) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)

            if key == 'role':
                entry = ttk.Combobox(frame, values=['admin', 'manager', 'master', 'cashier'], width=27)
                entry.set(default)
            elif key == 'is_active':
                entry = ttk.Combobox(frame, values=['Да', 'Нет'], width=27)
                entry.set(default)
            else:
                entry = tk.Entry(frame, width=30)
                entry.insert(0, default)

            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[key] = entry

        def save():
            data = {
                'full_name': entries['full_name'].get().strip(),
                'role': entries['role'].get(),
                'email': entries['email'].get().strip(),
                'phone': entries['phone'].get().strip(),
                'is_active': entries['is_active'].get() == 'Да'
            }

            if self.user_manager.update_user(user_id, **data):
                messagebox.showinfo("Успех", "Данные обновлены")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить данные")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save,
                  bg='#27ae60', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    def change_password_dialog(self):
        """Диалог смены пароля"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        values = self.tree.item(selection[0])['values']
        user_id = values[0]
        username = values[1]

        dialog = tk.Toplevel(self.tab)
        dialog.title("Смена пароля")
        dialog.geometry("350x200")
        dialog.transient(self.tab)
        dialog.grab_set()

        tk.Label(dialog, text=f"Смена пароля для: {username}",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        frame = tk.Frame(dialog)
        frame.pack(padx=20, pady=10)

        tk.Label(frame, text="Новый пароль:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        password_entry = tk.Entry(frame, width=25, show="•")
        password_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame, text="Подтверждение:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        confirm_entry = tk.Entry(frame, width=25, show="•")
        confirm_entry.grid(row=1, column=1, padx=10, pady=5)

        def save():
            password = password_entry.get()
            confirm = confirm_entry.get()

            if not password:
                messagebox.showwarning("Внимание", "Введите пароль")
                return

            if password != confirm:
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return

            if self.user_manager.change_password(user_id, password):
                messagebox.showinfo("Успех", "Пароль изменен")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось изменить пароль")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Сохранить", command=save,
                  bg='#27ae60', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg='#95a5a6', fg='white', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    def delete_user(self):
        """Удаление пользователя (деактивация)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        values = self.tree.item(selection[0])['values']
        user_id = values[0]
        username = values[1]

        # Нельзя удалить самого себя
        if hasattr(self.user_manager, 'current_user') and self.user_manager.current_user:
            if user_id == self.user_manager.current_user.get('id'):
                messagebox.showerror("Ошибка", "Нельзя удалить самого себя")
                return

        confirm = messagebox.askyesno("Подтверждение",
                                      f"Вы уверены, что хотите удалить пользователя {username}?")

        if confirm:
            if self.user_manager.delete_user(user_id):
                messagebox.showinfo("Успех", "Пользователь удален")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")