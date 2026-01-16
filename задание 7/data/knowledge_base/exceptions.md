# Exceptions — обработка исключений в Python

## Что такое исключения

Исключения (exceptions) — это события, которые прерывают нормальный поток выполнения программы. Python использует исключения для сигнализации об ошибках и нештатных ситуациях.

## Базовый синтаксис

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Деление на ноль!")
except (TypeError, ValueError) as e:
    print(f"Ошибка типа или значения: {e}")
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
else:
    print("Выполняется если не было исключений")
finally:
    print("Выполняется всегда")
```

## Иерархия встроенных исключений

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── ValueError
    ├── TypeError
    ├── AttributeError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    └── ...
```

## Часто используемые исключения

| Исключение          | Когда возникает             |
| ------------------- | --------------------------- |
| `ValueError`        | Неверное значение аргумента |
| `TypeError`         | Неверный тип аргумента      |
| `KeyError`          | Ключ не найден в словаре    |
| `IndexError`        | Индекс вне диапазона        |
| `AttributeError`    | Атрибут не существует       |
| `FileNotFoundError` | Файл не найден              |
| `ImportError`       | Ошибка импорта модуля       |
| `RuntimeError`      | Общая ошибка выполнения     |

## Создание собственных исключений

```python
class ValidationError(Exception):
    """Ошибка валидации данных"""
    pass

class UserNotFoundError(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Пользователь {user_id} не найден")

# Использование
def get_user(user_id):
    user = db.find_user(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user

try:
    user = get_user(123)
except UserNotFoundError as e:
    print(f"Ошибка: {e}, ID: {e.user_id}")
```

## Raise и re-raise

```python
# Генерация исключения
raise ValueError("Неверное значение")

# С указанием причины
try:
    parse_json(data)
except json.JSONDecodeError as e:
    raise ValueError("Неверный формат данных") from e

# Повторная генерация текущего исключения
try:
    risky_operation()
except Exception:
    logger.exception("Ошибка операции")
    raise  # Пробрасываем дальше
```

## Контекстные менеджеры для обработки ресурсов

```python
# Автоматическое закрытие файла
with open("file.txt") as f:
    data = f.read()
# Файл закроется даже при исключении

# Несколько ресурсов
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())

# Собственный контекстный менеджер
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)
```

## Лучшие практики

### 1. Ловите конкретные исключения

```python
# Плохо
try:
    do_something()
except:
    pass

# Хорошо
try:
    do_something()
except SpecificError as e:
    handle_error(e)
```

### 2. Не подавляйте исключения без причины

```python
# Плохо
try:
    risky_operation()
except Exception:
    pass  # Ошибка проглочена

# Хорошо
try:
    risky_operation()
except SpecificError:
    logger.warning("Ожидаемая ошибка, продолжаем")
```

### 3. Используйте finally для cleanup

```python
connection = None
try:
    connection = create_connection()
    connection.execute(query)
except DatabaseError:
    handle_error()
finally:
    if connection:
        connection.close()
```

### 4. Документируйте исключения

```python
def divide(a: float, b: float) -> float:
    """
    Делит a на b.

    Raises:
        ZeroDivisionError: Если b равно нулю
        TypeError: Если аргументы не числа
    """
    return a / b
```

## Частые вопросы

**Когда использовать исключения vs проверки?**
Используйте исключения для "исключительных" ситуаций. Для ожидаемых условий лучше проверки.

**Как обработать исключение и продолжить?**

```python
for item in items:
    try:
        process(item)
    except ProcessingError:
        logger.error(f"Ошибка обработки {item}")
        continue
```

**Как создать цепочку исключений?**

```python
raise NewError("описание") from original_error
```
