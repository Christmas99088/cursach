import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar


class DatePicker:
    """Виджет для выбора даты с календарём"""

    def __init__(self, parent, initial_date=None, **kwargs):
        self.parent = parent
        self.current_date = initial_date or datetime.now()

        # Создаём фрейм
        self.frame = tk.Frame(parent, **kwargs)

        # Поле для ввода даты
        self.date_var = tk.StringVar()
        self.date_var.set(self.current_date.strftime('%Y-%m-%d'))

        self.entry = tk.Entry(self.frame, textvariable=self.date_var, width=12, font=('Arial', 10))
        self.entry.pack(side=tk.LEFT, padx=(0, 5))

        # Кнопка открытия календаря
        self.calendar_btn = tk.Button(self.frame, text="📅", command=self.show_calendar,
                                      width=3, height=1, font=('Arial', 9))
        self.calendar_btn.pack(side=tk.LEFT)

        self.calendar_window = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get(self):
        return self.date_var.get()

    def set(self, date):
        if isinstance(date, datetime):
            self.current_date = date
            self.date_var.set(date.strftime('%Y-%m-%d'))
        else:
            self.date_var.set(date)

    def show_calendar(self):
        """Показать окно календаря"""
        if self.calendar_window and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            return

        self.calendar_window = tk.Toplevel(self.parent)
        self.calendar_window.title("Выберите дату")
        self.calendar_window.geometry("300x280")
        self.calendar_window.transient(self.parent)
        self.calendar_window.grab_set()

        # Центрируем окно
        self.calendar_window.update_idletasks()
        x = (self.calendar_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.calendar_window.winfo_screenheight() // 2) - (280 // 2)
        self.calendar_window.geometry(f"+{x}+{y}")

        # Выбранный месяц и год
        self.calendar_year = self.current_date.year
        self.calendar_month = self.current_date.month
        self.calendar_day = self.current_date.day

        self.create_calendar_widgets()

    def create_calendar_widgets(self):
        """Создание виджетов календаря"""
        # Очищаем окно
        for widget in self.calendar_window.winfo_children():
            widget.destroy()

        # Верхняя панель с навигацией
        nav_frame = tk.Frame(self.calendar_window)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопка предыдущий месяц
        prev_btn = tk.Button(nav_frame, text="◀", command=self.prev_month,
                             width=3, font=('Arial', 10))
        prev_btn.pack(side=tk.LEFT)

        # Название месяца и года
        month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        self.month_label = tk.Label(nav_frame, text=f"{month_names[self.calendar_month - 1]} {self.calendar_year}",
                                    font=('Arial', 12, 'bold'), width=15)
        self.month_label.pack(side=tk.LEFT, expand=True)

        # Кнопка следующий месяц
        next_btn = tk.Button(nav_frame, text="▶", command=self.next_month,
                             width=3, font=('Arial', 10))
        next_btn.pack(side=tk.RIGHT)

        # Дни недели
        days_frame = tk.Frame(self.calendar_window)
        days_frame.pack(pady=5)

        week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for i, day in enumerate(week_days):
            lbl = tk.Label(days_frame, text=day, width=4, height=1,
                           font=('Arial', 9, 'bold'), bg='#3498db', fg='white')
            lbl.grid(row=0, column=i, padx=1, pady=1)

        # Календарь
        self.calendar_frame = tk.Frame(self.calendar_window)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.update_calendar_days()

        # Кнопки внизу
        btn_frame = tk.Frame(self.calendar_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Сегодня", command=self.select_today,
                  bg='#27ae60', fg='white', padx=15).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Отмена", command=self.calendar_window.destroy,
                  bg='#95a5a6', fg='white', padx=15).pack(side=tk.RIGHT, padx=5)

    def update_calendar_days(self):
        """Обновление отображения дней в календаре"""
        # Очищаем старые кнопки
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Получаем календарь на месяц
        cal = calendar.monthcalendar(self.calendar_year, self.calendar_month)

        # Текущая дата для подсветки
        today = datetime.now().date()

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    btn = tk.Button(self.calendar_frame, text="", width=4, height=2,
                                    state='disabled', bg='#ecf0f1')
                else:
                    # Определяем цвет фона
                    bg_color = '#ffffff'
                    fg_color = '#000000'

                    # Если это выбранный день
                    if day == self.calendar_day:
                        bg_color = '#3498db'
                        fg_color = '#ffffff'
                    # Если это сегодня
                    elif day == today.day and self.calendar_year == today.year and self.calendar_month == today.month:
                        bg_color = '#f39c12'
                        fg_color = '#ffffff'
                    # Если это выходной
                    elif day_num in (5, 6):
                        bg_color = '#fdebd0'
                        fg_color = '#e74c3c'

                    btn = tk.Button(self.calendar_frame, text=str(day), width=4, height=2,
                                    bg=bg_color, fg=fg_color,
                                    command=lambda d=day: self.select_date(d))

                btn.grid(row=week_num, column=day_num, padx=1, pady=1)

    def select_date(self, day):
        """Выбор даты"""
        self.calendar_day = day
        selected_date = datetime(self.calendar_year, self.calendar_month, day)
        self.current_date = selected_date
        self.date_var.set(selected_date.strftime('%Y-%m-%d'))
        self.calendar_window.destroy()

    def select_today(self):
        """Выбор сегодняшней даты"""
        today = datetime.now()
        self.current_date = today
        self.date_var.set(today.strftime('%Y-%m-%d'))
        self.calendar_window.destroy()

    def prev_month(self):
        """Предыдущий месяц"""
        if self.calendar_month == 1:
            self.calendar_month = 12
            self.calendar_year -= 1
        else:
            self.calendar_month -= 1

        # Корректируем день
        last_day = calendar.monthrange(self.calendar_year, self.calendar_month)[1]
        if self.calendar_day > last_day:
            self.calendar_day = last_day

        self.update_calendar_display()

    def next_month(self):
        """Следующий месяц"""
        if self.calendar_month == 12:
            self.calendar_month = 1
            self.calendar_year += 1
        else:
            self.calendar_month += 1

        # Корректируем день
        last_day = calendar.monthrange(self.calendar_year, self.calendar_month)[1]
        if self.calendar_day > last_day:
            self.calendar_day = last_day

        self.update_calendar_display()

    def update_calendar_display(self):
        """Обновление отображения календаря"""
        month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        self.month_label.config(text=f"{month_names[self.calendar_month - 1]} {self.calendar_year}")
        self.update_calendar_days()