import requests
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000/api"


def log_request(method, url, params=None, body=None, response=None, error=None):
    """Логирование запроса"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "url": url,
        "params": params,
        "body": body,
        "status_code": response.status_code if response else None,
        "content_type": response.headers.get("Content-Type") if response else None,
        "response": response.text if response else None,
        "error": str(error) if error else None
    }
    return log_entry


def safe_request(method, url, **kwargs):
    """Выполнение запроса с обработкой ошибок"""
    try:
        # Извлекаем параметры для логирования
        params = kwargs.get('params')
        body = kwargs.get('json')

        if method == 'GET':
            response = requests.get(url, timeout=10, **kwargs)
        elif method == 'POST':
            response = requests.post(url, timeout=10, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, timeout=10, **kwargs)
        elif method == 'PATCH':
            response = requests.patch(url, timeout=10, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10, **kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")

        response.raise_for_status()
        log_entry = log_request(method, url, params=params, body=body, response=response)
        logger.info(f"{method} {url} - Status: {response.status_code}")
        return response, log_entry

    except requests.exceptions.Timeout:
        logger.error(f"Timeout: {method} {url}")
        log_entry = log_request(method, url, error="Timeout")
        return None, log_entry

    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {method} {url}")
        log_entry = log_request(method, url, error="ConnectionError")
        return None, log_entry

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {method} {url} - {e}")
        log_entry = log_request(method, url, error=str(e))
        return None, log_entry

    except Exception as e:
        logger.error(f"Unexpected error: {method} {url} - {e}")
        log_entry = log_request(method, url, error=str(e))
        return None, log_entry


def test_crud():
    """Тестирование CRUD операций"""
    print("\n" + "=" * 60)
    print("ЭТАП B: REST API CRUD")
    print("=" * 60)

    all_logs = []

    # 1. GET - получить все записи
    print("\n1. GET /api/items")
    response, log = safe_request('GET', f"{BASE_URL}/items")
    all_logs.append(log)
    if response:
        print(f"Найдено записей: {len(response.json())}")
        print(f"Первая запись: {response.json()[0] if response.json() else 'Нет записей'}")

    # 2. POST - создать новую запись
    print("\n2. POST /api/items")
    new_item = {
        "name": "Новый товар",
        "category": "Электроника",
        "value": 999.99,
        "updated_at": "2024-12-01",
        "active": True
    }
    response, log = safe_request('POST', f"{BASE_URL}/items", json=new_item)
    all_logs.append(log)
    created_id = None
    if response:
        result = response.json()
        created_id = result.get('id')
        print(f"Создан товар с id: {created_id}")

    if created_id:
        # 3. PUT - полное обновление
        print(f"\n3. PUT /api/items/{created_id}")
        updated_item = {
            "name": "Обновленный товар",
            "category": "Бытовая техника",
            "value": 1500.00,
            "updated_at": "2024-12-15",
            "active": False
        }
        response, log = safe_request('PUT', f"{BASE_URL}/items/{created_id}", json=updated_item)
        all_logs.append(log)
        if response:
            print(f"Товар {created_id} полностью обновлен")

        # 4. PATCH - частичное обновление
        print(f"\n4. PATCH /api/items/{created_id}")
        patch_data = {
            "value": 2000.00,
            "active": True
        }
        response, log = safe_request('PATCH', f"{BASE_URL}/items/{created_id}", json=patch_data)
        all_logs.append(log)
        if response:
            print(f"Товар {created_id} частично обновлен")

        # 5. GET - получить конкретную запись
        print(f"\n5. GET /api/items/{created_id}")
        response, log = safe_request('GET', f"{BASE_URL}/items/{created_id}")
        all_logs.append(log)
        if response:
            print(f"Получен товар: {response.json()}")

        # 6. DELETE - удалить запись
        print(f"\n6. DELETE /api/items/{created_id}")
        response, log = safe_request('DELETE', f"{BASE_URL}/items/{created_id}")
        all_logs.append(log)
        if response:
            print(f"Товар {created_id} удален")

        # 7. GET - проверить что удалено
        print(f"\n7. GET /api/items/{created_id} (проверка удаления)")
        response, log = safe_request('GET', f"{BASE_URL}/items/{created_id}")
        all_logs.append(log)
        if response is None:
            print(f"Товар {created_id} успешно удален (404)")

    # Сохранение логов
    Path('results').mkdir(parents=True, exist_ok=True)
    log_df = pd.DataFrame(all_logs)
    log_df.to_csv('results/api_log.csv', index=False, encoding='utf-8-sig')
    print("\nЛоги сохранены в results/api_log.csv")

    return all_logs


def test_error_handling():
    """Тестирование обработки ошибок"""
    print("\n" + "=" * 60)
    print("ЭТАП C: ОБРАБОТКА ОШИБОК")
    print("=" * 60)

    print("\n1. Несуществующий id (404)")
    response, log = safe_request('GET', f"{BASE_URL}/items/99999")
    print(f"Результат: {response is None}")

    print("\n2. Ошибка соединения (неправильный порт)")
    response, log = safe_request('GET', "http://127.0.0.1:9999/api/items")
    print(f"Результат: {response is None}")

    print("\n3. Timeout (маленький таймаут)")
    try:
        response = requests.get(f"{BASE_URL}/items", timeout=0.001)
    except Exception as e:
        print(f"Timeout пойман: {type(e).__name__}")


if __name__ == "__main__":
    print("=" * 60)
    print("ВНИМАНИЕ: Убедись что backend.py запущен!")
    print("=" * 60)
    test_crud()
    test_error_handling()