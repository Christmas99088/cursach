import mysql.connector


def update_service_history_table():
    """Добавление недостающих колонок в таблицу service_history"""

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        # Проверяем и добавляем колонку next_mileage
        try:
            cursor.execute("ALTER TABLE service_history ADD COLUMN next_mileage INT DEFAULT NULL")
            print("✅ Добавлена колонка 'next_mileage'")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("ℹ️ Колонка 'next_mileage' уже существует")
            else:
                print(f"⚠️ {e}")

        # Проверяем и добавляем колонку next_service_date
        try:
            cursor.execute("ALTER TABLE service_history ADD COLUMN next_service_date DATE DEFAULT NULL")
            print("✅ Добавлена колонка 'next_service_date'")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("ℹ️ Колонка 'next_service_date' уже существует")
            else:
                print(f"⚠️ {e}")

        # Проверяем и добавляем колонку parts_used
        try:
            cursor.execute("ALTER TABLE service_history ADD COLUMN parts_used TEXT DEFAULT NULL")
            print("✅ Добавлена колонка 'parts_used'")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("ℹ️ Колонка 'parts_used' уже существует")
            else:
                print(f"⚠️ {e}")

        connection.commit()
        cursor.close()
        connection.close()

        print("\n✅ Таблица service_history успешно обновлена!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    update_service_history_table()