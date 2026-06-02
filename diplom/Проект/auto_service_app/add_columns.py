import mysql.connector


def add_columns():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        # Проверяем и добавляем колонки
        cursor.execute("SHOW COLUMNS FROM service_history")
        existing_columns = [col[0] for col in cursor.fetchall()]

        if 'next_mileage' not in existing_columns:
            cursor.execute("ALTER TABLE service_history ADD COLUMN next_mileage INT DEFAULT NULL")
            print("✅ Добавлена колонка next_mileage")

        if 'next_service_date' not in existing_columns:
            cursor.execute("ALTER TABLE service_history ADD COLUMN next_service_date DATE DEFAULT NULL")
            print("✅ Добавлена колонка next_service_date")

        if 'parts_used' not in existing_columns:
            cursor.execute("ALTER TABLE service_history ADD COLUMN parts_used TEXT DEFAULT NULL")
            print("✅ Добавлена колонка parts_used")

        connection.commit()
        cursor.close()
        connection.close()

        print("\n✅ Все колонки добавлены!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    add_columns()