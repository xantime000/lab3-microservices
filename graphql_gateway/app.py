import os
import sys
from typing import List, Optional
import httpx
import strawberry
from strawberry.dataloader import DataLoader
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SERVICE_PORT = int(os.getenv("PORT", "5004"))
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:5003")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:5002")


# ============================================================
# 1. ОПИСАНИЕ ТИПОВ СХЕМЫ GRAPHQL С ПОДРОБНЫМИ DESCRIPTION
# ============================================================

@strawberry.type(description="Сущность товара из сервиса каталога")
class Product:
    id: strawberry.ID = strawberry.field(description="Уникальный идентификатор товара")
    name: str = strawberry.field(description="Наименование товара")
    price: float = strawberry.field(description="Стоимость товара в рублях")


@strawberry.type(description="Элемент заказа, связывающий товар и его количество")
class OrderItem:
    quantity: int = strawberry.field(description="Количество единиц товара в заказе")
    _product_id: strawberry.Private[int]

    @strawberry.field(description="Информация о товаре, загружаемая через DataLoader без проблемы N+1")
    async def product(self, info: strawberry.Info) -> Product:
        # Используем DataLoader из контекста запроса
        loader: DataLoader = info.context["product_loader"]
        return await loader.load(self._product_id)


@strawberry.type(description="Сущность заказа пользователя")
class Order:
    id: strawberry.ID = strawberry.field(description="Уникальный идентификатор заказа")
    userId: strawberry.ID = strawberry.field(description="Идентификатор пользователя, оформившего заказ")
    createdAt: str = strawberry.field(description="Дата и время создания заказа в формате ISO 8601")
    items: List[OrderItem] = strawberry.field(description="Список позиций (товаров) в заказе")


# ============================================================
# 2. РЕАЛИЗАЦИЯ DATALOADER ДЛЯ РЕШЕНИЯ ПРОБЛЕМЫ N+1
# ============================================================

async def batch_load_products(keys: List[int]) -> List[Optional[Product]]:
    """
    Пакетная функция DataLoader:
    Принимает список всех ID товаров (keys), запрошенных во всех элементах заказов.
    Выполняет ОДИН пакетный HTTP-запрос к Catalog Service REST API вместо N запросов!
    """
    if not keys:
        return []

    # Убираем дубликаты для запроса, но сохраняем исходный порядок для возврата
    unique_ids = list(set(keys))
    ids_param = ",".join(str(k) for k in unique_ids)
    url = f"{CATALOG_SERVICE_URL}/api/catalog/products?ids={ids_param}"

    print(f"[DataLoader] Пакетная загрузка товаров для ID: {unique_ids} (всего запросов в батче: {len(keys)})")

    products_map = {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    products_map[item["id"]] = Product(
                        id=strawberry.ID(str(item["id"])),
                        name=item["name"],
                        price=float(item["price"])
                    )
            else:
                print(f"[DataLoader Error] Catalog Service вернул {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[DataLoader Exception] Ошибка подключения к Catalog Service: {e}")

    # DataLoader требует вернуть список объектов в строго том же порядке, что и входные keys!
    result = []
    for k in keys:
        if k in products_map:
            result.append(products_map[k])
        else:
            # Фолбэк, если товар не найден
            result.append(Product(
                id=strawberry.ID(str(k)),
                name=f"Товар #{k} (нет в каталоге)",
                price=0.0
            ))
    return result


# ============================================================
# 3. КОРНЕВОЙ QUERY С РЕЗОЛВЕРОМ АГРЕГАЦИИ ДАННЫХ
# ============================================================

@strawberry.type(description="Корневые запросы GraphQL Gateway")
class Query:
    @strawberry.field(description="Получение всех заказов пользователя с деталями товаров (агрегация Order + Catalog)")
    async def ordersByUserId(self, userId: strawberry.ID) -> List[Order]:
        """
        Резолвер заказов пользователя:
        1. Запрашивает массив заказов из REST API Order Service по userId
        2. Формирует структуру Order и OrderItem
        3. Детали товаров подгружаются лениво через DataLoader при обращении к полю product
        """
        url = f"{ORDER_SERVICE_URL}/api/orders?userId={userId}"
        raw_orders = []

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    raw_orders = resp.json()
                else:
                    print(f"[Order Service Error] Статус: {resp.status_code}")
        except Exception as e:
            print(f"[Order Service Exception] Ошибка подключения: {e}")

        orders_list: List[Order] = []
        for o in raw_orders:
            order_items: List[OrderItem] = []
            for item in o.get("items", []):
                order_items.append(OrderItem(
                    quantity=int(item["quantity"]),
                    _product_id=int(item["productId"])
                ))

            orders_list.append(Order(
                id=strawberry.ID(str(o["id"])),
                userId=strawberry.ID(str(o["userId"])),
                createdAt=str(o["createdAt"]),
                items=order_items
            ))

        return orders_list


try:
    from .ide import get_ide_html
except ImportError:
    from ide import get_ide_html


# ============================================================
# 4. СОЗДАНИЕ СХЕМЫ И FASTAPI ПРИЛОЖЕНИЯ
# ============================================================

# Интроспекция (introspection=True) включена по требованию Шага 3
schema = strawberry.Schema(query=Query)


async def get_context():
    """Контекст создается индивидуально для каждого GraphQL-запроса с новым экземпляром DataLoader"""
    return {
        "product_loader": DataLoader(load_fn=batch_load_products)
    }


class StandaloneGraphQLRouter(GraphQLRouter):
    """
    Автономный роутер со встроенным GraphQL Playground без внешних CDN.
    Исключает зависание на 'Loading...' при закрытом или медленном доступе к unpkg.com.
    """
    async def render_graphql_ide(self, request) -> HTMLResponse:
        return HTMLResponse(get_ide_html())


# Подключаем GraphQLRouter со встроенным надежным Playground по пути /graphql
graphql_app = StandaloneGraphQLRouter(
    schema,
    context_getter=get_context
)

app = FastAPI(
    title="GraphQL API Gateway",
    description="GraphQL шлюз, объединяющий сервисы Order и Catalog с решением проблемы N+1 через DataLoader",
    version="1.0.0"
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/playground", response_class=HTMLResponse, include_in_schema=False)
def playground_page():
    return HTMLResponse(get_ide_html())


@app.get("/health")
def health():
    return {"status": "ok", "service": "graphql-gateway"}


@app.get("/")
def index():
    return RedirectResponse(url="/graphql")


if __name__ == "__main__":
    import uvicorn
    print(f"Запуск GraphQL Gateway на порту {SERVICE_PORT}...")
    print(f"GraphQL Playground доступен по адресу: http://localhost:{SERVICE_PORT}/graphql")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
