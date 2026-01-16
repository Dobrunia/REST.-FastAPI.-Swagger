# Pytest — тестирование в Python

## Что такое Pytest

Pytest — это популярный фреймворк для тестирования Python-кода. Он поддерживает простые assert-ы, фикстуры, параметризацию и плагины. Pytest автоматически обнаруживает тесты и предоставляет подробные отчёты об ошибках.

## Установка и запуск

```bash
pip install pytest

# Запуск тестов
pytest                      # Все тесты
pytest tests/               # Тесты в папке
pytest test_module.py       # Конкретный файл
pytest test_module.py::test_func  # Конкретный тест
pytest -v                   # Подробный вывод
pytest -x                   # Остановиться на первой ошибке
pytest -k "name"            # Фильтр по имени
```

## Структура тестов

```python
# test_calculator.py

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

class TestCalculator:
    def test_multiply(self):
        assert 2 * 3 == 6

    def test_divide(self):
        assert 10 / 2 == 5
```

Правила именования:

- Файлы: `test_*.py` или `*_test.py`
- Функции: `test_*`
- Классы: `Test*`

## Фикстуры (Fixtures)

Фикстуры — это функции, которые подготавливают данные или состояние для тестов.

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "John", "age": 30}

@pytest.fixture
def database_connection():
    conn = create_connection()
    yield conn  # Тест выполняется здесь
    conn.close()  # Cleanup после теста

def test_with_data(sample_data):
    assert sample_data["name"] == "John"

def test_with_db(database_connection):
    result = database_connection.query("SELECT 1")
    assert result == 1
```

### Области действия фикстур

```python
@pytest.fixture(scope="function")  # По умолчанию, для каждого теста
@pytest.fixture(scope="class")     # Один раз на класс
@pytest.fixture(scope="module")    # Один раз на модуль
@pytest.fixture(scope="session")   # Один раз на всю сессию
```

## Параметризация

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected

@pytest.mark.parametrize("a,b,result", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, result):
    assert a + b == result
```

## Проверка исключений

```python
import pytest

def test_raises_exception():
    with pytest.raises(ValueError):
        int("not a number")

def test_exception_message():
    with pytest.raises(ValueError, match="invalid literal"):
        int("abc")
```

## Маркеры

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    # Долгий тест
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_syntax():
    pass
```

Запуск с маркерами:

```bash
pytest -m slow              # Только slow тесты
pytest -m "not slow"        # Все кроме slow
```

## conftest.py

Файл `conftest.py` содержит общие фикстуры для всех тестов в директории.

```python
# conftest.py
import pytest

@pytest.fixture
def app():
    return create_app(testing=True)

@pytest.fixture
def client(app):
    return app.test_client()
```

## Частые вопросы

**Как запустить тесты параллельно?**

```bash
pip install pytest-xdist
pytest -n auto              # Автоопределение числа процессов
```

**Как измерить покрытие кода?**

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
```
