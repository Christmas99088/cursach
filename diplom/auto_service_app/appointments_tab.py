import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database import AppointmentManager
from date_picker import DatePicker


class AppointmentsTab:
    """Вкладка записи клиентов"""

    def __init__(self, parent, db, user_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager

        # Инициализация менеджера
        self.appointment_manager = AppointmentManager(db)
        self.db.appointment_manager = self.appointment_manager

        self.tab = ttk.Frame(parent)
        self.create_widgets()
        self.load_today_appointments()

    def get_tab(self):
        return self.tab

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.tab, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📅 ЗАПИСЬ КЛИЕНТОВ",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Основной контейнер
        main_frame = tk.Frame(self.tab, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - форма записи
        left_frame = tk.LabelFrame(main_frame, text="Новая запись", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.create_booking_form(left_frame)

        # Правая панель - список записей
        right_frame = tk.LabelFrame(main_frame, text="Записи", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.create_appointments_list(right_frame)

    def create_booking_form(self, parent):
        """Создание формы записи"""
        # Клиент
        tk.Label(parent, text="Клиент:*", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.client_combo = ttk.Combobox(parent, width=40)
        self.client_combo.pack(fill=tk.X, pady=(0, 10))
        self.client_combo.bind('<<ComboboxSelected>>', self.on_client_select)

        # Автомобиль
        tk.Label(parent, text="Автомобиль:", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.car_combo = ttk.Combobox(parent, width=40)
        self.car_combo.pack(fill=tk.X, pady=(0, 10))

        # Услуга
        tk.Label(parent, text="Услуга:*", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.service_combo = ttk.Combobox(parent, width=40)
        self.service_combo.pack(fill=tk.X, pady=(0, 10))

        # Дата
        tk.Label(parent, text="Дата:*", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.date_picker = DatePicker(parent)
        self.date_picker.pack(fill=tk.X, pady=(0, 10))
        self.date_picker.date_var.trace('w', lambda *a: self.load_available_slots())

        # Время
        tk.Label(parent, text="Время:*", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.time_combo = ttk.Combobox(parent, width=40)
        self.time_combo.pack(fill=tk.X, pady=(0, 10))

        # Мастер
        tk.Label(parent, text="Мастер:", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.master_combo = ttk.Combobox(parent, width=40)
        self.master_combo.pack(fill=tk.X, pady=(0, 10))
        self.master_combo.bind('<<ComboboxSelected>>', lambda e: self.load_available_slots())

        # Примечания
        tk.Label(parent, text="Примечания:", font=('Arial', 10)).pack(anchor='w', pady=(0, 2))
        self.notes_text = tk.Text(parent, width=40, height=3)
        self.notes_text.pack(fill=tk.X, pady=(0, 10))

        # Кнопка сохранения
        save_btn = tk.Button(parent, text="✅ Записать клиента", command=self.save_appointment,
                             bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8)
        save_btn.pack(pady=10)

        # Загрузка данных
        self.load_clients_list()
        self.load_services_list()
        self.load_masters_list()

    def create_appointments_list(self, parent):
        """Создание списка записей"""
        # Панель фильтров
        filter_frame = tk.Frame(parent, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="Дата:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_date_picker = DatePicker(filter_frame)
        self.filter_date_picker.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date_picker.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.filter_date_picker.date_var.trace('w', lambda *a: self.load_appointments_by_date())

        refresh_btn = tk.Button(filter_frame, text="🔄", command=self.load_appointments_by_date,
                                bg='#3498db', fg='white', width=3)
        refresh_btn.pack(side=tk.LEFT)

        # Таблица записей
        table_frame = tk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('ID', 'Время', 'Клиент', 'Авто', 'Услуга', 'Мастер', 'Статус')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        col_widths = [50, 80, 150, 120, 150, 120, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Контекстное меню для изменения статуса
        self.status_menu = tk.Menu(self.tree, tearoff=0)
        self.status_menu.add_command(label="✅ Подтвердить", command=lambda: self.change_status('confirmed'))
        self.status_menu.add_command(label="✔️ Выполнено", command=lambda: self.change_status('completed'))
        self.status_menu.add_command(label="❌ Отменить", command=lambda: self.change_status('cancelled'))
        self.tree.bind("<Button-3>", self.show_context_menu)

    def load_clients_list(self):
        """Загрузка списка клиентов"""
        clients = self.db.get_clients()
        self.client_combo['values'] = [f"{c[1]} {c[2]} (ID:{c[0]})" for c in clients]

    def load_services_list(self):
        """Загрузка списка услуг"""
        services = self.db.get_services()
        self.service_combo['values'] = [f"{s[1]} - {s[3]} руб." for s in services]
        self.service_combo.bind('<<ComboboxSelected>>', self.on_service_select)

    def on_service_select(self, event):
        """При выборе услуги - обновляем длительность"""
        selection = self.service_combo.get()
        if selection:
            # Можно получить длительность услуги для расчета времени
            pass

    def load_masters_list(self):
        """Загрузка списка мастеров"""
        masters = ['Иван Иванов', 'Петр Петров', 'Алексей Смирнов']
        self.master_combo['values'] = masters
        if masters:
            self.master_combo.set(masters[0])

    def on_client_select(self, event):
        """При выборе клиента - загружаем его автомобили"""
        selection = self.client_combo.get()
        if selection:
            client_id = int(selection.split('ID:')[1].rstrip(')'))
            try:
                cursor = self.db.connection.cursor(dictionary=True)
                cursor.execute('SELECT * FROM client_cars WHERE client_id = %s', (client_id,))
                cars = cursor.fetchall()
                cursor.close()

                if cars:
                    self.car_combo['values'] = [f"{c['brand']} {c['model']} ({c['license_plate']})" for c in cars]
                    self.car_combo.set(self.car_combo['values'][0])
                else:
                    self.car_combo['values'] = []
                    self.car_combo.set('Нет автомобилей')
            except:
                pass

    def load_available_slots(self):
        """Загрузка доступных слотов для записи"""
        date_str = self.date_picker.get()
        master = self.master_combo.get()

        if not date_str or not master:
            return

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            slots = self.appointment_manager.get_available_slots(date, master)

            if slots:
                slot_strings = [f"{s['time']} - {s['time_end']} ({s['master']})" for s in slots]
                self.time_combo['values'] = slot_strings
                if slot_strings:
                    self.time_combo.set(slot_strings[0])
            else:
                self.time_combo['values'] = []
                self.time_combo.set('Нет свободных слотов')
        except Exception as e:
            print(f"Ошибка загрузки слотов: {e}")

    def save_appointment(self):
        """Сохранение записи"""
        client = self.client_combo.get()
        service = self.service_combo.get()
        date = self.date_picker.get()
        time_slot = self.time_combo.get()
        master = self.master_combo.get()

        if not client or not service or not date or not time_slot:
            messagebox.showwarning("Внимание", "Заполните все обязательные поля")
            return

        try:
            client_id = int(client.split('ID:')[1].rstrip(')'))

            # Получаем ID услуги
            service_name = service.split(' - ')[0]
            services = self.db.get_services()
            service_id = None
            for s in services:
                if s[1] == service_name:
                    service_id = s[0]
                    break

            # Получаем ID автомобиля (если есть)
            car_id = None
            car_selection = self.car_combo.get()
            if car_selection and car_selection != 'Нет автомобилей':
                try:
                    cursor = self.db.connection.cursor()
                    cursor.execute('SELECT id FROM client_cars WHERE client_id = %s', (client_id,))
                    cars = cursor.fetchall()
                    if cars:
                        car_id = cars[0][0]
                    cursor.close()
                except:
                    pass

            # Получаем время (только час:минута)
            appointment_time = time_slot.split(' - ')[0]

            # Проверяем, что дата в правильном формате
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return

            # Создаём запись
            appointment_id = self.appointment_manager.create_appointment(
                client_id=client_id,
                car_id=car_id,
                service_id=service_id,
                appointment_date=date,  # Передаём строку, метод сам преобразует
                appointment_time=appointment_time,
                master_name=master,
                notes=self.notes_text.get("1.0", tk.END).strip()
            )

            if appointment_id:
                messagebox.showinfo("Успех", f"Клиент записан!\nДата: {date}\nВремя: {appointment_time}")
                self.clear_form()
                self.load_appointments_by_date()
                # Логируем действие
                if hasattr(self.db, 'audit_logger'):
                    self.db.audit_logger.log(
                        action_type='CREATE',
                        entity_type='appointment',
                        entity_id=appointment_id,
                        details=f"Создана запись для клиента ID:{client_id} на {date} {appointment_time}"
                    )
            else:
                messagebox.showerror("Ошибка", "Не удалось создать запись")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def clear_form(self):
        """Очистка формы"""
        self.client_combo.set('')
        self.car_combo.set('')
        self.service_combo.set('')
        self.notes_text.delete("1.0", tk.END)
        self.date_picker.set(datetime.now().strftime('%Y-%m-%d'))
        self.load_available_slots()

    def load_today_appointments(self):
        """Загрузка записей на сегодня"""
        self.filter_date_picker.set(datetime.now().strftime('%Y-%m-%d'))
        self.load_appointments_by_date()

    def load_appointments_by_date(self):
        """Загрузка записей по выбранной дате"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        date_str = self.filter_date_picker.get()
        if not date_str:
            print("Нет даты для фильтрации")
            return

        try:
            # Проверяем формат даты
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            print(f"Загрузка записей за {date}")

            # Получаем записи
            appointments = self.appointment_manager.get_appointments(date=date)
            print(f"Найдено записей: {len(appointments)}")

            # Если есть записи, выводим их в консоль для отладки
            if appointments:
                for apt in appointments:
                    print(
                        f"  - ID:{apt['id']}, {apt.get('first_name')} {apt.get('last_name')}, {apt.get('appointment_time')}")

            status_icons = {
                'pending': '⏳ Ожидает',
                'confirmed': '✅ Подтверждено',
                'completed': '✔️ Выполнено',
                'cancelled': '❌ Отменено'
            }

            for apt in appointments:
                # Форматируем время
                if apt.get('appointment_time'):
                    if hasattr(apt['appointment_time'], 'strftime'):
                        time_str = apt['appointment_time'].strftime('%H:%M')
                    else:
                        time_str = str(apt['appointment_time'])[:5]
                else:
                    time_str = '-'

                # Форматируем клиента
                client_name = f"{apt.get('first_name', '')} {apt.get('last_name', '')}".strip()
                if not client_name:
                    client_name = f"Клиент ID:{apt.get('client_id')}"

                # Форматируем авто
                car_info = "-"
                if apt.get('brand') or apt.get('model'):
                    car_info = f"{apt.get('brand', '')} {apt.get('model', '')}".strip()
                    if apt.get('license_plate'):
                        car_info += f" ({apt.get('license_plate')})"

                # Статус на русском
                status = status_icons.get(apt.get('status', 'pending'), apt.get('status', 'pending'))

                self.tree.insert('', tk.END, values=(
                    apt.get('id', ''),
                    time_str,
                    client_name,
                    car_info,
                    apt.get('service_name', '-') or '-',
                    apt.get('master_name', '-') or '-',
                    status
                ))

            # Если записей нет, показываем сообщение
            if not appointments:
                self.tree.insert('', tk.END, values=('', '', 'Нет записей на эту дату', '', '', '', ''))

        except Exception as e:
            print(f"Ошибка загрузки записей: {e}")
            import traceback
            traceback.print_exc()
            self.tree.insert('', tk.END, values=('', '', f'Ошибка: {str(e)[:50]}', '', '', '', ''))

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.status_menu.post(event.x_root, event.y_root)

    def change_status(self, new_status):
        """Изменение статуса записи"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        appointment_id = values[0]

        if self.appointment_manager.update_appointment_status(appointment_id, new_status):
            self.load_appointments_by_date()
            messagebox.showinfo("Успех", f"Статус записи изменен на '{new_status}'")
        else:
            messagebox.showerror("Ошибка", "Не удалось изменить статус")