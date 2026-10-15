import os
import sys
from typing import List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI, Query
from pydantic import BaseModel

SERVICE_PORT = int(os.getenv("PORT", "5003"))

# База данных заказов: каждый заказ содержит список товаров (только productId и quantity)
orders_db = [
    {
        "id": "ord-101",
        "userId": "123",
        "createdAt": "2026-10-10T14:30:00Z",
        "items": [
            {"productId": 1, "quantity": 1},  # Игровой ноутбук
            {"productId": 2, "quantity": 2},  # Беспроводная мышь
        ]
    },
    {
        "id": "ord-102",
        "userId": "123",
        "createdAt": "2026-10-12T18:15:00Z",
        "items": [
            {"productId": 2, "quantity": 1},  # Беспроводная мышь (повторяется!)
            {"productId": 5, "quantity": 1},  # Наушники HyperX
        ]
    },
    {
        "id": "ord-103",
        "userId": "456",
        "createdAt": "2026-10-14T09:00:00Z",
        "items": [
            {"productId": 3, "quantity": 1},  # Клавиатура
            {"productId": 4, "quantity": 1},  # Монитор
        ]
    }
]

app = FastAPI(
    title="Order Service REST API",
    description="Сервис управления заказами пользователей",
    version="1.0.0",
    docs_url="/docs"
)


class OrderItemRaw(BaseModel):
    productId: int
    quantity: int


class OrderRaw(BaseModel):
    id: str
    userId: str
    createdAt: str
    items: List[OrderItemRaw]


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "order-service"}


@app.get(
    "/api/orders",
    response_model=List[OrderRaw],
    summary="Получение заказов пользователя",
    tags=["Orders"]
)
def get_orders(userId: Optional[str] = Query(None, description="ID пользователя")):
    if userId:
        return [o for o in orders_db if o["userId"] == str(userId)]
    return orders_db


if __name__ == "__main__":
    import uvicorn
    print(f"Запуск Order Service на порту {SERVICE_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
