import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Настройка стилей matplotlib для лучшей читаемости
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10


class FinancialAnalytics:
    """Класс для расширенной финансовой аналитики с адаптивным интерфейсом"""

    def __init__(self, parent, db, user_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager

        # Создаем вкладку с прокруткой
        self.tab = ttk.Frame(parent)
        self.create_scrollable_interface()
        self.load_analytics()

    def get_tab(self):
        return self.tab

    def create_scrollable_interface(self):
        """Создание интерфейса с прокруткой для больших данных"""

        # Создаем канвас для прокрутки
        self.canvas = tk.Canvas(self.tab, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Привязываем изменение размера
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Упаковываем
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем колесико мыши
        self._bind_mousewheel()

        # Основной контейнер
        self.main_container = self.scrollable_frame

        # Заголовок
        self.create_header()

        # Панель фильтров
        self.create_filters_panel()

        # Панель KPI (будет обновляться динамически)
        self.kpi_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.kpi_frame.pack(fill=tk.X, pady=(0, 10))

        # Контейнер для графиков (сетка)
        self.charts_grid = tk.Frame(self.main_container, bg='#f0f0f0')
        self.charts_grid.pack(fill=tk.BOTH, expand=True)

    def _on_canvas_configure(self, event):
        """Обновление ширины при изменении размера окна"""
        self.canvas.itemconfig(1, width=event.width)

    def _bind_mousewheel(self):
        """Привязка колесика мыши для прокрутки"""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def create_header(self):
        """Создание заголовка"""
        header_frame = tk.Frame(self.main_container, bg='#2c3e50', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Заголовок
        title = tk.Label(header_frame, text="📊 РАСШИРЕННАЯ ФИНАНСОВАЯ АНАЛИТИКА",
                         font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title.pack(expand=True)

        # Подзаголовок
        subtitle = tk.Label(header_frame, text="Анализ ключевых показателей, прогнозирование и визуализация данных",
                            font=('Arial', 10), bg='#2c3e50', fg='#bdc3c7')
        subtitle.pack()

    def create_filters_panel(self):
        """Создание панели фильтров"""
        filter_frame = tk.LabelFrame(self.main_container, text="Параметры анализа",
                                     font=('Arial', 11, 'bold'),
                                     padx=15, pady=10, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Внутренний контейнер для адаптивного расположения
        inner_frame = tk.Frame(filter_frame, bg='white')
        inner_frame.pack(fill=tk.X)

        # Ряд 1: Период и год
        row1 = tk.Frame(inner_frame, bg='white')
        row1.pack(fill=tk.X, pady=5)

        # Период
        tk.Label(row1, text="Период анализа:", font=('Arial', 10),
                 bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.period_var = tk.StringVar(value="12")
        period_combo = ttk.Combobox(row1, textvariable=self.period_var,
                                    values=["3", "6", "12", "24"], width=8)
        period_combo.pack(side=tk.LEFT, padx=(0, 5))
        # ↓↓↓ ДОБАВЬТЕ ЭТУ СТРОКУ ↓↓↓
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.load_analytics())

        tk.Label(row1, text="месяцев", font=('Arial', 10),
                 bg='white').pack(side=tk.LEFT, padx=(0, 30))

        # Год
        tk.Label(row1, text="Год:", font=('Arial', 10),
                 bg='white').pack(side=tk.LEFT, padx=(0, 10))

        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(row1, textvariable=self.year_var,
                                  values=[str(y) for y in range(current_year - 3, current_year + 1)],
                                  width=8)
        year_combo.pack(side=tk.LEFT, padx=(0, 30))
        # ↓↓↓ ДОБАВЬТЕ ЭТУ СТРОКУ ↓↓↓
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_analytics())

        # Кнопка обновления (оставляем на всякий случай)
        update_btn = tk.Button(row1, text="🔄 Обновить аналитику",
                               command=self.load_analytics,
                               bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                               padx=20, pady=5, cursor='hand2')
        update_btn.pack(side=tk.LEFT, padx=10)

        # Ряд 2: Информация
        row2 = tk.Frame(inner_frame, bg='white')
        row2.pack(fill=tk.X, pady=5)

        info_label = tk.Label(row2, text="💡 Для построения прогноза необходимо минимум 3 месяца данных",
                              font=('Arial', 9), bg='white', fg='#7f8c8d')
        info_label.pack(side=tk.LEFT)

    def create_kpi_cards(self, data):
        """Создание карточек с ключевыми показателями"""

        # Очищаем предыдущие карточки
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        monthly_data = data.get('monthly_data', [])

        if not monthly_data:
            no_data_label = tk.Label(self.kpi_frame, text="Нет данных за выбранный период",
                                     font=('Arial', 12), fg='gray', bg='#f0f0f0')
            no_data_label.pack(expand=True, pady=20)
            return

        # Расчет KPI из полученных данных (НЕ ИЗ БАЗЫ!)
        total_revenue = sum(float(m.get('revenue', 0)) for m in monthly_data)
        total_orders = sum(int(m.get('orders_count', 0)) for m in monthly_data)
        avg_check = total_revenue / total_orders if total_orders > 0 else 0

        # Количество уникальных клиентов за период (через SQL)
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT client_id) FROM orders WHERE status = 'Завершено'")
        unique_clients = cursor.fetchone()[0] or 0

        # Удержание клиентов
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT client_id, COUNT(*) as cnt 
                FROM orders 
                WHERE status = 'Завершено'
                GROUP BY client_id 
                HAVING cnt > 1
            ) as returning
        """)
        returning = cursor.fetchone()[0] or 0
        cursor.close()

        retention_rate = (returning / unique_clients * 100) if unique_clients > 0 else 0

        # Рентабельность (можно сделать динамической)
        profit_margin = 35

        print(f"📊 KPI: Доход={total_revenue}, Заказов={total_orders}, Средний чек={avg_check}")  # Отладка

        # Данные для карточек
        kpis = [
            ("💰 ОБЩИЙ ДОХОД", f"{total_revenue:,.0f}", "руб.", "#27ae60"),
            ("📊 СРЕДНИЙ ЧЕК", f"{avg_check:,.0f}", "руб.", "#3498db"),
            ("📈 РЕНТАБЕЛЬНОСТЬ", f"{profit_margin:.1f}", "%", "#f39c12"),
            ("👥 КЛИЕНТЫ", f"{unique_clients}", "", "#9b59b6"),
            ("🔄 УДЕРЖАНИЕ", f"{retention_rate:.1f}", "%", "#1abc9c"),
            ("📦 ЗАКАЗЫ", f"{total_orders}", "", "#e74c3c")
        ]

        # ... остальной код создания карточек ...

        # Создаем карточки в сетке (3x2)
        row_num = 0
        col_num = 0
        max_cols = 3

        for title, value, unit, color in kpis:
            # Карточка
            card = tk.Frame(self.kpi_frame, bg='white', relief=tk.RAISED, bd=1,
                            highlightthickness=0)
            card.grid(row=row_num, column=col_num, padx=5, pady=5, sticky='nsew')

            # Настройка растягивания
            self.kpi_frame.grid_columnconfigure(col_num, weight=1)

            # Внутренний контейнер
            inner = tk.Frame(card, bg='white')
            inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            # Заголовок
            tk.Label(inner, text=title, font=('Arial', 10, 'bold'),
                     bg='white', fg='#7f8c8d').pack()

            # Значение
            value_frame = tk.Frame(inner, bg='white')
            value_frame.pack(pady=(10, 0))

            tk.Label(value_frame, text=value, font=('Arial', 24, 'bold'),
                     bg='white', fg=color).pack(side=tk.LEFT)

            if unit:
                tk.Label(value_frame, text=unit, font=('Arial', 14),
                         bg='white', fg=color).pack(side=tk.LEFT, padx=(2, 0))

            # Обновляем колонку и строку
            col_num += 1
            if col_num >= max_cols:
                col_num = 0
                row_num += 1

        # Настройка веса строк
        for i in range(row_num + 1):
            self.kpi_frame.grid_rowconfigure(i, weight=1)

    def create_chart_in_grid(self, parent, title, row, col, rowspan=1, colspan=1):
        """Создание контейнера для графика в сетке"""

        # Настройка сетки
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

        # Фрейм для графика
        frame = tk.LabelFrame(parent, text=title, font=('Arial', 11, 'bold'),
                              padx=10, pady=10, bg='white')
        frame.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
                   padx=5, pady=5, sticky='nsew')

        return frame

    def load_analytics(self):
        """Загрузка всех аналитических данных"""

        # Очищаем область графиков
        for widget in self.charts_grid.winfo_children():
            widget.destroy()

        # Получаем параметры
        months = int(self.period_var.get())
        year = int(self.year_var.get())

        print(f"📊 ===== ЗАГРУЗКА АНАЛИТИКИ =====")
        print(f"📊 Период: {months} месяцев")
        print(f"📊 Год: {year}")

        # Показываем индикатор загрузки
        loading_label = tk.Label(self.charts_grid, text="⏳ Загрузка данных...",
                                 font=('Arial', 14), fg='gray', bg='#f0f0f0')
        loading_label.pack(expand=True, pady=50)
        self.charts_grid.update()

        # Получаем данные
        data = self.get_financial_data(months, year)

        # Удаляем индикатор
        loading_label.destroy()

        if not data or not data.get('monthly_data'):
            error_label = tk.Label(self.charts_grid,
                                   text=f"Нет данных для анализа за период: {months} месяцев {year} года",
                                   font=('Arial', 14), fg='gray', bg='#f0f0f0')
            error_label.pack(expand=True, pady=50)
            return

        # Обновляем заголовок с информацией о периоде
        if 'start_date' in data and 'end_date' in data:
            period_text = f"Период: {data['start_date'].strftime('%d.%m.%Y')} - {data['end_date'].strftime('%d.%m.%Y')}"
            # Можно добавить где-нибудь отображение периода
            print(f"📊 {period_text}")

        # Создаем KPI карточки
        self.create_kpi_cards(data)

        # Настраиваем сетку графиков
        self.charts_grid.grid_rowconfigure(0, weight=1)
        self.charts_grid.grid_rowconfigure(1, weight=1)
        self.charts_grid.grid_rowconfigure(2, weight=1)
        self.charts_grid.grid_columnconfigure(0, weight=1)
        self.charts_grid.grid_columnconfigure(1, weight=1)

        # Создаем все графики с новыми данными
        self.create_revenue_chart(data, self.charts_grid, 0, 0)
        self.create_profit_margin_chart(data, self.charts_grid, 0, 1)
        self.create_top_services_chart(data, self.charts_grid, 1, 0)
        self.create_seasonality_chart(data, self.charts_grid, 1, 1)
        self.create_forecast_chart(data, self.charts_grid, 2, 0, colspan=2)

    def refresh_all_charts(self):
        """Принудительное обновление всех графиков"""
        print("🔄 Принудительное обновление аналитики...")
        self.load_analytics()

    def get_financial_data(self, months, year):
        """Получение финансовых данных из базы за указанный период"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)

            print(f"📊 Запрос данных: период={months} месяцев, год={year}")

            # Рассчитываем дату начала периода
            from datetime import datetime
            current_date = datetime.now()

            # Если выбран текущий год, считаем от текущей даты
            if year == current_date.year:
                start_date = current_date - timedelta(days=months * 30)
            else:
                # Для прошлых годов берём полный год
                start_date = datetime(year, 1, 1)

            end_date = datetime(year, 12, 31) if year == current_date.year else datetime(year, 12, 31)

            print(f"📅 Период: с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")

            # Получаем помесячные данные за указанный период
            query = """
                SELECT 
                    DATE_FORMAT(order_date, '%%Y-%%m') as month,
                    DATE_FORMAT(order_date, '%%m') as month_num,
                    SUM(CASE WHEN status = 'Завершено' THEN total_amount ELSE 0 END) as revenue,
                    COUNT(CASE WHEN status = 'Завершено' THEN 1 END) as orders_count,
                    AVG(CASE WHEN status = 'Завершено' THEN total_amount ELSE NULL END) as avg_check
                FROM orders
                WHERE order_date >= %s 
                    AND order_date <= %s
                    AND status = 'Завершено'
                GROUP BY DATE_FORMAT(order_date, '%%Y-%%m'), DATE_FORMAT(order_date, '%%m')
                ORDER BY month ASC
            """

            cursor.execute(query, (start_date, end_date))
            monthly_data = cursor.fetchall()

            # Если нужно ограничить количество месяцев (для текущего года)
            if len(monthly_data) > months and year == current_date.year:
                monthly_data = monthly_data[-months:]

            print(f"📊 Получено {len(monthly_data)} месяцев данных")
            for m in monthly_data:
                print(f"   {m['month']}: {m['revenue']} руб.")

            # Получаем топ услуг за указанный период
            query_top = """
                SELECT 
                    s.name as service_name,
                    COUNT(o.id) as order_count,
                    SUM(o.total_amount) as total_revenue,
                    AVG(o.total_amount) as avg_price
                FROM orders o
                JOIN services s ON o.service_id = s.id
                WHERE o.status = 'Завершено'
                    AND o.order_date >= %s 
                    AND o.order_date <= %s
                GROUP BY s.id
                ORDER BY total_revenue DESC
                LIMIT 5
            """
            cursor.execute(query_top, (start_date, end_date))
            top_services = cursor.fetchall()

            cursor.close()

            return {
                'monthly_data': monthly_data,
                'top_services': top_services,
                'year': year,
                'months': months,
                'start_date': start_date,
                'end_date': end_date
            }

        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_revenue_chart(self, data, parent, row, col):
        """График доходов по месяцам"""

        frame = self.create_chart_in_grid(parent, "📈 Динамика доходов", row, col)

        monthly_data = data['monthly_data']

        if monthly_data:
            # Подготовка данных
            months = [m['month'][5:7] for m in monthly_data]
            revenues = [float(m['revenue']) for m in monthly_data]

            # Адаптивный размер графика
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

            # Столбчатая диаграмма
            bars = ax.bar(months, revenues, color='#3498db', alpha=0.7)

            # Линия тренда
            x = np.arange(len(months))
            if len(x) > 1:
                z = np.polyfit(x, revenues, 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), "r--", alpha=0.8, linewidth=2, label='Тренд')

            ax.set_xlabel('Месяц', fontsize=10)
            ax.set_ylabel('Доход (руб.)', fontsize=10)
            ax.set_title(f'Динамика доходов', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Добавляем значения на столбцы
            for i, (bar, val) in enumerate(zip(bars, revenues)):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1000,
                        f'{val:,.0f}', ha='center', va='bottom', fontsize=8, rotation=45)

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(frame, text="Нет данных для отображения",
                     font=('Arial', 12), fg='gray').pack(expand=True)

    def create_profit_margin_chart(self, data, parent, row, col):
        """График рентабельности и среднего чека"""

        frame = self.create_chart_in_grid(parent, "📊 Анализ эффективности", row, col)

        monthly_data = data['monthly_data']

        if monthly_data:
            fig, ax1 = plt.subplots(figsize=(6, 4), dpi=100)

            months = [m['month'][5:7] for m in monthly_data]
            avg_checks = [float(m['avg_check']) if m['avg_check'] else 0 for m in monthly_data]
            orders_count = [int(m['orders_count']) for m in monthly_data]

            # График среднего чека
            color = '#27ae60'
            ax1.set_xlabel('Месяц', fontsize=10)
            ax1.set_ylabel('Средний чек (руб.)', color=color, fontsize=10)
            line1 = ax1.plot(months, avg_checks, color=color, marker='o', linewidth=2, label='Средний чек')
            ax1.tick_params(axis='y', labelcolor=color)

            # Вторая ось для количества заказов
            ax2 = ax1.twinx()
            color2 = '#3498db'
            ax2.set_ylabel('Количество заказов', color=color2, fontsize=10)
            bars = ax2.bar(months, orders_count, color=color2, alpha=0.3, label='Кол-во заказов')
            ax2.tick_params(axis='y', labelcolor=color2)

            ax1.grid(True, alpha=0.3)
            ax1.set_title('Динамика среднего чека и количества заказов', fontsize=11)

            # Легенда
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(frame, text="Нет данных для отображения",
                     font=('Arial', 12), fg='gray').pack(expand=True)

    def create_top_services_chart(self, data, parent, row, col):
        """Круговая диаграмма топ услуг"""

        frame = self.create_chart_in_grid(parent, "🥇 Топ услуг по доходу", row, col)

        # Очищаем предыдущий график
        for widget in frame.winfo_children():
            widget.destroy()

        top_services = data.get('top_services', [])

        if top_services:
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

            names = [s['service_name'][:15] for s in top_services]
            revenues = [float(s['total_revenue']) for s in top_services]

            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            wedges, texts, autotexts = ax.pie(revenues, labels=names, autopct='%1.1f%%',
                                              colors=colors, textprops={'fontsize': 9})

            ax.set_title('Распределение доходов по услугам', fontsize=11)

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(frame, text="Нет данных для отображения",
                     font=('Arial', 12), fg='gray').pack(expand=True)

    def create_seasonality_chart(self, data, parent, row, col):
        """График сезонности (по месяцам за все годы)"""

        frame = self.create_chart_in_grid(parent, "📅 Сезонность продаж", row, col)

        try:
            cursor = self.db.connection.cursor(dictionary=True)

            query = """
                SELECT 
                    MONTH(order_date) as month_num,
                    SUM(total_amount) as total_revenue,
                    COUNT(*) as order_count
                FROM orders
                WHERE status = 'Завершено'
                GROUP BY MONTH(order_date)
                ORDER BY month_num
            """
            cursor.execute(query)
            season_data = cursor.fetchall()
            cursor.close()

            if season_data:
                fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

                months_num = [d['month_num'] for d in season_data]
                revenues = [float(d['total_revenue']) for d in season_data]

                month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                               'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

                bars = ax.bar([month_names[m - 1] for m in months_num], revenues,
                              color='#e74c3c', alpha=0.7)
                ax.set_xlabel('Месяц', fontsize=10)
                ax.set_ylabel('Доход (руб.)', fontsize=10)
                ax.set_title('Сезонность продаж (все годы)', fontsize=11)
                ax.grid(True, alpha=0.3)

                # Находим пиковый месяц
                max_idx = revenues.index(max(revenues))
                bars[max_idx].set_color('#c0392b')
                bars[max_idx].set_alpha(0.9)

                # Добавляем подпись пика
                ax.text(months_num[max_idx] - 1, max(revenues) + 1000, '📈 ПИК',
                        ha='center', fontsize=9, color='red', fontweight='bold')

                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                tk.Label(frame, text="Нет данных для отображения",
                         font=('Arial', 12), fg='gray').pack(expand=True)

        except Exception as e:
            print(f"Ошибка сезонности: {e}")
            tk.Label(frame, text="Ошибка загрузки данных",
                     font=('Arial', 12), fg='gray').pack(expand=True)

    def create_forecast_chart(self, data, parent, row, col, colspan=1):
        """Прогнозирование доходов"""

        frame = self.create_chart_in_grid(parent, "🔮 Прогноз доходов", row, col)
        frame.grid(row=row, column=col, rowspan=1, columnspan=colspan,
                   padx=5, pady=5, sticky='nsew')

        monthly_data = data.get('monthly_data', [])

        if len(monthly_data) >= 3:
            try:
                from sklearn.linear_model import LinearRegression

                # Подготовка данных
                revenues = [float(m['revenue']) for m in monthly_data]
                x = np.arange(len(revenues)).reshape(-1, 1)
                y = np.array(revenues)

                # Обучение модели
                model = LinearRegression()
                model.fit(x, y)

                # Прогноз на 3 месяца вперед
                future_x = np.arange(len(revenues), len(revenues) + 3).reshape(-1, 1)
                forecast = model.predict(future_x)

                # Создаем график
                fig, ax = plt.subplots(figsize=(7, 4), dpi=100)

                # Исторические данные
                months_hist = [m['month'][5:7] for m in monthly_data]
                ax.plot(months_hist, revenues, 'b-o', linewidth=2, label='Факт', markersize=8)

                # Прогноз
                future_months = [f'+{i + 1}' for i in range(3)]
                ax.plot(future_months, forecast, 'r--o', linewidth=2, label='Прогноз', markersize=8)

                # Заполнение области доверия
                std = np.std([y[i] - model.predict([[i]])[0] for i in range(len(y))])
                ax.fill_between(range(len(months_hist), len(months_hist) + 3),
                                forecast - std, forecast + std, alpha=0.2, color='red')

                ax.set_xlabel('Период', fontsize=10)
                ax.set_ylabel('Доход (руб.)', fontsize=10)
                ax.set_title('Прогноз доходов на следующие 3 месяца', fontsize=11)
                ax.legend(loc='upper left')
                ax.grid(True, alpha=0.3)

                # Добавляем значения
                for i, val in enumerate(forecast):
                    ax.text(len(months_hist) + i, val + 1000, f'{val:,.0f}',
                            ha='center', fontsize=9, color='red', fontweight='bold')

                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                # Добавляем текстовый прогноз
                forecast_frame = tk.Frame(frame, bg='#f0f8ff', relief=tk.RIDGE, bd=1)
                forecast_frame.pack(fill=tk.X, pady=(10, 0))

                # Иконка и текст
                tk.Label(forecast_frame, text="📊", font=('Arial', 16),
                         bg='#f0f8ff').pack(side=tk.LEFT, padx=10, pady=5)

                forecast_text = f"Прогноз на следующий месяц: {forecast[0]:,.0f} руб."
                tk.Label(forecast_frame, text=forecast_text, font=('Arial', 11, 'bold'),
                         fg='#e74c3c', bg='#f0f8ff').pack(side=tk.LEFT, padx=10, pady=5)

            except ImportError:
                tk.Label(frame, text="⚠️ Для прогнозирования установите scikit-learn\n\npip install scikit-learn",
                         font=('Arial', 10), fg='gray', justify='center').pack(expand=True)
        else:
            tk.Label(frame, text=f"⚠️ Недостаточно данных для прогноза\n(минимум 3 месяца, сейчас {len(monthly_data)})",
                     font=('Arial', 11), fg='gray', justify='center').pack(expand=True)

