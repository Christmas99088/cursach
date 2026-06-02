from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
from database import DatabaseManager
from config import Config
import json

# Создаем экземпляр приложения
app = FastAPI(title="Auto Service API", version="1.0.0")

# Настройка CORS для доступа с любого клиента
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
db = DatabaseManager()


# ==================== ЗДОРОВЬЕ СЕРВЕРА ====================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Auto Service API is running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "pong"}


# ==================== КЛИЕНТЫ ====================

@app.get("/api/clients")
async def get_clients():
    """Получение всех клиентов"""
    result = db.execute_query("SELECT * FROM clients ORDER BY id DESC")
    return result


@app.get("/api/clients/{client_id}")
async def get_client(client_id: int):
    """Получение клиента по ID"""
    result = db.execute_query("SELECT * FROM clients WHERE id = %s", (client_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return result[0]


@app.post("/api/clients")
async def create_client(
        first_name: str = Body(...),
        last_name: str = Body(...),
        phone: str = Body(""),
        email: str = Body(""),
        address: str = Body("")
):
    """Создание нового клиента"""
    query = """
        INSERT INTO clients (first_name, last_name, phone, email, address)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = db.execute_query(query, (first_name, last_name, phone, email, address))

    if result and 'last_insert_id' in result[0]:
        client_id = result[0]['last_insert_id']
        return {"id": client_id, "message": "Клиент создан"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось создать клиента")


@app.delete("/api/clients/{client_id}")
async def delete_client(client_id: int):
    """Удаление клиента"""
    # Проверяем наличие заказов
    orders = db.execute_query("SELECT COUNT(*) as count FROM orders WHERE client_id = %s", (client_id,))
    if orders and orders[0]['count'] > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить клиента с существующими заказами")

    result = db.execute_query("DELETE FROM clients WHERE id = %s", (client_id,))
    return {"message": "Клиент удален"}


# ==================== УСЛУГИ ====================

@app.get("/api/services")
async def get_services():
    """Получение всех услуг"""
    result = db.execute_query("SELECT * FROM services ORDER BY id")
    return result


@app.get("/api/services/{service_id}")
async def get_service(service_id: int):
    """Получение услуги по ID"""
    result = db.execute_query("SELECT * FROM services WHERE id = %s", (service_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return result[0]


@app.post("/api/services")
async def create_service(
        name: str = Body(...),
        description: str = Body(""),
        price: float = Body(...),
        duration: int = Body(60),
        category: str = Body("")
):
    """Создание новой услуги"""
    query = """
        INSERT INTO services (name, description, price, duration, category)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = db.execute_query(query, (name, description, price, duration, category))

    if result and 'last_insert_id' in result[0]:
        service_id = result[0]['last_insert_id']
        return {"id": service_id, "message": "Услуга создана"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось создать услугу")


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int):
    """Удаление услуги"""
    # Проверяем использование в заказах
    orders = db.execute_query("SELECT COUNT(*) as count FROM orders WHERE service_id = %s", (service_id,))
    if orders and orders[0]['count'] > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить услугу, используемую в заказах")

    result = db.execute_query("DELETE FROM services WHERE id = %s", (service_id,))
    return {"message": "Услуга удалена"}


# ==================== ЗАКАЗЫ ====================

@app.get("/api/orders")
async def get_orders():
    """Получение всех заказов с информацией о клиентах и услугах"""
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
    result = db.execute_query(query)
    return result


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    """Получение заказа по ID"""
    query = """
        SELECT 
            o.*,
            c.first_name, c.last_name, c.phone,
            s.name as service_name, s.price
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        LEFT JOIN services s ON o.service_id = s.id
        WHERE o.id = %s
    """
    result = db.execute_query(query, (order_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return result[0]


@app.post("/api/orders")
async def create_order(
        client_id: int = Body(...),
        service_id: int = Body(...),
        total_amount: float = Body(...),
        status: str = Body("В работе"),
        notes: str = Body("")
):
    """Создание нового заказа"""
    query = """
        INSERT INTO orders (client_id, service_id, total_amount, status, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = db.execute_query(query, (client_id, service_id, total_amount, status, notes))

    if result and 'last_insert_id' in result[0]:
        order_id = result[0]['last_insert_id']

        # Если заказ сразу завершен, добавляем финансовую операцию
        if status == "Завершено":
            add_financial_query = """
                INSERT INTO financial_transactions 
                (transaction_date, transaction_type, category, amount, order_id, client_id)
                VALUES (CURDATE(), 'income', 'Ремонт автомобилей', %s, %s, %s)
            """
            db.execute_query(add_financial_query, (total_amount, order_id, client_id))

        return {"id": order_id, "message": "Заказ создан"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось создать заказ")


@app.put("/api/orders/{order_id}/status")
async def update_order_status(
        order_id: int,
        status: str = Body(...),
        amount: float = Body(None),
        category: str = Body(None)
):
    """Обновление статуса заказа"""
    # Получаем текущий статус
    current = db.execute_query("SELECT status, total_amount, client_id FROM orders WHERE id = %s", (order_id,))
    if not current:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    current_status = current[0]['status']

    # Обновляем статус
    result = db.execute_query("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))

    # Если заказ завершен и ранее не был завершен, добавляем финансовую операцию
    if status == "Завершено" and current_status != "Завершено":
        total_amount = amount or current[0]['total_amount']
        client_id = current[0]['client_id']
        cat = category or "Ремонт автомобилей"

        add_financial_query = """
            INSERT INTO financial_transactions 
            (transaction_date, transaction_type, category, amount, order_id, client_id)
            VALUES (CURDATE(), 'income', %s, %s, %s, %s)
        """
        db.execute_query(add_financial_query, (cat, total_amount, order_id, client_id))

    return {"message": f"Статус заказа #{order_id} обновлен на '{status}'"}


@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    """Удаление заказа"""
    # Удаляем связанные финансовые операции
    db.execute_query("DELETE FROM financial_transactions WHERE order_id = %s", (order_id,))
    # Удаляем заказ
    result = db.execute_query("DELETE FROM orders WHERE id = %s", (order_id,))
    return {"message": "Заказ удален"}


# ==================== ФИНАНСЫ ====================

@app.get("/api/financial/report")
async def get_financial_report(
        period_type: str = "month",
        year: int = None,
        month: int = None
):
    """Получение финансового отчета"""
    from datetime import datetime

    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

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

    result = db.execute_query(query, tuple(params))

    # Подсчитываем итоги
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
async def add_financial_transaction(
        transaction_date: str = Body(...),
        transaction_type: str = Body(...),
        category: str = Body(...),
        amount: float = Body(...),
        payment_method: str = Body("cash"),
        description: str = Body(""),
        client_id: int = Body(None),
        order_id: int = Body(None)
):
    """Добавление финансовой операции"""
    query = """
        INSERT INTO financial_transactions 
        (transaction_date, transaction_type, category, description, amount, payment_method, client_id, order_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    result = db.execute_query(query, (
    transaction_date, transaction_type, category, description, amount, payment_method, client_id, order_id))

    if result and 'last_insert_id' in result[0]:
        return {"id": result[0]['last_insert_id'], "message": "Операция добавлена"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось добавить операцию")


# ==================== СТАТИСТИКА ====================

@app.get("/api/statistics")
async def get_statistics():
    """Получение общей статистики"""
    stats = {}

    # Количество клиентов
    result = db.execute_query("SELECT COUNT(*) as count FROM clients")
    stats['clients_count'] = result[0]['count'] if result else 0

    # Количество услуг
    result = db.execute_query("SELECT COUNT(*) as count FROM services")
    stats['services_count'] = result[0]['count'] if result else 0

    # Количество заказов
    result = db.execute_query("SELECT COUNT(*) as count FROM orders")
    stats['orders_count'] = result[0]['count'] if result else 0

    # Общий доход
    result = db.execute_query(
        "SELECT SUM(amount) as total FROM financial_transactions WHERE transaction_type = 'income'")
    stats['total_income'] = float(result[0]['total']) if result and result[0]['total'] else 0

    return stats


# ==================== ЗАПУСК СЕРВЕРА ====================

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