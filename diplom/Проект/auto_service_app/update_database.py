import mysql.connector
from mysql.connector import Error


def update_database():
    """Добавление новых таблиц для системы авторизации"""

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        print("🔄 Обновление структуры базы данных...")

        # 1. Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Таблица 'users' создана")

        # 2. Таблица сессий (для отслеживания активных сессий)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token VARCHAR(255) NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Таблица 'user_sessions' создана")

        # 3. Таблица прав доступа (детальные права)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role VARCHAR(20) NOT NULL,
                permission VARCHAR(100) NOT NULL,
                UNIQUE KEY unique_role_permission (role, permission)
            )
        ''')
        print("✅ Таблица 'permissions' создана")

        # 4. Таблица действий пользователей (аудит)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action_type VARCHAR(50),
                entity_type VARCHAR(50),
                entity_id INT,
                details TEXT,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        print("✅ Таблица 'user_actions' создана")

        # Добавляем права для ролей
        permissions = [
            # Администратор (все права)
            ('admin', 'view_clients'), ('admin', 'edit_clients'), ('admin', 'delete_clients'),
            ('admin', 'view_services'), ('admin', 'edit_services'), ('admin', 'delete_services'),
            ('admin', 'view_orders'), ('admin', 'edit_orders'), ('admin', 'delete_orders'),
            ('admin', 'view_finance'), ('admin', 'edit_finance'),
            ('admin', 'view_reports'), ('admin', 'export_reports'),
            ('admin', 'manage_users'), ('admin', 'view_logs'),

            # Менеджер (почти все, кроме управления пользователями)
            ('manager', 'view_clients'), ('manager', 'edit_clients'),
            ('manager', 'view_services'), ('manager', 'edit_services'),
            ('manager', 'view_orders'), ('manager', 'edit_orders'),
            ('manager', 'view_finance'), ('manager', 'view_reports'),
            ('manager', 'export_reports'),

            # Мастер (только заказы и услуги)
            ('master', 'view_clients'),
            ('master', 'view_services'),
            ('master', 'view_orders'), ('master', 'edit_orders'),

            # Кассир (только финансы)
            ('cashier', 'view_clients'),
            ('cashier', 'view_orders'),
            ('cashier', 'view_finance'), ('cashier', 'edit_finance'),
        ]

        cursor.executemany('''
            INSERT IGNORE INTO permissions (role, permission)
            VALUES (%s, %s)
        ''', permissions)

        # Добавляем тестовых пользователей
        import hashlib

        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        users = [
            ('admin', hash_password('admin123'), 'admin', 'Администратор Системы', 'admin@auto.ru', '+7 999 111-22-33'),
            ('manager', hash_password('manager123'), 'manager', 'Менеджер Сервиса', 'manager@auto.ru',
             '+7 999 222-33-44'),
            ('master', hash_password('master123'), 'master', 'Главный Мастер', 'master@auto.ru', '+7 999 333-44-55'),
            ('cashier', hash_password('cashier123'), 'cashier', 'Кассир', 'cashier@auto.ru', '+7 999 444-55-66'),
        ]

        cursor.executemany('''
            INSERT IGNORE INTO users (username, password_hash, role, full_name, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', users)

        connection.commit()
        cursor.close()
        connection.close()

        print("\n✅ База данных успешно обновлена!")
        print("\n👥 Тестовые пользователи:")
        print("   Логин: admin    | Пароль: admin123   | Роль: Администратор")
        print("   Логин: manager  | Пароль: manager123 | Роль: Менеджер")
        print("   Логин: master   | Пароль: master123  | Роль: Мастер")
        print("   Логин: cashier  | Пароль: cashier123 | Роль: Кассир")

    except Error as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    update_database()