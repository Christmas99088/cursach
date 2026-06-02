import mysql.connector


def fix_permissions():
    """Добавление всех необходимых прав для ролей"""

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='auto_service_db'
        )

        cursor = connection.cursor()

        # Сначала удалим старые права, чтобы избежать дублей
        cursor.execute("DELETE FROM permissions")

        # Полный список прав для всех ролей
        permissions = [
            # Администратор - все права
            ('admin', 'view_clients'), ('admin', 'edit_clients'), ('admin', 'delete_clients'),
            ('admin', 'view_services'), ('admin', 'edit_services'), ('admin', 'delete_services'),
            ('admin', 'view_orders'), ('admin', 'edit_orders'), ('admin', 'delete_orders'),
            ('admin', 'view_finance'), ('admin', 'edit_finance'),
            ('admin', 'view_reports'), ('admin', 'export_reports'),
            ('admin', 'manage_users'), ('admin', 'view_logs'),

            # Менеджер - может всё, кроме удаления и управления пользователями
            ('manager', 'view_clients'), ('manager', 'edit_clients'),
            ('manager', 'view_services'), ('manager', 'edit_services'),
            ('manager', 'view_orders'), ('manager', 'edit_orders'),  # ← ДОБАВЛЕНО edit_orders
            ('manager', 'view_finance'), ('manager', 'view_reports'),
            ('manager', 'export_reports'),

            # Мастер - только просмотр и изменение статуса заказов
            ('master', 'view_clients'),
            ('master', 'view_services'),
            ('master', 'view_orders'), ('master', 'edit_orders'),  # ← edit_orders для смены статуса

            # Кассир - только финансы и просмотр
            ('cashier', 'view_clients'),
            ('cashier', 'view_orders'),
            ('cashier', 'view_finance'), ('cashier', 'edit_finance'),
        ]

        # Добавляем права
        for role, permission in permissions:
            try:
                cursor.execute("INSERT INTO permissions (role, permission) VALUES (%s, %s)",
                               (role, permission))
            except:
                pass

        connection.commit()

        print("✅ Права доступа успешно обновлены!")
        print("\n📋 Добавлены права для:")
        print("   👑 Администратор - полный доступ")
        print("   📋 Менеджер - просмотр и редактирование")
        print("   🔧 Мастер - просмотр и изменение статуса заказов")
        print("   💰 Кассир - финансы и просмотр")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    fix_permissions()