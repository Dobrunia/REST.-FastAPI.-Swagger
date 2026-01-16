# Asyncio — асинхронное программирование в Python

## Что такое asyncio

Asyncio — это библиотека Python для написания асинхронного кода с использованием синтаксиса async/await. Она позволяет выполнять множество операций ввода-вывода параллельно без создания потоков, что особенно эффективно для сетевых приложений.

## Основные концепции

- **Корутина (coroutine)** — функция, объявленная через `async def`
- **Event Loop** — цикл событий, который управляет выполнением корутин
- **Task** — обёртка для запуска корутины в фоне
- **await** — ключевое слово для ожидания результата корутины

## Базовый синтаксис

```python
import asyncio

async def say_hello():
    print("Привет!")
    await asyncio.sleep(1)  # Неблокирующая пауза
    print("Пока!")

# Запуск корутины
asyncio.run(say_hello())
```

## Параллельное выполнение

### asyncio.gather

```python
async def fetch_data(url, delay):
    await asyncio.sleep(delay)
    return f"Data from {url}"

async def main():
    # Запуск нескольких корутин параллельно
    results = await asyncio.gather(
        fetch_data("api1", 2),
        fetch_data("api2", 1),
        fetch_data("api3", 3),
    )
    print(results)  # Все результаты через 3 секунды, не 6

asyncio.run(main())
```

### asyncio.create_task

```python
async def main():
    # Создание задач для параллельного выполнения
    task1 = asyncio.create_task(fetch_data("api1", 2))
    task2 = asyncio.create_task(fetch_data("api2", 1))

    # Можно делать что-то пока задачи выполняются
    print("Задачи запущены")

    # Получение результатов
    result1 = await task1
    result2 = await task2
```

## Таймауты

```python
async def slow_operation():
    await asyncio.sleep(10)
    return "done"

async def main():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Операция превысила таймаут!")
```

## Асинхронные контекстные менеджеры

```python
class AsyncDatabase:
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

async def main():
    async with AsyncDatabase() as db:
        await db.query("SELECT * FROM users")
```

## Асинхронные итераторы

```python
async def async_generator():
    for i in range(5):
        await asyncio.sleep(0.5)
        yield i

async def main():
    async for value in async_generator():
        print(value)
```

## Синхронизация

### asyncio.Lock

```python
lock = asyncio.Lock()

async def safe_increment(counter):
    async with lock:
        current = counter["value"]
        await asyncio.sleep(0.1)
        counter["value"] = current + 1
```

### asyncio.Semaphore

```python
# Ограничение числа одновременных операций
semaphore = asyncio.Semaphore(3)

async def limited_operation(n):
    async with semaphore:
        print(f"Операция {n} начата")
        await asyncio.sleep(1)
        print(f"Операция {n} завершена")
```

## Работа с aiohttp

```python
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    data = await fetch("https://api.example.com/data")
```

## Частые вопросы

**Когда использовать asyncio вместо threading?**
Asyncio лучше для I/O-bound задач (сеть, файлы). Threading подходит для CPU-bound задач или когда нужна совместимость с синхронным кодом.

**Можно ли вызывать sync функции из async?**
Да, но они заблокируют event loop. Используйте `asyncio.to_thread()` для CPU-bound операций:

```python
result = await asyncio.to_thread(sync_function, arg1, arg2)
```

**Как отладить async код?**
Включите debug mode: `asyncio.run(main(), debug=True)`
