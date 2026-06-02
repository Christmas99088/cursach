class Config:
    """Настройки приложения"""

    # URL сервера (измените если сервер на другом компьютере)
    SERVER_URL = "http://localhost:8000"

    # Настройки интерфейса
    APP_TITLE = "🚗 Система учёта автосервиса"
    APP_SIZE = "1200x700"

    # Цвета интерфейса
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    WARNING_COLOR = "#f39c12"
    DANGER_COLOR = "#e74c3c"

    # Шрифты
    TITLE_FONT = ("Arial", 16, "bold")
    HEADER_FONT = ("Arial", 14, "bold")
    NORMAL_FONT = ("Arial", 10)
    SMALL_FONT = ("Arial", 8)

    # Размеры
    INPUT_WIDTH = 30
    TABLE_HEIGHT = 15
    BUTTON_WIDTH = 15