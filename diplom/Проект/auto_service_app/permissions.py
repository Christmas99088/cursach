from functools import wraps
from tkinter import messagebox

def require_permission(permission):
    """Декоратор для проверки прав доступа"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'user_manager') and self.user_manager.current_user:
                if self.user_manager.check_permission(permission):
                    return func(self, *args, **kwargs)
                else:
                    messagebox.showerror("Доступ запрещен",
                                        f"У вас нет права на выполнение этого действия.\n"
                                        f"Требуется право: {permission}")
                    return None
            else:
                messagebox.showerror("Ошибка", "Пользователь не авторизован")
                return None
        return wrapper
    return decorator

def require_role(allowed_roles):
    """Декоратор для проверки роли"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'user_manager') and self.user_manager.current_user:
                if self.user_manager.current_user['role'] in allowed_roles:
                    return func(self, *args, **kwargs)
                else:
                    messagebox.showerror("Доступ запрещен",
                                        f"Доступ только для ролей: {', '.join(allowed_roles)}")
                    return None
            else:
                messagebox.showerror("Ошибка", "Пользователь не авторизован")
                return None
        return wrapper
    return decorator