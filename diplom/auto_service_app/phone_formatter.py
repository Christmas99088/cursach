import tkinter as tk
import re


class PhoneFormatter:
    """Класс для автоматического форматирования номера телефона"""

    @staticmethod
    def format_phone_number(phone_str):
        """Форматирование номера телефона (без виджета)"""
        if not phone_str:
            return "+7"

        # Удаляем все нецифровые символы
        digits = re.sub(r'\D', '', phone_str)

        # Ограничиваем длину (11 цифр для российских номеров)
        if len(digits) > 11:
            digits = digits[:11]

        # Форматируем по маске +7 XXX XXX-XX-XX
        formatted = ""
        if len(digits) > 0:
            # Код страны (всегда +7)
            formatted = "+7"

            if len(digits) > 1:
                # Первые 3 цифры после кода
                formatted += " " + digits[1:4]

                if len(digits) > 4:
                    # Следующие 3 цифры
                    formatted += " " + digits[4:7]

                    if len(digits) > 7:
                        # Следующие 2 цифры
                        formatted += "-" + digits[7:9]

                        if len(digits) > 9:
                            # Последние 2 цифры
                            formatted += "-" + digits[9:11]
        else:
            formatted = "+7"

        return formatted

    @staticmethod
    def on_key_release(event):
        """Обработчик события для поля ввода"""
        widget = event.widget
        if widget:
            # Получаем текущий текст
            phone = widget.get()

            # Форматируем
            formatted = PhoneFormatter.format_phone_number(phone)

            # Обновляем поле, если изменилось
            if phone != formatted:
                # Сохраняем позицию курсора
                cursor_pos = widget.index(tk.INSERT)

                # Обновляем текст
                widget.delete(0, tk.END)
                widget.insert(0, formatted)

                # Восстанавливаем позицию курсора
                new_pos = min(cursor_pos, len(formatted))
                try:
                    widget.icursor(new_pos)
                except:
                    widget.icursor(len(formatted))

    @staticmethod
    def validate_phone(phone):
        """Проверка корректности номера телефона"""
        # Удаляем все нецифровые символы
        digits = re.sub(r'\D', '', phone)

        # Проверяем длину (должно быть 11 цифр)
        if len(digits) != 11:
            return False, f"Номер телефона должен содержать 11 цифр (сейчас {len(digits)})"

        # Проверяем код страны (должен начинаться с 7)
        if digits[0] not in ['7']:
            return False, "Номер должен начинаться с +7"

        return True, "OK"

    @staticmethod
    def clean_phone(phone):
        """Очистка номера телефона (только цифры)"""
        digits = re.sub(r'\D', '', phone)
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        return digits

    @staticmethod
    def create_phone_entry(parent, **kwargs):
        """Создание поля для ввода телефона с автоматическим форматированием"""

        # Создаем поле ввода
        entry = tk.Entry(parent, font=('Arial', 11), width=25, **kwargs)

        # Устанавливаем начальное значение +7
        entry.insert(0, "+7")

        # Привязываем события форматирования
        entry.bind('<KeyRelease>', PhoneFormatter.on_key_release)

        return entry

    @staticmethod
    def format_for_display(phone):
        """Форматирование телефона для отображения в таблице"""
        if not phone:
            return ""
        # Убираем возможный код 8 или 7 в начале
        clean = re.sub(r'\D', '', phone)
        if clean.startswith('8'):
            clean = '7' + clean[1:]
        return PhoneFormatter.format_phone_number(clean)