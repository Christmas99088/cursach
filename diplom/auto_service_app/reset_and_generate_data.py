import mysql.connector
import random
from datetime import datetime, timedelta
import hashlib


def reset_and_generate_data():
    """Полная очистка и генерация всех тестовых данных"""

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        print("=" * 60)
        print("🔄 ПОЛНАЯ ОЧИСТКА БАЗЫ ДАННЫХ")
        print("=" * 60)

        # Отключаем проверку внешних ключей
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Список таблиц для очистки (в правильном порядке)
        tables = [
            'service_reminders',
            'appointments',
            'service_history',
            'financial_transactions',
            'orders',
            'client_cars',
            'user_sessions',
            'user_actions',
            'audit_log',
            'active_shift',
            'shifts',
            'permissions',
            'users',
            'services',
            'clients'
        ]

        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"   ✅ Очищена таблица: {table}")
            except Exception as e:
                print(f"   ⚠️ Не удалось очистить {table}: {e}")

        # Включаем проверку внешних ключей
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        print("\n" + "=" * 60)
        print("📊 ГЕНЕРАЦИЯ НОВЫХ ТЕСТОВЫХ ДАННЫХ")
        print("=" * 60)

        # ==================== 1. КЛИЕНТЫ (20 штук) ====================
        print("\n👥 Генерация клиентов...")

        first_names = ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей', 'Алексей', 'Иван', 'Михаил', 'Евгений',
                       'Владимир',
                       'Николай', 'Павел', 'Роман', 'Артем', 'Даниил', 'Елена', 'Ольга', 'Мария', 'Анна', 'Татьяна']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Соколов', 'Михайлов',
                      'Новиков',
                      'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев', 'Козлов', 'Егоров', 'Павлов', 'Семенов',
                      'Голубев']
        streets = ['Ленина', 'Советская', 'Мира', 'Гагарина', 'Пушкина', 'Лермонтова', 'Центральная', 'Молодежная',
                   'Строителей', 'Заводская']
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Челябинск',
                  'Самара', 'Омск', 'Ростов-на-Дону']

        clients = []
        for i in range(20):
            first = first_names[i]
            last = last_names[i]
            phone = f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(['mail.ru', 'gmail.com', 'yandex.ru', 'bk.ru'])}"
            address = f"г. {random.choice(cities)}, ул. {random.choice(streets)}, д.{random.randint(1, 100)}"
            created_date = datetime.now() - timedelta(days=random.randint(0, 730))

            cursor.execute("""
                INSERT INTO clients (first_name, last_name, phone, email, address, created_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (first, last, phone, email, address, created_date))
            clients.append(cursor.lastrowid)

        connection.commit()
        print(f"   ✅ Создано {len(clients)} клиентов")

        # ==================== 2. УСЛУГИ (30 штук) ====================
        print("\n🔧 Генерация услуг...")

        services_data = [
            # Техобслуживание
            ('Замена масла (двигатель)', 'Замена моторного масла с масляным фильтром', 2500, 45, 'Техобслуживание'),
            ('Замена масла (АКПП)', 'Замена масла в автоматической коробке передач', 4500, 90, 'Техобслуживание'),
            ('Замена масла (МКПП)', 'Замена масла в механической коробке передач', 3500, 60, 'Техобслуживание'),
            ('Замена воздушного фильтра', 'Замена воздушного фильтра двигателя', 800, 15, 'Техобслуживание'),
            ('Замена салонного фильтра', 'Замена салонного фильтра', 600, 10, 'Техобслуживание'),
            ('Замена топливного фильтра', 'Замена топливного фильтра', 1200, 30, 'Техобслуживание'),
            ('Комплексное ТО', 'Полное техническое обслуживание автомобиля', 12000, 240, 'Техобслуживание'),

            # Тормозная система
            ('Замена тормозных колодок передних', 'Замена передних тормозных колодок', 3500, 60, 'Тормозная система'),
            ('Замена тормозных колодок задних', 'Замена задних тормозных колодок', 3200, 60, 'Тормозная система'),
            ('Замена тормозных дисков', 'Замена тормозных дисков', 6000, 90, 'Тормозная система'),
            ('Замена тормозной жидкости', 'Замена тормозной жидкости', 1800, 45, 'Тормозная система'),

            # Двигатель
            ('Замена ремня ГРМ', 'Замена ремня ГРМ с роликами', 8500, 180, 'Двигатель'),
            ('Замена ремня генератора', 'Замена ремня генератора', 2500, 45, 'Двигатель'),
            ('Замена свечей зажигания', 'Замена комплекта свечей зажигания', 1800, 30, 'Двигатель'),
            ('Чистка инжектора', 'Ультразвуковая чистка форсунок', 4000, 90, 'Двигатель'),
            ('Замена антифриза', 'Замена охлаждающей жидкости', 2500, 60, 'Двигатель'),

            # Диагностика
            ('Диагностика двигателя', 'Компьютерная диагностика двигателя', 2000, 45, 'Диагностика'),
            ('Диагностика подвески', 'Полная диагностика ходовой части', 1500, 45, 'Диагностика'),
            ('Диагностика электроники', 'Диагностика электронных систем автомобиля', 2500, 60, 'Диагностика'),

            # Подвеска и рулевое
            ('Развал-схождение', 'Регулировка углов установки колес', 3500, 90, 'Подвеска'),
            ('Замена амортизаторов', 'Замена передних/задних амортизаторов', 7500, 150, 'Подвеска'),
            ('Замена шаровых опор', 'Замена шаровых опор', 4000, 90, 'Подвеска'),
            ('Замена рулевых наконечников', 'Замена рулевых наконечников', 3500, 90, 'Рулевое'),

            # Электрика
            ('Замена аккумулятора', 'Замена автомобильного аккумулятора', 1500, 20, 'Электрика'),
            ('Замена генератора', 'Замена генератора', 5500, 120, 'Электрика'),
            ('Замена стартера', 'Замена стартера', 5000, 90, 'Электрика'),

            # Климат
            ('Ремонт кондиционера', 'Ремонт системы кондиционирования', 5000, 120, 'Климат'),
            ('Заправка кондиционера', 'Заправка кондиционера фреоном', 3000, 45, 'Климат'),

            # Шиномонтаж
            ('Балансировка колес', 'Балансировка 4 колес', 2000, 45, 'Шиномонтаж'),
            ('Шиномонтаж (комплект)', 'Сезонная смена шин', 4000, 90, 'Шиномонтаж'),
        ]

        services_ids = []
        for service in services_data:
            cursor.execute("""
                INSERT INTO services (name, description, price, duration, category)
                VALUES (%s, %s, %s, %s, %s)
            """, service)
            services_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"   ✅ Создано {len(services_ids)} услуг")

        # ==================== 3. АВТОМОБИЛИ (по 1-2 на клиента) ====================
        print("\n🚗 Генерация автомобилей...")

        brands = ['Toyota', 'Hyundai', 'Kia', 'Renault', 'Volkswagen', 'Skoda', 'Ford', 'Nissan', 'BMW',
                  'Mercedes-Benz',
                  'Audi', 'Mazda', 'Mitsubishi', 'Subaru', 'Lexus', 'Honda', 'Chevrolet', 'Geely', 'Chery', 'Lada']
        models_by_brand = {
            'Toyota': ['Camry', 'Corolla', 'RAV4', 'Land Cruiser', 'Prius'],
            'Hyundai': ['Solaris', 'Creta', 'Santa Fe', 'Tucson', 'Elantra'],
            'Kia': ['Rio', 'Sportage', 'Cerato', 'Sorento', 'Optima'],
            'Renault': ['Logan', 'Sandero', 'Duster', 'Kaptur', 'Megane'],
            'Volkswagen': ['Polo', 'Golf', 'Passat', 'Tiguan', 'Jetta'],
            'Skoda': ['Octavia', 'Rapid', 'Kodiaq', 'Fabia', 'Superb'],
            'Ford': ['Focus', 'Mondeo', 'Fusion', 'Kuga', 'Explorer'],
            'Nissan': ['Almera', 'Qashqai', 'X-Trail', 'Juke', 'Teana'],
            'BMW': ['3 Series', '5 Series', 'X3', 'X5', '1 Series'],
            'Mercedes-Benz': ['E-Class', 'C-Class', 'GLC', 'S-Class', 'GLE'],
        }

        car_ids = []
        for client_id in clients:
            # 1-2 автомобиля на клиента
            num_cars = random.randint(1, 2)
            for _ in range(num_cars):
                brand = random.choice(brands)
                model = random.choice(models_by_brand.get(brand, ['Model']))
                year = random.randint(2008, 2024)
                plate = f"{random.choice(['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'])}{random.randint(100, 999)}{random.choice(['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'])}{random.randint(10, 99)}"
                vin = ''.join([chr(random.randint(65, 90)) + str(random.randint(0, 9)) for _ in range(8)])
                color = random.choice(
                    ['Белый', 'Черный', 'Серебристый', 'Синий', 'Красный', 'Серый', 'Зеленый', 'Коричневый'])

                cursor.execute("""
                    INSERT INTO client_cars (client_id, brand, model, year, license_plate, vin, color)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (client_id, brand, model, year, plate, vin, color))
                car_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"   ✅ Создано {len(car_ids)} автомобилей (в среднем по 1-2 на клиента)")

        # ==================== 4. ЗАКАЗЫ (за последние 12 месяцев) ====================
        print("\n📋 Генерация заказов...")

        statuses = ['Завершено', 'В работе', 'Новый', 'Отменено']
        status_weights = [0.65, 0.15, 0.1, 0.1]  # 65% завершено

        orders = []
        order_dates = []

        # Генерируем заказы для каждого клиента
        for client_id in clients:
            num_orders = random.randint(2, 8)  # от 2 до 8 заказов на клиента
            for _ in range(num_orders):
                service_id = random.choice(services_ids)
                total_amount = random.randint(800, 25000)
                status = random.choices(statuses, weights=status_weights)[0]
                # Дата в пределах последних 12 месяцев
                order_date = datetime.now() - timedelta(days=random.randint(1, 365))
                notes = random.choice(['', 'Предварительная запись', 'Срочный ремонт', 'Плановое ТО', 'Диагностика'])

                cursor.execute("""
                    INSERT INTO orders (client_id, service_id, total_amount, status, order_date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (client_id, service_id, total_amount, status, order_date, notes))
                orders.append(cursor.lastrowid)
                order_dates.append((cursor.lastrowid, order_date, total_amount, client_id, service_id))

        connection.commit()
        print(f"   ✅ Создано {len(orders)} заказов")

        # ==================== 5. ФИНАНСОВЫЕ ОПЕРАЦИИ ====================
        print("\n💰 Генерация финансовых операций...")

        # Доходы от завершённых заказов
        income_count = 0
        for order_id, order_date, amount, client_id, service_id in order_dates:
            # Получаем статус заказа
            cursor.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            status = cursor.fetchone()[0]

            if status == 'Завершено':
                cursor.execute("""
                    INSERT INTO financial_transactions 
                    (transaction_date, transaction_type, category, amount, order_id, client_id, description)
                    VALUES (%s, 'income', 'Ремонт автомобилей', %s, %s, %s, %s)
                """, (order_date, amount, order_id, client_id, f"Оплата заказа #{order_id}"))
                income_count += 1

        # Расходы (различные категории)
        expense_categories = [
            ('Запчасти', 5000, 50000),
            ('Расходные материалы', 1000, 15000),
            ('Аренда помещения', 30000, 60000),
            ('Зарплата сотрудников', 80000, 150000),
            ('Коммунальные услуги', 5000, 15000),
            ('Реклама', 5000, 30000),
            ('Инструмент и оборудование', 10000, 50000),
            ('Утилизация отходов', 2000, 8000),
        ]

        expense_count = 0
        for _ in range(40):
            category, min_amount, max_amount = random.choice(expense_categories)
            amount = random.randint(min_amount, max_amount)
            expense_date = datetime.now() - timedelta(days=random.randint(1, 365))
            description = f"{category} - {random.choice(['Закупка', 'Оплата', 'Счёт №' + str(random.randint(100, 999))])}"

            cursor.execute("""
                INSERT INTO financial_transactions 
                (transaction_date, transaction_type, category, amount, description)
                VALUES (%s, 'expense', %s, %s, %s)
            """, (expense_date, category, amount, description))
            expense_count += 1

        connection.commit()
        print(f"   ✅ Создано {income_count} доходных операций")
        print(f"   ✅ Создано {expense_count} расходных операций")

        # ==================== 6. ИСТОРИЯ ОБСЛУЖИВАНИЯ ====================
        print("\n🔧 Генерация истории обслуживания...")

        history_count = 0
        for car_id in car_ids:
            # 2-5 записей на автомобиль
            num_records = random.randint(2, 5)
            for _ in range(num_records):
                service_type = random.choice([s[0] for s in services_data[:20]])  # популярные услуги
                service_date = datetime.now() - timedelta(days=random.randint(1, 730))
                mileage = random.randint(10000, 150000)
                next_mileage = mileage + random.randint(5000, 15000)
                cost = random.randint(1000, 20000)
                master = random.choice(['Иван Иванов', 'Петр Петров', 'Алексей Смирнов', 'Дмитрий Козлов'])
                notes = random.choice(['', 'Замена по регламенту', 'По рекомендации', 'Срочная замена'])

                cursor.execute("""
                    INSERT INTO service_history 
                    (car_id, service_date, service_type, mileage, next_mileage, cost, master_name, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (car_id, service_date, service_type, mileage, next_mileage, cost, master, notes))
                history_count += 1

        connection.commit()
        print(f"   ✅ Создано {history_count} записей в истории обслуживания")

        # ==================== 7. ЗАПИСИ КЛИЕНТОВ (на будущие даты) ====================
        print("\n📅 Генерация записей клиентов...")

        masters = ['Иван Иванов', 'Петр Петров', 'Алексей Смирнов', 'Дмитрий Козлов']
        times = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
        statuses_app = ['pending', 'confirmed', 'completed', 'cancelled']

        appointments_count = 0
        for _ in range(40):
            client_id = random.choice(clients)
            service_id = random.choice(services_ids)
            car_id = random.choice(car_ids)
            appointment_date = datetime.now().date() + timedelta(days=random.randint(-30, 60))
            appointment_time = random.choice(times)
            master = random.choice(masters)
            status = random.choice(statuses_app)
            notes = random.choice(['', 'Просьба позвонить перед выездом', 'Нужна диагностика', 'Срочно'])

            cursor.execute("""
                INSERT INTO appointments 
                (client_id, car_id, service_id, appointment_date, appointment_time, master_name, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (client_id, car_id, service_id, appointment_date, appointment_time, master, status, notes))
            appointments_count += 1

        connection.commit()
        print(f"   ✅ Создано {appointments_count} записей клиентов")

        # ==================== 8. ПОЛЬЗОВАТЕЛИ ====================
        print("\n👤 Создание пользователей...")

        def hash_password(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        users_data = [
            ('admin', hash_password('admin123'), 'admin', 'Администратор Системы', 'admin@auto_service.ru',
             '+7 999 111-22-33'),
            ('manager', hash_password('manager123'), 'manager', 'Иван Петров', 'manager@auto_service.ru',
             '+7 999 222-33-44'),
            ('master1', hash_password('master123'), 'master', 'Сергей Иванов', 'master1@auto_service.ru',
             '+7 999 333-44-55'),
            ('master2', hash_password('master123'), 'master', 'Алексей Смирнов', 'master2@auto_service.ru',
             '+7 999 444-55-66'),
            ('cashier', hash_password('cashier123'), 'cashier', 'Елена Кузнецова', 'cashier@auto_service.ru',
             '+7 999 555-66-77'),
        ]

        for user in users_data:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email, phone, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, user)

        connection.commit()
        print(f"   ✅ Создано {len(users_data)} пользователей")

        # ==================== 9. ПРАВА ДОСТУПА ====================
        print("\n🔐 Настройка прав доступа...")

        permissions = [
            # Администратор - все права
            ('admin', 'view_clients'), ('admin', 'edit_clients'), ('admin', 'delete_clients'),
            ('admin', 'view_services'), ('admin', 'edit_services'), ('admin', 'delete_services'),
            ('admin', 'view_orders'), ('admin', 'edit_orders'), ('admin', 'delete_orders'),
            ('admin', 'view_finance'), ('admin', 'edit_finance'),
            ('admin', 'view_reports'), ('admin', 'export_reports'),
            ('admin', 'manage_users'), ('admin', 'view_logs'),

            # Менеджер
            ('manager', 'view_clients'), ('manager', 'edit_clients'),
            ('manager', 'view_services'), ('manager', 'edit_services'),
            ('manager', 'view_orders'), ('manager', 'edit_orders'),
            ('manager', 'view_finance'), ('manager', 'view_reports'),
            ('manager', 'export_reports'),

            # Мастер
            ('master', 'view_clients'), ('master', 'view_services'),
            ('master', 'view_orders'), ('master', 'edit_orders'),

            # Кассир
            ('cashier', 'view_clients'), ('cashier', 'view_orders'),
            ('cashier', 'view_finance'), ('cashier', 'edit_finance'),
        ]

        for role, permission in permissions:
            try:
                cursor.execute("INSERT INTO permissions (role, permission) VALUES (%s, %s)", (role, permission))
            except:
                pass

        connection.commit()
        print(f"   ✅ Создано {len(permissions)} прав доступа")

        # ==================== 10. АКТИВНЫЕ СМЕНЫ ====================
        print("\n⏰ Создание смен...")

        # Создаём смены для мастеров за последние 30 дней
        shifts_count = 0
        masters_list = ['master1', 'master2']

        for username in masters_list:
            cursor.execute("SELECT id, full_name FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                user_id, full_name = user

                for day in range(1, 21):  # 20 дней смен
                    shift_start = datetime.now() - timedelta(days=day, hours=random.randint(0, 8))
                    shift_end = shift_start + timedelta(hours=random.randint(4, 10))
                    duration = int((shift_end - shift_start).total_seconds() / 60)
                    status = 'closed'

                    cursor.execute("""
                        INSERT INTO shifts (user_id, username, full_name, role, shift_start, shift_end, duration_minutes, status)
                        VALUES (%s, %s, %s, 'master', %s, %s, %s, %s)
                    """, (user_id, username, full_name, shift_start, shift_end, duration, status))
                    shifts_count += 1

        connection.commit()
        print(f"   ✅ Создано {shifts_count} записей о сменах")

        cursor.close()
        connection.close()

        print("\n" + "=" * 60)
        print("✅ ГЕНЕРАЦИЯ ДАННЫХ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   👥 Клиенты: 20")
        print(f"   🔧 Услуги: 30")
        print(f"   🚗 Автомобили: {len(car_ids)} (привязаны к клиентам)")
        print(f"   📋 Заказы: {len(orders)}")
        print(f"   💰 Доходные операции: {income_count}")
        print(f"   💸 Расходные операции: {expense_count}")
        print(f"   🔧 История обслуживания: {history_count}")
        print(f"   📅 Записи клиентов: {appointments_count}")
        print(f"   👤 Пользователи: {len(users_data)}")
        print(f"   ⏰ Смены: {shifts_count}")
        print("\n🔐 ДАННЫЕ ДЛЯ ВХОДА:")
        print("   👑 admin / admin123 - Администратор")
        print("   📋 manager / manager123 - Менеджер")
        print("   🔧 master1 / master123 - Мастер 1")
        print("   🔧 master2 / master123 - Мастер 2")
        print("   💰 cashier / cashier123 - Кассир")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    reset_and_generate_data()