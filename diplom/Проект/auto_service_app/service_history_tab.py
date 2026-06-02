import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from date_picker import DatePicker


class ServiceHistoryTab:
    """Вкладка истории обслуживания автомобилей (только просмотр)"""

    def __init__(self, parent, db, user_manager):
        self.parent = parent
        self.db = db
        self.user_manager = user_manager
        self.current_car_id = None

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_clients_list()

    def get_tab(self):
        return self.frame

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.frame, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🔧 История обслуживания автомобилей",
                 font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(expand=True)

        # Панель выбора
        select_frame = tk.LabelFrame(self.frame, text="Выбор автомобиля", padx=10, pady=10)
        select_frame.pack(fill=tk.X, padx=10, pady=10)

        row0 = tk.Frame(select_frame)
        row0.pack(fill=tk.X, pady=5)

        tk.Label(row0, text="Клиент:").pack(side=tk.LEFT, padx=(0, 5))
        self.client_combo = ttk.Combobox(row0, width=30)
        self.client_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.client_combo.bind('<<ComboboxSelected>>', self.on_client_select)

        tk.Label(row0, text="Автомобиль:").pack(side=tk.LEFT, padx=(0, 5))
        self.car_combo = ttk.Combobox(row0, width=35)
        self.car_combo.pack(side=tk.LEFT)
        self.car_combo.bind('<<ComboboxSelected>>', self.on_car_select)

        row1 = tk.Frame(select_frame)
        row1.pack(fill=tk.X, pady=10)

        tk.Button(row1, text="➕ Добавить автомобиль",
                  command=self.add_car_dialog,
                  bg='#27ae60', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(row1, text="📝 Добавить обслуживание",
                  command=self.add_service_dialog,
                  bg='#3498db', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(row1, text="🔄 Обновить",
                  command=self.refresh,
                  bg='#95a5a6', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(self.frame, text="Выберите клиента и автомобиль",
                                   font=('Arial', 10), fg='gray', bg='#f0f0f0')
        self.info_label.pack(pady=5)

        # Таблица истории
        history_frame = tk.LabelFrame(self.frame, text="История обслуживания", padx=10, pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Дата', 'Вид услуги', 'Пробег (км)', 'Следующий пробег', 'Стоимость (руб)', 'Мастер')
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)

        col_widths = [50, 100, 200, 100, 120, 120, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Контекстное меню (только подробная информация)
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="📋 Подробная информация", command=self.show_record_details)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.show_record_details())

    # ==================== ЗАГРУЗКА ДАННЫХ ====================

    def load_clients_list(self):
        try:
            clients = self.db.get_clients()
            client_list = [f"{c[1]} {c[2]} (ID:{c[0]})" for c in clients]
            self.client_combo['values'] = client_list
            if client_list:
                self.client_combo.set(client_list[0])
                client_id = int(client_list[0].split('ID:')[1].rstrip(')'))
                self.load_client_cars(client_id)
        except Exception as e:
            print(f"Ошибка: {e}")

    def on_client_select(self, event):
        selection = self.client_combo.get()
        if selection:
            client_id = int(selection.split('ID:')[1].rstrip(')'))
            self.load_client_cars(client_id)

    def load_client_cars(self, client_id):
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM client_cars WHERE client_id = %s ORDER BY id DESC', (client_id,))
            cars = cursor.fetchall()
            cursor.close()

            if cars:
                car_list = [f"{c['brand']} {c['model']} ({c['license_plate']}) - ID:{c['id']}" for c in cars]
                self.car_combo['values'] = car_list
                self.car_combo.set(car_list[0])
                self.current_car_id = cars[0]['id']
                self.load_car_history(self.current_car_id)

                car = cars[0]
                self.info_label.config(
                    text=f"🚗 {car['brand']} {car['model']} | {car['year'] or '?'} г. | {car['license_plate']}",
                    fg='#2c3e50'
                )
            else:
                self.car_combo['values'] = []
                self.car_combo.set('')
                self.current_car_id = None
                self.info_label.config(text="У клиента нет автомобилей", fg='orange')
                self.tree.delete(*self.tree.get_children())
        except Exception as e:
            print(f"Ошибка: {e}")

    def on_car_select(self, event):
        selection = self.car_combo.get()
        if selection:
            car_id = int(selection.split('ID:')[1])
            self.current_car_id = car_id
            self.load_car_history(car_id)

            try:
                cursor = self.db.connection.cursor(dictionary=True)
                cursor.execute('SELECT * FROM client_cars WHERE id = %s', (car_id,))
                car = cursor.fetchone()
                cursor.close()
                if car:
                    self.info_label.config(text=f"🚗 {car['brand']} {car['model']} | {car['license_plate']}")
            except:
                pass

    def load_car_history(self, car_id):
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM service_history WHERE car_id = %s ORDER BY service_date DESC', (car_id,))
            history = cursor.fetchall()
            cursor.close()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for record in history:
                service_date = record.get('service_date')
                date_str = service_date.strftime('%d.%m.%Y') if service_date else '-'
                cost_str = f"{record.get('cost', 0):,.0f}" if record.get('cost') else '-'

                self.tree.insert('', tk.END, values=(
                    record.get('id', ''),
                    date_str,
                    record.get('service_type', '-'),
                    record.get('mileage', '-'),
                    record.get('next_mileage', '-'),
                    cost_str,
                    record.get('master_name', '-')
                ))
        except Exception as e:
            print(f"Ошибка: {e}")

    def refresh(self):
        selection = self.client_combo.get()
        if selection:
            client_id = int(selection.split('ID:')[1].rstrip(')'))
            self.load_client_cars(client_id)

    # ==================== ДИАЛОГИ ====================

    def add_car_dialog(self):
        selection = self.client_combo.get()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return

        client_id = int(selection.split('ID:')[1].rstrip(')'))

        dialog = tk.Toplevel(self.frame)
        dialog.title("Добавить автомобиль")
        dialog.geometry("400x450")
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Добавление автомобиля", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = tk.Frame(dialog)
        frame.pack(padx=20, pady=10)

        entries = {}
        fields = [
            ('Марка:*', 'brand'),
            ('Модель:*', 'model'),
            ('Год:', 'year'),
            ('Госномер:*', 'license_plate'),
            ('VIN:', 'vin'),
            ('Цвет:', 'color')
        ]

        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(frame, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[key] = entry

        def save():
            brand = entries['brand'].get().strip()
            model = entries['model'].get().strip()
            plate = entries['license_plate'].get().strip()

            if not brand or not model or not plate:
                messagebox.showwarning("Внимание", "Заполните марку, модель и госномер")
                return

            try:
                cursor = self.db.connection.cursor()
                cursor.execute('''
                    INSERT INTO client_cars (client_id, brand, model, year, license_plate, vin, color)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (client_id, brand, model, entries['year'].get() or None,
                      plate, entries['vin'].get() or None, entries['color'].get() or None))
                self.db.connection.commit()
                cursor.close()

                messagebox.showinfo("Успех", "Автомобиль добавлен")
                dialog.destroy()
                self.load_client_cars(client_id)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Сохранить", command=save, bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT,
                                                                                                     padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg='#95a5a6', fg='white', padx=20).pack(
            side=tk.LEFT, padx=10)

    def add_service_dialog(self):
        if not self.current_car_id:
            messagebox.showwarning("Внимание", "Выберите автомобиль")
            return

        dialog = tk.Toplevel(self.frame)
        dialog.title("Добавить обслуживание")
        dialog.geometry("450x550")
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Добавление записи об обслуживании", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = tk.Frame(dialog)
        frame.pack(padx=20, pady=10)

        # Вид услуги
        tk.Label(frame, text="Вид услуги:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        service_combo = ttk.Combobox(frame, width=27)
        service_combo['values'] = ["Замена масла", "Замена тормозных колодок", "Замена ремня ГРМ",
                                   "Диагностика", "Развал-схождение", "Техобслуживание", "Другое"]
        service_combo.grid(row=0, column=1, padx=10, pady=5)

        # Дата
        tk.Label(frame, text="Дата:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        date_picker = DatePicker(frame)
        date_picker.grid(row=1, column=1, padx=10, pady=5)

        # Пробег
        tk.Label(frame, text="Пробег (км):*").grid(row=2, column=0, sticky=tk.W, pady=5)
        mileage_entry = tk.Entry(frame, width=30)
        mileage_entry.grid(row=2, column=1, padx=10, pady=5)

        # Следующий пробег
        tk.Label(frame, text="Следующий пробег (км):").grid(row=3, column=0, sticky=tk.W, pady=5)
        next_mileage_entry = tk.Entry(frame, width=30)
        next_mileage_entry.grid(row=3, column=1, padx=10, pady=5)

        # Стоимость
        tk.Label(frame, text="Стоимость (руб.):").grid(row=4, column=0, sticky=tk.W, pady=5)
        cost_entry = tk.Entry(frame, width=30)
        cost_entry.grid(row=4, column=1, padx=10, pady=5)

        # Мастер
        tk.Label(frame, text="Мастер:").grid(row=5, column=0, sticky=tk.W, pady=5)
        master_entry = tk.Entry(frame, width=30)
        if self.user_manager.current_user:
            master_entry.insert(0, self.user_manager.current_user.get('full_name', ''))
        master_entry.grid(row=5, column=1, padx=10, pady=5)

        # Примечания
        tk.Label(frame, text="Примечания:").grid(row=6, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(frame, width=30, height=3)
        notes_text.grid(row=6, column=1, padx=10, pady=5)

        def save():
            service_type = service_combo.get()
            mileage = mileage_entry.get()

            if not service_type or not mileage:
                messagebox.showwarning("Внимание", "Заполните вид услуги и пробег")
                return

            try:
                cursor = self.db.connection.cursor()
                cursor.execute('''
                    INSERT INTO service_history 
                    (car_id, service_date, service_type, mileage, next_mileage, cost, master_name, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (self.current_car_id, date_picker.get(), service_type, int(mileage),
                      int(next_mileage_entry.get()) if next_mileage_entry.get() else None,
                      float(cost_entry.get()) if cost_entry.get() else 0,
                      master_entry.get(), notes_text.get("1.0", tk.END).strip()))
                self.db.connection.commit()
                cursor.close()

                messagebox.showinfo("Успех", "Запись добавлена")
                dialog.destroy()
                self.load_car_history(self.current_car_id)
            except ValueError:
                messagebox.showerror("Ошибка", "Пробег и стоимость должны быть числами")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Сохранить", command=save, bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT,
                                                                                                     padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg='#95a5a6', fg='white', padx=20).pack(
            side=tk.LEFT, padx=10)

    # ==================== КОНТЕКСТНОЕ МЕНЮ (ТОЛЬКО ПРОСМОТР) ====================

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_record(self):
        selection = self.tree.selection()
        if not selection:
            return None
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values or len(values) < 7:
            return None
        return {
            'record_id': values[0],
            'date': values[1],
            'service_type': values[2],
            'mileage': values[3],
            'next_mileage': values[4],
            'cost': values[5],
            'master': values[6]
        }

    def show_record_details(self):
        """Показать подробную информацию"""
        record = self.get_selected_record()
        if not record:
            messagebox.showwarning("Внимание", "Выберите запись")
            return

        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT sh.*, c.first_name, c.last_name, c.phone, c.email,
                       ct.brand, ct.model, ct.license_plate, ct.vin, ct.year, ct.color
                FROM service_history sh
                LEFT JOIN client_cars ct ON sh.car_id = ct.id
                LEFT JOIN clients c ON ct.client_id = c.id
                WHERE sh.id = %s
            ''', (record['record_id'],))
            data = cursor.fetchone()
            cursor.close()

            if not data:
                messagebox.showerror("Ошибка", "Данные не найдены")
                return

            # Окно с подробной информацией
            win = tk.Toplevel(self.frame)
            win.title(f"Детали обслуживания")
            win.geometry("500x500")
            win.transient(self.frame)
            win.grab_set()

            win.update_idletasks()
            x = (win.winfo_screenwidth() // 2) - (500 // 2)
            y = (win.winfo_screenheight() // 2) - (500 // 2)
            win.geometry(f"+{x}+{y}")

            tk.Label(win, text="📋 ПОДРОБНАЯ ИНФОРМАЦИЯ", font=('Arial', 14, 'bold'),
                     bg='#2c3e50', fg='white').pack(fill=tk.X, pady=10)

            frame = tk.Frame(win, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            service_date = data.get('service_date')
            date_str = service_date.strftime('%d.%m.%Y') if service_date else '-'

            info_text = f"""
🚗 АВТОМОБИЛЬ:
   {data.get('brand', '-')} {data.get('model', '-')}
   Госномер: {data.get('license_plate', '-')}
   VIN: {data.get('vin', '-')}
   Год: {data.get('year', '-')}

👤 КЛИЕНТ:
   {data.get('first_name', '-')} {data.get('last_name', '-')}
   Телефон: {data.get('phone', '-')}
   Email: {data.get('email', '-')}

🔧 ОБСЛУЖИВАНИЕ:
   Дата: {date_str}
   Услуга: {data.get('service_type', '-')}
   Пробег: {data.get('mileage', '-')} км
   Следующий пробег: {data.get('next_mileage', '-')} км
   Стоимость: {data.get('cost', 0):,.2f} руб.
   Мастер: {data.get('master_name', '-')}
            """

            if data.get('notes'):
                info_text += f"\n📝 ПРИМЕЧАНИЯ:\n   {data.get('notes')}"

            tk.Label(frame, text=info_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor='w')
            tk.Button(frame, text="Закрыть", command=win.destroy,
                      bg='#3498db', fg='white', padx=20, pady=8).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")