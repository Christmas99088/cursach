import tkinter as tk
from tkinter import ttk, messagebox
import hashlib


class LoginDialog:
    """Диалоговое окно входа в систему"""

    def __init__(self, parent, user_manager):
        self.parent = parent
        self.user_manager = user_manager
        self.result = None

        # Создаем окно входа
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Авторизация")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        # Центрируем окно
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Создаем интерфейс
        self.create_widgets()

        # Ждем закрытия окна
        self.parent.wait_window(self.dialog)

    def create_widgets(self):
        """Создание интерфейса входа"""

        # Заголовок
        title_frame = tk.Frame(self.dialog, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="🚗 АВТОСЕРВИС",
                 font=('Arial', 18, 'bold'),
                 bg='#2c3e50', fg='white').pack(expand=True)

        tk.Label(title_frame, text="Вход в систему",
                 font=('Arial', 10),
                 bg='#2c3e50', fg='#bdc3c7').pack()

        # Форма входа
        form_frame = tk.Frame(self.dialog, bg='white', padx=40, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Поле Логин
        tk.Label(form_frame, text="Логин:", font=('Arial', 10),
                 bg='white').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(form_frame, textvariable=self.username_var,
                                       font=('Arial', 11), width=25)
        self.username_entry.grid(row=1, column=0, pady=(0, 15))
        self.username_entry.focus()

        # Поле Пароль
        tk.Label(form_frame, text="Пароль:", font=('Arial', 10),
                 bg='white').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form_frame, textvariable=self.password_var,
                                       font=('Arial', 11), width=25, show="•")
        self.password_entry.grid(row=3, column=0, pady=(0, 20))

        # Привязываем Enter
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Кнопки
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=4, column=0)

        self.login_btn = tk.Button(button_frame, text="Войти",
                                   command=self.login,
                                   bg='#27ae60', fg='white',
                                   font=('Arial', 10, 'bold'),
                                   padx=30, pady=5)
        self.login_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(button_frame, text="Отмена",
                                    command=self.dialog.destroy,
                                    bg='#95a5a6', fg='white',
                                    font=('Arial', 10),
                                    padx=30, pady=5)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Информация о тестовых пользователях
        info_frame = tk.Frame(self.dialog, bg='#ecf0f1', height=60)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)

        info_text = "Тестовые пользователи:\nadmin / admin123 | manager / manager123 | master / master123 | cashier / cashier123"
        tk.Label(info_frame, text=info_text, font=('Arial', 8),
                 bg='#ecf0f1', fg='#7f8c8d', justify=tk.CENTER).pack(expand=True)

    def login(self):
        """Обработка входа"""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль")
            return

        # Аутентификация
        user = self.user_manager.authenticate(username, password)

        if user:
            self.result = user
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            self.password_var.set("")
            self.password_entry.focus()