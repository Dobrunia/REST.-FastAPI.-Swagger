# Type Hints — аннотации типов в Python

## Что такое Type Hints

Type hints (аннотации типов) — это способ указать ожидаемые типы переменных, аргументов функций и возвращаемых значений. Они не влияют на выполнение кода, но помогают IDE, линтерам и документации.

## Базовый синтаксис

```python
# Переменные
name: str = "John"
age: int = 30
price: float = 19.99
is_active: bool = True

# Функции
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

# Функция без возвращаемого значения
def print_message(msg: str) -> None:
    print(msg)
```

## Коллекции

```python
from typing import List, Dict, Set, Tuple

# Python 3.9+ можно использовать встроенные типы
numbers: list[int] = [1, 2, 3]
mapping: dict[str, int] = {"a": 1, "b": 2}
unique: set[str] = {"a", "b", "c"}
point: tuple[float, float] = (1.0, 2.0)
mixed: tuple[str, int, bool] = ("name", 42, True)

# До Python 3.9
from typing import List, Dict
numbers: List[int] = [1, 2, 3]
mapping: Dict[str, int] = {"a": 1}
```

## Optional и Union

```python
from typing import Optional, Union

# Optional — значение или None
def find_user(user_id: int) -> Optional[User]:
    """Возвращает User или None"""
    return db.get(user_id)

# Union — несколько возможных типов
def process(value: Union[str, int]) -> str:
    return str(value)

# Python 3.10+ синтаксис
def process(value: str | int) -> str:
    return str(value)

def find_user(user_id: int) -> User | None:
    return db.get(user_id)
```

## Callable

```python
from typing import Callable

# Функция как параметр
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# Callable без указания сигнатуры
from typing import Callable
handler: Callable[..., None]  # Любые аргументы, возврат None
```

## TypeVar и Generic

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

def first(items: List[T]) -> T:
    return items[0]

# Generic класс
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# Использование
stack: Stack[int] = Stack()
stack.push(1)
```

## TypedDict

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> None:
    print(data["name"])  # IDE знает, что это str

user: UserDict = {"name": "John", "age": 30, "email": "john@example.com"}
```

## Literal

```python
from typing import Literal

def set_status(status: Literal["active", "inactive", "pending"]) -> None:
    print(f"Status: {status}")

set_status("active")     # OK
set_status("unknown")    # Ошибка mypy
```

## Protocol (структурная типизация)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(obj: Drawable) -> None:
    obj.draw()

# Circle неявно реализует Drawable
render(Circle())  # OK
```

## Проверка типов с mypy

```bash
pip install mypy
mypy script.py
mypy src/ --strict
```

Конфигурация `mypy.ini`:

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_ignores = True
disallow_untyped_defs = True

[mypy-tests.*]
disallow_untyped_defs = False
```

## Частые вопросы

**Влияют ли type hints на производительность?**
Нет, они полностью игнорируются во время выполнения (кроме специальных случаев с `typing.get_type_hints()`).

**Нужны ли type hints везде?**
Рекомендуется для публичных API, библиотек и больших проектов. Для скриптов и прототипов — по желанию.

**Как указать тип self?**

```python
from typing import Self  # Python 3.11+

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self
```

**Как игнорировать ошибку mypy?**

```python
result = untyped_function()  # type: ignore
```
