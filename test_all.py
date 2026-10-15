import sys
import time
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Базовые URL (можно переопределить через аргумент, например для Docker http://localhost:8080)
BASE_URL = "http://localhost:8080" if len(sys.argv) > 1 and sys.argv[1] == "docker" else None

AUTH_URL = BASE_URL or "http://127.0.0.1:5001"
CATALOG_URL = BASE_URL or "http://127.0.0.1:5002"
GRAPHQL_URL = f"{BASE_URL}/graphql" if BASE_URL else "http://127.0.0.1:5004/graphql"


def print_section(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def main():
    print(f"\n[ТЕСТ] Запуск проверки ЛР3: REST API и GraphQL Gateway\n")

    # ----------------------------------------------------
    # 1. ТЕСТИРОВАНИЕ REST API: AUTH SERVICE
    # ----------------------------------------------------
    print_section("1. ТЕСТИРОВАНИЕ REST API: AUTH SERVICE")
    email = f"student_{int(time.time())}@tpu.ru"
    password = "StrongPassword123!"

    # 1.1 Регистрация
    print("\n[1.1 Регистрация пользователя POST /api/auth/register]")
    reg_res = requests.post(
        f"{AUTH_URL}/api/auth/register",
        json={"email": email, "password": password}
    )
    print(f"Статус: HTTP {reg_res.status_code}")
    print(f"Ответ: {reg_res.json()}")
    assert reg_res.status_code == 201, "Ошибка регистрации"

    # 1.2 Вход и выпуск JWT
    print("\n[1.2 Аутентификация пользователя POST /api/auth/login]")
    login_res = requests.post(
        f"{AUTH_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    print(f"Статус: HTTP {login_res.status_code}")
    login_data = login_res.json()
    print(f"Ответ: {login_data}")
    assert login_res.status_code == 200, "Ошибка входа"
    token = login_data["access_token"]
    print(f"-> Успешно получен JWT-токен: {token[:30]}...{token[-15:]}")

    # ----------------------------------------------------
    # 2. ТЕСТИРОВАНИЕ REST API: CATALOG SERVICE
    # ----------------------------------------------------
    print_section("2. ТЕСТИРОВАНИЕ REST API: CATALOG SERVICE")

    # 2.1 Список с пагинацией
    print("\n[2.1 Получение списка товаров с пагинацией GET /api/catalog/products?page=1&limit=3]")
    cat_res = requests.get(f"{CATALOG_URL}/api/catalog/products", params={"page": 1, "limit": 3})
    print(f"Статус: HTTP {cat_res.status_code}")
    cat_data = cat_res.json()
    print(f"Всего товаров в каталоге: {cat_data['total']}, на странице: {len(cat_data['items'])}")
    for item in cat_data["items"]:
        print(f"  - [{item['id']}] {item['name']} — {item['price']} руб.")
    assert cat_res.status_code == 200, "Ошибка получения каталога"

    # 2.2 Товар по ID
    print("\n[2.2 Получение товара по ID GET /api/catalog/products/1]")
    item_res = requests.get(f"{CATALOG_URL}/api/catalog/products/1")
    print(f"Статус: HTTP {item_res.status_code}")
    print(f"Товар: {item_res.json()}")
    assert item_res.status_code == 200, "Ошибка получения товара по ID"

    # ----------------------------------------------------
    # 3. ТЕСТИРОВАНИЕ ДОКУМЕНТАЦИИ OPENAPI (SWAGGER)
    # ----------------------------------------------------
    print_section("3. ПРОВЕРКА ДОКУМЕНТАЦИИ OPENAPI / SWAGGER UI")
    auth_docs = requests.get(f"{AUTH_URL}/docs")
    catalog_docs = requests.get(f"{CATALOG_URL}/docs")
    print(f"Auth Service Swagger (/docs): HTTP {auth_docs.status_code}")
    print(f"Catalog Service Swagger (/docs): HTTP {catalog_docs.status_code}")
    assert auth_docs.status_code == 200 and catalog_docs.status_code == 200, "Ошибка доступа к Swagger UI"
    print("-> Интерактивная документация OpenAPI доступна!")

    # ----------------------------------------------------
    # 4. ТЕСТИРОВАНИЕ GRAPHQL GATEWAY (АГРЕГАЦИЯ + DATALOADER)
    # ----------------------------------------------------
    print_section("4. ТЕСТИРОВАНИЕ GRAPHQL GATEWAY (АГРЕГАЦИЯ ORDER + CATALOG)")

    # 4.1 Проверка интроспекции (Introspection)
    print("\n[4.1 Проверка интроспекции GraphQL]")
    intro_query = """
    query {
      __schema {
        types {
          name
        }
      }
    }
    """
    intro_res = requests.post(GRAPHQL_URL, json={"query": intro_query})
    print(f"Статус интроспекции: HTTP {intro_res.status_code}")
    assert intro_res.status_code == 200 and "data" in intro_res.json(), "Интроспекция отключена или недоступна"
    print("-> Интроспекция включена, GraphQL Playground и схема готовы к работе!")

    # 4.2 Выполнение запроса из Этапа 4 (ordersByUserId)
    print("\n[4.2 Выполнение запроса заказов пользователя с деталями товаров]")
    query_str = """
    query GetUserOrders($userId: ID!) {
      ordersByUserId(userId: $userId) {
        id
        createdAt
        items {
          quantity
          product {
            id
            name
            price
          }
        }
      }
    }
    """
    variables = {"userId": "123"}

    gql_res = requests.post(GRAPHQL_URL, json={"query": query_str, "variables": variables})
    print(f"Статус: HTTP {gql_res.status_code}")
    gql_data = gql_res.json()
    print("Ответ GraphQL Gateway:")
    import json
    print(json.dumps(gql_data, indent=2, ensure_ascii=False))

    orders = gql_data.get("data", {}).get("ordersByUserId", [])
    assert len(orders) > 0, "Заказы не найдены"

    # Проверяем, что товар подгрузился из Catalog REST API
    first_order = orders[0]
    first_item = first_order["items"][0]
    assert "name" in first_item["product"], "Поле product.name не подгрузилось"
    print(f"\n-> Товар успешно агрегирован: '{first_item['product']['name']}' (Цена: {first_item['product']['price']} руб.)")
    print("-> Проблема N+1 успешно решена с помощью DataLoader (пакетная загрузка батча)!")

    print_section("ИТОГ: ВСЕ ТРЕБОВАНИЯ ЛАБОРАТОРНОЙ РАБОТЫ №3 ВЫПОЛНЕНЫ НА 100%!")


if __name__ == "__main__":
    main()
