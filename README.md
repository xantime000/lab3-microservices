# Лабораторная работа №3: Документирование и интеграция REST + GraphQL Gateway

Проект представляет собой распределенную микросервисную систему с гибридным доступом к данным: REST API сервисы и агрегирующий GraphQL API Gateway с устранением проблемы N+1 через паттерн DataLoader.

## Структура проекта

- `auth_service/` — REST API сервис аутентификации (регистрация, PBKDF2 хеширование, JWT токены, OpenAPI 3.1 Swagger UI).
- `catalog_service/` — REST API сервис каталога товаров (постраничная пагинация, выборка по ID, пакетная выгрузка ?ids=... для DataLoader).
- `order_service/` — REST API сервис заказов (хранение заказов пользователей с перечнем позиций и количеств).
- `graphql_gateway/` — GraphQL Gateway на Strawberry GraphQL + FastAPI (схема SDL, DataLoader для пакетной выборки без N+1, GraphiQL IDE).
- `openapi/` — экспортированные спецификации OpenAPI в формате YAML.
- `nginx/` — конфигурация Nginx Reverse Proxy (единая точка входа).
- `docker-compose.yml` — оркестрация всех сервисов и шлюза Nginx в контейнерах.
- `run_local.py` — скрипт одновременного локального запуска всех микросервисов на Windows без Docker.
- `test_all.py` — сценарий автоматизированного интеграционного тестирования всех эндпоинтов и GraphQL шлюза.

## Требования

- Python 3.10+
- Зависимости из `requirements.txt` (`fastapi`, `uvicorn`, `strawberry-graphql`, `httpx`, `requests`, `pyjwt`, `passlib`, `pydantic`)
- (Опционально) Docker и Docker Compose

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск

### Вариант 1. Локальный запуск (без Docker)

Запуск всех микросервисов:

```bash
python run_local.py
```

Порты сервисов:
- GraphQL Gateway & IDE: http://localhost:5004/graphql
- Auth Service Swagger UI: http://localhost:5001/docs
- Catalog Service Swagger UI: http://localhost:5002/docs
- Order Service Swagger UI: http://localhost:5003/docs

Запуск проверки:
```bash
python test_all.py
```

### Вариант 2. Запуск через Docker Compose

```bash
docker compose up --build
```

Доступ через единый шлюз Nginx (порт 8080):
- Единая навигационная страница: http://localhost:8080/
- GraphQL Gateway & IDE: http://localhost:8080/graphql
- Документация Auth Service: http://localhost:8080/docs/auth
- Документация Catalog Service: http://localhost:8080/docs/catalog
- Документация Order Service: http://localhost:8080/docs/order

Запуск проверки для Docker:
```bash
python test_all.py docker
```

## Пример запроса GraphQL

Для проверки агрегации заказов и товаров без проблемы N+1 перейдите в интерфейс GraphiQL (http://localhost:5004/graphql) и выполните запрос:

```graphql
query GetUserOrders {
  ordersByUserId(userId: "123") {
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
```
