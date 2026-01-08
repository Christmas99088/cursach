class Config:
    """Настройки приложения"""

    # Основные настройки
    APP_TITLE = "🚗 Система учёта автосервиса"
    APP_SIZE = "1200x700"

    # Настройки MySQL
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"  # Ваш пароль MySQL
    MYSQL_DATABASE = "auto_service_db"
    MYSQL_PORT = 3306

    # Цвета интерфейса
    PRIMARY_COLOR = "#2c3e50"  # Тёмно-синий
    SECONDARY_COLOR = "#3498db"  # Синий
    SUCCESS_COLOR = "#27ae60"  # Зелёный
    WARNING_COLOR = "#f39c12"  # Оранжевый
    DANGER_COLOR = "#e74c3c"  # Красный

    # Шрифты
    TITLE_FONT = ("Arial", 16, "bold")
    HEADER_FONT = ("Arial", 14, "bold")
    NORMAL_FONT = ("Arial", 10)
    SMALL_FONT = ("Arial", 8)

    # Размеры
    INPUT_WIDTH = 30
    TABLE_HEIGHT = 15
    BUTTON_WIDTH = 15