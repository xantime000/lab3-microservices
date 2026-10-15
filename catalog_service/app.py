import os
import sys
from typing import List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

SERVICE_PORT = int(os.getenv("PORT", "5002"))

# Начальная база данных товаров
products_db = {
    1: {"id": 1, "name": "Игровой ноутбук ASUS ROG", "price": 125000.0, "category": "Компьютеры"},
    2: {"id": 2, "name": "Беспроводная мышь Logitech G Pro", "price": 8500.0, "category": "Периферия"},
    3: {"id": 3, "name": "Механическая клавиатура Dark Project", "price": 9200.0, "category": "Периферия"},
    4: {"id": 4, "name": "Монитор 27'' IPS 165Hz", "price": 32000.0, "category": "Мониторы"},
    5: {"id": 5, "name": "Игровые наушники HyperX Cloud", "price": 11500.0, "category": "Аудио"},
    6: {"id": 6, "name": "Коврик для мыши XXL", "price": 1800.0, "category": "Аксессуары"},
    7: {"id": 7, "name": "SSD NVMe M.2 1TB", "price": 9800.0, "category": "Комплектующие"},
    8: {"id": 8, "name": "Оперативная память DDR5 32GB", "price": 14200.0, "category": "Комплектующие"},
}

app = FastAPI(
    title="Catalog Service REST API",
    description="Сервис товарного каталога с пагинацией и поиском по ID",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

@app.get("/api-docs", include_in_schema=False)
def api_docs_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str


class ProductListResponse(BaseModel):
    items: List[Product]
    total: int
    page: int
    limit: int
    total_pages: int


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "catalog-service"}


@app.get(
    "/api/catalog/products",
    response_model=ProductListResponse,
    summary="Получение списка товаров с пагинацией",
    tags=["Catalog"]
)
def get_products(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество товаров на странице"),
    ids: Optional[str] = Query(None, description="Список ID через запятую для пакетной выборки (например: 1,3,5)")
):
    all_items = list(products_db.values())

    # Если передан список конкретных ID (для пакетной выборки DataLoader/REST)
    if ids:
        try:
            target_ids = set(int(x.strip()) for x in ids.split(",") if x.strip())
            filtered = [p for p in all_items if p["id"] in target_ids]
            return ProductListResponse(
                items=filtered,
                total=len(filtered),
                page=1,
                limit=len(filtered) or 1,
                total_pages=1
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат параметра ids")

    total = len(all_items)
    start = (page - 1) * limit
    end = start + limit
    paginated_items = all_items[start:end]
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return ProductListResponse(
        items=paginated_items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@app.get(
    "/api/catalog/products/{product_id}",
    response_model=Product,
    summary="Получение информации о товаре по ID",
    tags=["Catalog"]
)
def get_product_by_id(product_id: int):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с id={product_id} не найден"
        )
    return product


if __name__ == "__main__":
    import uvicorn
    print(f"Запуск Catalog Service на порту {SERVICE_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
