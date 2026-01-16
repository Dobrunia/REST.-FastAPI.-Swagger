# FastAPI — современный веб-фреймворк

## Что такое FastAPI

FastAPI — это современный, быстрый веб-фреймворк для создания API на Python. Он основан на стандартах OpenAPI и JSON Schema, использует Pydantic для валидации данных и поддерживает асинхронное программирование из коробки.

## Основные преимущества

- **Высокая производительность** — на уровне NodeJS и Go
- **Автоматическая документация** — Swagger UI и ReDoc
- **Валидация данных** — через Pydantic
- **Поддержка async/await** — асинхронные эндпоинты
- **Type hints** — подсказки типов везде

## Установка и минимальное приложение

```bash
pip install fastapi uvicorn
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

Запуск:

```bash
uvicorn main:app --reload
```

Документация доступна по адресам:

- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/redoc` — ReDoc

## Pydantic модели

```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    tax: float = 0.0

@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "total": item.price + item.tax}
```

## Query и Path параметры

```python
from fastapi import Query, Path

@app.get("/items/")
def read_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=None, min_length=3)
):
    return {"skip": skip, "limit": limit, "q": q}

@app.get("/items/{item_id}")
def read_item(
    item_id: int = Path(..., ge=1, description="ID товара")
):
    return {"item_id": item_id}
```

## Асинхронные эндпоинты

```python
import asyncio

@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)  # Имитация async операции
    return {"status": "done"}
```

## Зависимости (Dependency Injection)

```python
from fastapi import Depends

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def read_users(db = Depends(get_db)):
    return db.query(User).all()
```

## Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

## Обработка ошибок

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

## Частые вопросы

**Чем FastAPI отличается от Flask?**
FastAPI быстрее, имеет встроенную валидацию через Pydantic, автоматическую документацию и нативную поддержку async/await.

**Как структурировать большой проект?**
Используйте APIRouter для разделения эндпоинтов по модулям:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])
```
