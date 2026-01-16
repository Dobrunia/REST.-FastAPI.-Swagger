# Pydantic — валидация данных в Python

## Что такое Pydantic

Pydantic — это библиотека для валидации данных и управления настройками с использованием аннотаций типов Python. Она автоматически приводит данные к нужным типам, проверяет ограничения и генерирует понятные сообщения об ошибках.

## Установка

```bash
pip install pydantic
# Для работы с .env файлами
pip install pydantic-settings
```

## Базовые модели

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: datetime = datetime.now()

# Создание из словаря
user = User(id=1, name="John", email="john@example.com")

# Автоматическое приведение типов
user = User(id="1", name="John", email="john@example.com")  # id станет int

# Доступ к данным
print(user.name)
print(user.model_dump())  # В словарь
print(user.model_dump_json())  # В JSON строку
```

## Валидация полей

```python
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Цена должна быть положительной")
    quantity: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_not_contain_digits(cls, v):
        if any(c.isdigit() for c in v):
            raise ValueError("Имя не должно содержать цифры")
        return v.title()
```

## Field параметры

- `default` — значение по умолчанию
- `default_factory` — функция для создания значения по умолчанию
- `alias` — альтернативное имя поля при парсинге
- `gt`, `ge`, `lt`, `le` — числовые ограничения (>, >=, <, <=)
- `min_length`, `max_length` — ограничения длины строк
- `pattern` — regex паттерн для строк

## Вложенные модели

```python
class Address(BaseModel):
    city: str
    street: str
    zip_code: str

class Company(BaseModel):
    name: str
    address: Address
    employees: list["Employee"] = []

class Employee(BaseModel):
    name: str
    position: str
    company: Optional[Company] = None
```

## Настройки приложения

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Автоматически читает из переменных окружения и .env
settings = Settings()
```

## Сериализация

```python
class User(BaseModel):
    id: int
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 1, "password": "secret"}]
        }
    }

user = User(id=1, password="secret")

# Исключение полей
user.model_dump(exclude={"password"})

# Только определённые поля
user.model_dump(include={"id"})

# Исключить None значения
user.model_dump(exclude_none=True)
```

## Обработка ошибок валидации

```python
from pydantic import ValidationError

try:
    user = User(id="not_a_number", name="", email="invalid")
except ValidationError as e:
    print(e.json())  # JSON с описанием ошибок
    for error in e.errors():
        print(f"Поле: {error['loc']}, Ошибка: {error['msg']}")
```

## Частые вопросы

**Чем Pydantic отличается от dataclasses?**
Pydantic выполняет валидацию и приведение типов при создании объекта, dataclasses просто хранят данные. Pydantic также поддерживает сериализацию в JSON и работу с .env файлами.

**Как сделать поле обязательным без значения по умолчанию?**
Используйте `...` (Ellipsis):

```python
name: str = Field(...)
```

**Как игнорировать лишние поля?**

```python
class User(BaseModel):
    model_config = {"extra": "ignore"}  # или "forbid", "allow"
```

**Как сделать модель неизменяемой?**

```python
class User(BaseModel):
    model_config = {"frozen": True}
```
