import os
import sys
import time
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

processes = []

def start_service(name, script_path, env_vars=None):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    if env_vars:
        env.update(env_vars)
    
    print(f"[Запуск] {name}...")
    p = subprocess.Popen(
        [PYTHON_EXE, script_path],
        cwd=os.path.dirname(script_path),
        env=env
    )
    processes.append((name, p))
    return p

def main():
    print("=" * 65)
    print("  ЗАПУСК ЛАБОРАТОРНОЙ РАБОТЫ №3: REST + GRAPHQL GATEWAY")
    print("  Режим: Локальный запуск на Windows (без Docker)")
    print("=" * 65)

    try:
        # 1. Auth Service (порт 5001)
        start_service(
            "Auth Service",
            os.path.join(CURRENT_DIR, "auth_service", "app.py"),
            {"PORT": "5001"}
        )

        # 2. Catalog Service (порт 5002)
        start_service(
            "Catalog Service",
            os.path.join(CURRENT_DIR, "catalog_service", "app.py"),
            {"PORT": "5002"}
        )

        # 3. Order Service (порт 5003)
        start_service(
            "Order Service",
            os.path.join(CURRENT_DIR, "order_service", "app.py"),
            {"PORT": "5003"}
        )

        time.sleep(2)

        # 4. GraphQL Gateway (порт 5004)
        start_service(
            "GraphQL Gateway",
            os.path.join(CURRENT_DIR, "graphql_gateway", "app.py"),
            {
                "PORT": "5004",
                "ORDER_SERVICE_URL": "http://127.0.0.1:5003",
                "CATALOG_SERVICE_URL": "http://127.0.0.1:5002"
            }
        )

        time.sleep(2)
        print("\n" + "=" * 65)
        print("  ВСЕ СЕРВИСЫ УСПЕШНО ЗАПУЩЕНЫ!")
        print("=" * 65)
        print("  -> GraphQL Gateway & IDE: http://localhost:5004/graphql")
        print("  -> Auth Service Swagger:  http://localhost:5001/docs")
        print("  -> Catalog Service Swagger: http://localhost:5002/docs")
        print("  -> Order Service Swagger: http://localhost:5003/docs")
        print("=" * 65)
        print("  Для проверки запустите автотест: python test_all.py")
        print("  Для остановки всех сервисов нажмите Ctrl + C")
        print("=" * 65 + "\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nОстановка всех сервисов...")
        for name, p in processes:
            print(f"Останавливаю {name}...")
            p.terminate()
        print("Все сервисы остановлены.")

if __name__ == "__main__":
    main()
