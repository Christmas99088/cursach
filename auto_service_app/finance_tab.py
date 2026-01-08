import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class FinanceTab:
    """Класс для вкладки финансового учета"""

    def __init__(self, parent, db):
        """
        Инициализация финансовой вкладки

        Args:
            parent: родительский виджет (notebook)
            db: экземпляр класса Database
        """
        self.parent = parent
        self.db = db

        # Создаем вкладку
        self.tab = ttk.Frame(self.parent)

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем данные
        self.load_data()

    def get_tab(self):
        """Возвращает созданную вкладку"""
        return self.tab

    def create_widgets(self):
        """Создание всех виджетов вкладки"""
        # Основной контейнер
        main_container = tk.Frame(self.tab, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. Панель фильтров
        self.create_filters_panel(main_container)

        # 2. Карточки с общей статистикой
        self.create_statistics_cards(main_container)

        # 3. Панель с детальной информацией
        self.create_details_panel(main_container)

        # 4. Кнопка обновления
        refresh_btn = tk.Button(main_container, text="🔄 Обновить",
                                command=self.load_data,
                                bg='#3498db', fg='white',
                                font=('Arial', 10),
                                padx=20, pady=5)
        refresh_btn.pack(pady=10)

    def create_filters_panel(self, parent):
        """Создание панели фильтров"""
        filter_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="Фильтры периода:",
                 font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, padx=10, pady=5)

        # Контейнер для элементов фильтрации
        filters_container = tk.Frame(filter_frame, bg='white')
        filters_container.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Выбор типа периода
        tk.Label(filters_container, text="Период:", bg='white').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.period_type = tk.StringVar(value="month")
        period_combo = ttk.Combobox(filters_container, textvariable=self.period_type,
                                    values=["День", "Неделя", "Месяц", "Квартал", "Год"],
                                    state="readonly", width=10)
        period_combo.grid(row=0, column=1, padx=(0, 20))

        # Выбор года
        tk.Label(filters_container, text="Год:", bg='white').grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 5, current_year + 1)]
        self.selected_year = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(filters_container, textvariable=self.selected_year,
                                  values=years, state="readonly", width=8)
        year_combo.grid(row=0, column=3, padx=(0, 20))

        # Выбор месяца (если период "месяц")
        self.month_label = tk.Label(filters_container, text="Месяц:", bg='white')
        self.month_label.grid(row=0, column=4, sticky=tk.W, padx=(0, 10))

        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        self.selected_month = tk.StringVar(value=months[datetime.now().month - 1])
        self.month_combo = ttk.Combobox(filters_container, textvariable=self.selected_month,
                                        values=months, state="readonly", width=10)
        self.month_combo.grid(row=0, column=5, padx=(0, 20))

        # Кнопка применения фильтров
        apply_btn = tk.Button(filters_container, text="Применить",
                              command=self.apply_filters,
                              bg='#2ecc71', fg='white')
        apply_btn.grid(row=0, column=6, padx=(0, 10))

    def create_statistics_cards(self, parent):
        """Создание карточек со статистикой"""
        cards_frame = tk.Frame(parent, bg='#f0f0f0')
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        # Карточки будут созданы здесь
        self.cards = {}

        # Доходы
        self.cards['income'] = self.create_stat_card(cards_frame, "💰 Доходы", "0 руб.", "#27ae60")
        self.cards['income'].pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Расходы
        self.cards['expense'] = self.create_stat_card(cards_frame, "💸 Расходы", "0 руб.", "#e74c3c")
        self.cards['expense'].pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Прибыль
        self.cards['profit'] = self.create_stat_card(cards_frame, "📈 Прибыль", "0 руб.", "#3498db")
        self.cards['profit'].pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Операций
        self.cards['transactions'] = self.create_stat_card(cards_frame, "📋 Операций", "0", "#9b59b6")
        self.cards['transactions'].pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def create_stat_card(self, parent, title, value, color):
        """Создание одной карточки статистики"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)

        # Заголовок
        tk.Label(card, text=title, font=('Arial', 10, 'bold'),
                 bg='white', fg='#333').pack(pady=(10, 5))

        # Значение
        value_label = tk.Label(card, text=value, font=('Arial', 14, 'bold'),
                               bg='white', fg=color)
        value_label.pack(pady=(0, 10))

        # Сохраняем ссылку на label для обновления
        card.value_label = value_label

        return card

    def create_details_panel(self, parent):
        """Создание панели с детальной информацией"""
        # Контейнер для таблиц
        details_frame = tk.Frame(parent, bg='#f0f0f0')
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть - доходы
        income_frame = tk.LabelFrame(details_frame, text="📈 Доходы по категориям",
                                     padx=10, pady=10)
        income_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Таблица доходов
        columns = ('Категория', 'Сумма', 'Доля')
        self.income_tree = ttk.Treeview(income_frame, columns=columns,
                                        show='headings', height=15)

        for col in columns:
            self.income_tree.heading(col, text=col)
            self.income_tree.column(col, width=100)

        income_scrollbar = ttk.Scrollbar(income_frame, orient=tk.VERTICAL,
                                         command=self.income_tree.yview)
        self.income_tree.configure(yscrollcommand=income_scrollbar.set)

        self.income_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        income_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Правая часть - расходы
        expense_frame = tk.LabelFrame(details_frame, text="📉 Расходы по категориям",
                                      padx=10, pady=10)
        expense_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Таблица расходов
        self.expense_tree = ttk.Treeview(expense_frame, columns=columns,
                                         show='headings', height=15)

        for col in columns:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=100)

        expense_scrollbar = ttk.Scrollbar(expense_frame, orient=tk.VERTICAL,
                                          command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=expense_scrollbar.set)

        self.expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        expense_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        """Загрузка финансовых данных"""
        try:
            # Получаем параметры фильтрации
            period_type = self.period_type.get()
            year = int(self.selected_year.get())

            # Преобразуем название месяца в номер
            month_name = self.selected_month.get()
            months = [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ]
            month = months.index(month_name) + 1 if month_name in months else datetime.now().month

            # Преобразуем русские названия периодов в английские для БД
            period_map = {
                "День": "day",
                "Неделя": "week",
                "Месяц": "month",
                "Квартал": "quarter",
                "Год": "year"
            }
            db_period = period_map.get(period_type, "month")

            # Получаем отчет из базы данных
            report = self.db.get_financial_report(db_period, year, month)

            if report:
                # Обновляем карточки статистики
                self.update_statistics_cards(report)

                # Обновляем таблицы доходов и расходов
                self.update_income_expense_tables(report)

                print(f"✅ Финансовые данные загружены: {period_type} {year}")
            else:
                messagebox.showwarning("Внимание", "Не удалось загрузить финансовые данные")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
            print(f"❌ Ошибка загрузки финансовых данных: {e}")

    def update_statistics_cards(self, report):
        """Обновление карточек статистики"""
        # Обновляем значения в карточках
        self.cards['income'].value_label.config(
            text=f"{report['total_income']:,.2f} руб.".replace(',', ' ')
        )

        self.cards['expense'].value_label.config(
            text=f"{report['total_expense']:,.2f} руб.".replace(',', ' ')
        )

        self.cards['profit'].value_label.config(
            text=f"{report['profit']:,.2f} руб.".replace(',', ' ')
        )

        self.cards['transactions'].value_label.config(
            text=str(report['total_transactions'])
        )

        # Изменяем цвет прибыли в зависимости от значения
        if report['profit'] > 0:
            self.cards['profit'].value_label.config(fg="#27ae60")  # зеленый
        elif report['profit'] < 0:
            self.cards['profit'].value_label.config(fg="#e74c3c")  # красный
        else:
            self.cards['profit'].value_label.config(fg="#7f8c8d")  # серый

    def update_income_expense_tables(self, report):
        """Обновление таблиц доходов и расходов"""
        # Очищаем таблицы
        for tree in [self.income_tree, self.expense_tree]:
            for row in tree.get_children():
                tree.delete(row)

        # Группируем данные из отчета по категориям и типам
        income_data = {}
        expense_data = {}
        total_income = report['total_income']
        total_expense = report['total_expense']

        # Обрабатываем данные отчета
        for row in report['report_data']:
            trans_type, category, count, total, avg_amount, min_amount, max_amount = row

            if trans_type == 'income':
                if category not in income_data:
                    income_data[category] = {
                        'total': 0,
                        'count': 0
                    }
                income_data[category]['total'] += total
                income_data[category]['count'] += count
            elif trans_type == 'expense':
                if category not in expense_data:
                    expense_data[category] = {
                        'total': 0,
                        'count': 0
                    }
                expense_data[category]['total'] += total
                expense_data[category]['count'] += count

        # Заполняем таблицу доходов
        for category, data in income_data.items():
            percentage = (data['total'] / total_income * 100) if total_income > 0 else 0
            self.income_tree.insert('', tk.END, values=(
                category,
                f"{data['total']:,.2f} руб.".replace(',', ' '),
                f"{percentage:.1f}%"
            ))

        # Заполняем таблицу расходов
        for category, data in expense_data.items():
            percentage = (data['total'] / total_expense * 100) if total_expense > 0 else 0
            self.expense_tree.insert('', tk.END, values=(
                category,
                f"{data['total']:,.2f} руб.".replace(',', ' '),
                f"{percentage:.1f}%"
            ))

    def apply_filters(self):
        """Применение фильтров"""
        self.load_data()