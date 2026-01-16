# HTTP-запросы в Python

## Библиотека requests

Requests — самая популярная библиотека для HTTP-запросов в Python. Она проста в использовании и поддерживает все необходимые функции.

```bash
pip install requests
```

## Основные методы

```python
import requests

# GET запрос
response = requests.get("https://api.example.com/users")

# POST запрос
response = requests.post(
    "https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)

# PUT запрос
response = requests.put(
    "https://api.example.com/users/1",
    json={"name": "John Updated"}
)

# DELETE запрос
response = requests.delete("https://api.example.com/users/1")

# PATCH запрос
response = requests.patch(
    "https://api.example.com/users/1",
    json={"email": "new@example.com"}
)
```

## Работа с ответом

```python
response = requests.get("https://api.example.com/data")

# Статус код
print(response.status_code)  # 200

# Проверка успешности
response.raise_for_status()  # Исключение если не 2xx

# Тело ответа
print(response.text)         # Как строка
print(response.json())       # Как JSON (словарь)
print(response.content)      # Как bytes

# Заголовки
print(response.headers)
print(response.headers["Content-Type"])

# Время ответа
print(response.elapsed.total_seconds())
```

## Параметры запроса

```python
# Query параметры
response = requests.get(
    "https://api.example.com/search",
    params={"q": "python", "page": 1, "limit": 10}
)
# URL: https://api.example.com/search?q=python&page=1&limit=10

# Заголовки
response = requests.get(
    "https://api.example.com/data",
    headers={
        "Authorization": "Bearer token123",
        "Accept": "application/json"
    }
)

# Таймаут
response = requests.get(
    "https://api.example.com/data",
    timeout=5  # секунды
)

# Cookies
response = requests.get(
    "https://api.example.com/data",
    cookies={"session_id": "abc123"}
)
```

## Отправка данных

```python
# JSON
response = requests.post(
    "https://api.example.com/users",
    json={"name": "John"}  # Автоматически сериализует и ставит Content-Type
)

# Form data
response = requests.post(
    "https://api.example.com/login",
    data={"username": "john", "password": "secret"}
)

# Загрузка файла
with open("photo.jpg", "rb") as f:
    response = requests.post(
        "https://api.example.com/upload",
        files={"image": f}
    )
```

## Сессии

```python
# Переиспользование соединений и cookies
with requests.Session() as session:
    session.headers.update({"Authorization": "Bearer token"})

    response1 = session.get("https://api.example.com/users")
    response2 = session.get("https://api.example.com/posts")
```

## Асинхронные запросы с aiohttp

```python
import aiohttp
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Запуск
data = asyncio.run(fetch("https://api.example.com/data"))
```

## Обработка ошибок

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

try:
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    data = response.json()
except Timeout:
    print("Превышено время ожидания")
except ConnectionError:
    print("Ошибка соединения")
except HTTPError as e:
    print(f"HTTP ошибка: {e.response.status_code}")
except requests.RequestException as e:
    print(f"Ошибка запроса: {e}")
```

## Частые вопросы

**Как работать с API, требующим авторизации?**

```python
# Bearer token
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Basic auth
from requests.auth import HTTPBasicAuth
response = requests.get(url, auth=HTTPBasicAuth("user", "pass"))
```

**Как отключить проверку SSL?**

```python
response = requests.get(url, verify=False)  # Не рекомендуется для production
```

**requests vs aiohttp — что выбрать?**

- `requests` — для синхронного кода, простых скриптов
- `aiohttp` — для асинхронных приложений, параллельных запросов

**Как сделать retry при ошибках?**

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
```
