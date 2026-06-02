import tkinter as tk
from tkinter import ttk


class RequiredField:
    """Класс для работы с обязательными полями"""

    @staticmethod
    def add_required_marker(parent, text, row, column, **kwargs):
        """Добавление метки с маркером обязательного поля"""

        frame = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0')
        frame.grid(row=row, column=column, sticky='w', padx=5, pady=2)

        # Звездочка обязательности
        star = tk.Label(frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                        bg=frame.cget('bg'))
        star.pack(side=tk.LEFT)

        # Текст метки
        label = tk.Label(frame, text=f"{text}:", font=('Arial', 10),
                         bg=frame.cget('bg'))
        label.pack(side=tk.LEFT, padx=(2, 0))

        return frame

    @staticmethod
    def add_required_hint(parent, row, column):
        """Добавление подсказки об обязательных полях"""

        hint_frame = tk.Frame(parent, bg='#fff3cd', relief=tk.SOLID, bd=1)
        hint_frame.grid(row=row, column=column, columnspan=2, sticky='ew', pady=(5, 0))

        hint_label = tk.Label(hint_frame, text="⚠️ Поля, отмеченные *, обязательны для заполнения",
                              font=('Arial', 9), fg='#856404', bg='#fff3cd')
        hint_label.pack(padx=10, pady=5)

        return hint_frame

    @staticmethod
    def create_required_entry(parent, label, row, column, required=True, **kwargs):
        """Создание поля ввода с меткой и маркером обязательности"""

        # Контейнер для метки
        label_frame = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0')
        label_frame.grid(row=row, column=column, sticky='w', padx=5, pady=(5, 0))

        if required:
            star = tk.Label(label_frame, text="*", fg='red', font=('Arial', 12, 'bold'),
                            bg=label_frame.cget('bg'))
            star.pack(side=tk.LEFT)

        lbl = tk.Label(label_frame, text=f"{label}:", font=('Arial', 10),
                       bg=label_frame.cget('bg'))
        lbl.pack(side=tk.LEFT, padx=(2, 0))

        # Поле ввода
        entry = tk.Entry(parent, width=35, font=('Arial', 10))
        entry.grid(row=row, column=column + 1, padx=10, pady=(5, 0), sticky='ew')

        return entry

    @staticmethod
    def validate_required_fields(parent, fields_data):
        """Проверка обязательных полей

        Args:
            parent: родительское окно для показа сообщения
            fields_data: список кортежей (поле, значение, название)

        Returns:
            bool: True если все поля заполнены
        """
        empty_fields = []

        for field, value, name in fields_data:
            if not value or not str(value).strip():
                empty_fields.append(name)

        if empty_fields:
            message = f"Заполните обязательные поля:\n• " + "\n• ".join(empty_fields)
            from tkinter import messagebox
            messagebox.showwarning("Внимание", message)
            return False

        return True