import mysql.connector


def recreate_tables():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        # Отключаем проверку внешних ключей
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Удаляем таблицы
        print("Удаление старых таблиц...")
        cursor.execute("DROP TABLE IF EXISTS service_reminders")
        cursor.execute("DROP TABLE IF EXISTS service_history")
        cursor.execute("DROP TABLE IF EXISTS client_cars")
        print("✅ Старые таблицы удалены")

        # Создаём таблицу client_cars
        print("Создание таблицы client_cars...")
        cursor.execute('''
            CREATE TABLE client_cars (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                brand VARCHAR(50),
                model VARCHAR(50),
                year INT,
                license_plate VARCHAR(20),
                vin VARCHAR(50),
                color VARCHAR(30),
                engine_type VARCHAR(50),
                transmission VARCHAR(30),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица client_cars создана")

        # Создаём таблицу service_history
        print("Создание таблицы service_history...")
        cursor.execute('''
            CREATE TABLE service_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                order_id INT NULL,
                service_date DATE NOT NULL,
                service_type VARCHAR(100),
                mileage INT,
                next_mileage INT DEFAULT NULL,
                next_service_date DATE DEFAULT NULL,
                parts_used TEXT,
                cost DECIMAL(10,2),
                master_name VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица service_history создана")

        # Создаём таблицу service_reminders
        print("Создание таблицы service_reminders...")
        cursor.execute('''
            CREATE TABLE service_reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                reminder_type VARCHAR(50),
                reminder_date DATE,
                mileage_target INT,
                is_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица service_reminders создана")

        # Включаем проверку обратно
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        connection.commit()
        cursor.close()
        connection.close()

        print("\n✅ Все таблицы успешно пересозданы!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    recreate_tables()