from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uvicorn

from database import db_manager
from config import Config
from auth import authenticate_user, create_access_token


# ==================== МОДЕЛИ ДАННЫХ ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    address: str = ""


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    duration: int = 60
    category: str = ""


class OrderCreate(BaseModel):
    client_id: int
    service_id: int
    total_amount: float
    status: str = "В работе"
    notes: str = ""


class OrderStatusUpdate(BaseModel):
    status: str
    amount: Optional[float] = None
    category: Optional[str] = None


class FinancialTransactionCreate(BaseModel):
    transaction_date: str
    transaction_type: str
    category: str
    amount: float
    payment_method: str = "cash"
    description: str = ""
    client_id: Optional[int] = None
    order_id: Optional[int] = None


# ==================== СОЗДАНИЕ ПРИЛОЖЕНИЯ ====================

app = FastAPI(title="Auto Service API", version="1.0.0")
security = HTTPBearer()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ЭНДПОИНТЫ ====================

@app.get("/")
async def root():
    return {"status": "ok", "message": "Auto Service API is running", "timestamp": datetime.now().isoformat()}


@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "pong"}


# -------------------- АВТОРИЗАЦИЯ --------------------
@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Авторизация пользователя"""
    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    # Обновляем время последнего входа
    db_manager.execute_query(
        "UPDATE users SET last_login = NOW() WHERE id = %s",
        (user['id'],),
        fetch=False
    )

    # Создаём токен
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username'], "user_id": user['id'], "role": user['role']},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "full_name": user['full_name'],
            "role": user['role']
        }
    }


# -------------------- КЛИЕНТЫ --------------------
@app.get("/api/clients")
async def get_clients():
    """Получение всех клиентов"""
    result = db_manager.execute_query("SELECT * FROM clients ORDER BY id DESC")
    return result


@app.get("/api/clients/{client_id}")
async def get_client(client_id: int):
    """Получение клиента по ID"""
    result = db_manager.execute_query("SELECT * FROM clients WHERE id = %s", (client_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return result[0]


@app.post("/api/clients")
async def create_client(client: ClientCreate):
    """Создание нового клиента"""
    result = db_manager.execute_query(
        "INSERT INTO clients (first_name, last_name, phone, email, address) VALUES (%s, %s, %s, %s, %s)",
        (client.first_name, client.last_name, client.phone, client.email, client.address),
        fetch=False
    )
    return {"id": result.get('last_insert_id'), "message": "Клиент создан"}


@app.delete("/api/clients/{client_id}")
async def delete_client(client_id: int):
    """Удаление клиента"""
    # Проверяем наличие заказов
    orders = db_manager.execute_query("SELECT COUNT(*) as count FROM orders WHERE client_id = %s", (client_id,))
    if orders and orders[0]['count'] > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить клиента с заказами")

    db_manager.execute_query("DELETE FROM clients WHERE id = %s", (client_id,), fetch=False)
    return {"message": "Клиент удален"}


# -------------------- УСЛУГИ --------------------
@app.get("/api/services")
async def get_services():
    """Получение всех услуг"""
    result = db_manager.execute_query("SELECT * FROM services ORDER BY id")
    return result


@app.get("/api/services/{service_id}")
async def get_service(service_id: int):
    """Получение услуги по ID"""
    result = db_manager.execute_query("SELECT * FROM services WHERE id = %s", (service_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return result[0]


@app.post("/api/services")
async def create_service(service: ServiceCreate):
    """Создание новой услуги"""
    result = db_manager.execute_query(
        "INSERT INTO services (name, description, price, duration, category) VALUES (%s, %s, %s, %s, %s)",
        (service.name, service.description, service.price, service.duration, service.category),
        fetch=False
    )
    return {"id": result.get('last_insert_id'), "message": "Услуга создана"}


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int):
    """Удаление услуги"""
    orders = db_manager.execute_query("SELECT COUNT(*) as count FROM orders WHERE service_id = %s", (service_id,))
    if orders and orders[0]['count'] > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить услугу, используемую в заказах")

    db_manager.execute_query("DELETE FROM services WHERE id = %s", (service_id,), fetch=False)
    return {"message": "Услуга удалена"}


# -------------------- ЗАКАЗЫ --------------------
@app.get("/api/orders")
async def get_orders():
    """Получение всех заказов"""
    query = """
        SELECT 
            o.id,
            COALESCE(c.first_name, '') as first_name,
            COALESCE(c.last_name, '') as last_name,
            COALESCE(s.name, 'Неизвестная услуга') as service_name,
            COALESCE(o.status, 'В работе') as status,
            COALESCE(o.total_amount, 0) as total_amount,
            o.order_date,
            COALESCE(o.notes, '') as notes
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        LEFT JOIN services s ON o.service_id = s.id
        ORDER BY o.id DESC
    """
    result = db_manager.execute_query(query)
    return result


@app.post("/api/orders")
async def create_order(order: OrderCreate):
    """Создание нового заказа"""
    result = db_manager.execute_query(
        "INSERT INTO orders (client_id, service_id, total_amount, status, notes) VALUES (%s, %s, %s, %s, %s)",
        (order.client_id, order.service_id, order.total_amount, order.status, order.notes),
        fetch=False
    )
    order_id = result.get('last_insert_id')

    # Если заказ сразу завершен, добавляем финансовую операцию
    if order.status == "Завершено":
        db_manager.execute_query(
            """INSERT INTO financial_transactions 
               (transaction_date, transaction_type, category, amount, order_id, client_id)
               VALUES (CURDATE(), 'income', 'Ремонт автомобилей', %s, %s, %s)""",
            (order.total_amount, order_id, order.client_id),
            fetch=False
        )

    return {"id": order_id, "message": "Заказ создан"}


@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, update: OrderStatusUpdate):
    """Обновление статуса заказа"""
    # Получаем текущий статус
    current = db_manager.execute_query("SELECT status, total_amount, client_id FROM orders WHERE id = %s", (order_id,))
    if not current:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    current_status = current[0]['status']

    # Обновляем статус
    db_manager.execute_query("UPDATE orders SET status = %s WHERE id = %s", (update.status, order_id), fetch=False)

    # Если заказ завершен, добавляем финансовую операцию
    if update.status == "Завершено" and current_status != "Завершено":
        total_amount = update.amount or current[0]['total_amount']
        client_id = current[0]['client_id']
        category = update.category or "Ремонт автомобилей"

        db_manager.execute_query(
            """INSERT INTO financial_transactions 
               (transaction_date, transaction_type, category, amount, order_id, client_id)
               VALUES (CURDATE(), 'income', %s, %s, %s, %s)""",
            (category, total_amount, order_id, client_id),
            fetch=False
        )

    return {"message": f"Статус заказа #{order_id} обновлен"}


@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    """Удаление заказа"""
    db_manager.execute_query("DELETE FROM financial_transactions WHERE order_id = %s", (order_id,), fetch=False)
    db_manager.execute_query("DELETE FROM orders WHERE id = %s", (order_id,), fetch=False)
    return {"message": "Заказ удален"}


# -------------------- ФИНАНСЫ --------------------
@app.get("/api/financial/report")
async def get_financial_report(period_type: str = "month", year: int = None, month: int = None):
    """Получение финансового отчета"""
    current_date = datetime.now()
    if year is None:
        year = current_date.year
    if month is None:
        month = current_date.month

    conditions = []
    params = []

    if period_type == "month":
        conditions.append("YEAR(transaction_date) = %s")
        conditions.append("MONTH(transaction_date) = %s")
        params.extend([year, month])
    elif period_type == "year":
        conditions.append("YEAR(transaction_date) = %s")
        params.append(year)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT 
            transaction_type,
            COALESCE(category, 'Без категории') as category,
            COUNT(*) as count,
            SUM(amount) as total_amount
        FROM financial_transactions
        WHERE {where_clause}
        GROUP BY transaction_type, category
        ORDER BY transaction_type, total_amount DESC
    """

    result = db_manager.execute_query(query, tuple(params))

    total_income = 0
    total_expense = 0

    for row in result:
        if row['transaction_type'] == 'income':
            total_income += row['total_amount']
        else:
            total_expense += row['total_amount']

    return {
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'profit': float(total_income - total_expense),
        'total_transactions': len(result),
        'report_data': result
    }


@app.post("/api/financial/transaction")
async def add_financial_transaction(transaction: FinancialTransactionCreate):
    """Добавление финансовой операции"""
    result = db_manager.execute_query(
        """INSERT INTO financial_transactions 
           (transaction_date, transaction_type, category, description, amount, payment_method, client_id, order_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (transaction.transaction_date, transaction.transaction_type, transaction.category,
         transaction.description, transaction.amount, transaction.payment_method,
         transaction.client_id, transaction.order_id),
        fetch=False
    )
    return {"id": result.get('last_insert_id'), "message": "Операция добавлена"}


# -------------------- СТАТИСТИКА --------------------
@app.get("/api/statistics")
async def get_statistics():
    """Получение общей статистики"""
    stats = {}

    result = db_manager.execute_query("SELECT COUNT(*) as count FROM clients")
    stats['clients_count'] = result[0]['count'] if result else 0

    result = db_manager.execute_query("SELECT COUNT(*) as count FROM services")
    stats['services_count'] = result[0]['count'] if result else 0

    result = db_manager.execute_query("SELECT COUNT(*) as count FROM orders")
    stats['orders_count'] = result[0]['count'] if result else 0

    result = db_manager.execute_query(
        "SELECT SUM(amount) as total FROM financial_transactions WHERE transaction_type = 'income'")
    stats['total_income'] = float(result[0]['total']) if result and result[0]['total'] else 0

    return stats


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    config = Config()
    print("=" * 60)
    print("🚀 ЗАПУСК BACKEND СЕРВЕРА")
    print("=" * 60)
    print(f"📡 Сервер запускается на: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"📚 Документация API: http://{config.SERVER_HOST}:{config.SERVER_PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=True
    )