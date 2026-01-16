# Debugging — отладка Python кода

## Что такое отладка

Отладка (debugging) — это процесс поиска и исправления ошибок в программе. Python предоставляет встроенные инструменты отладки, а также существует множество IDE с графическими отладчиками.

## Встроенный отладчик pdb

### Запуск pdb

```python
# Вставка точки останова в код
import pdb; pdb.set_trace()

# Python 3.7+ — более короткий синтаксис
breakpoint()

# Запуск скрипта в режиме отладки
# python -m pdb script.py
```

### Команды pdb

```
n (next)      — выполнить следующую строку
s (step)      — войти в функцию
c (continue)  — продолжить до следующей точки останова
r (return)    — выполнить до return текущей функции
l (list)      — показать код вокруг текущей строки
ll            — показать весь код текущей функции
p <expr>      — вывести значение выражения
pp <expr>     — pretty-print значения
w (where)     — показать стек вызовов
u (up)        — подняться на уровень вверх по стеку
d (down)      — опуститься на уровень вниз по стеку
b <line>      — установить точку останова
cl <num>      — удалить точку останова
q (quit)      — выйти из отладчика
```

### Пример сессии pdb

```python
def calculate(x, y):
    breakpoint()  # Останов здесь
    result = x + y
    return result * 2

# В pdb:
# (Pdb) p x
# 5
# (Pdb) p y
# 3
# (Pdb) n
# (Pdb) p result
# 8
```

## Отладка в VS Code

1. Установите расширение Python
2. Создайте файл `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

3. Установите точки останова кликом слева от номера строки
4. Нажмите F5 для запуска

## Отладка с print (быстрый способ)

```python
# Простой print
print(f"DEBUG: variable = {variable}")

# С информацией о месте вызова
def debug(*args):
    import inspect
    frame = inspect.currentframe().f_back
    print(f"[{frame.f_code.co_filename}:{frame.f_lineno}]", *args)

debug("value =", value)
```

## Rich для красивого вывода

```python
from rich import print, inspect
from rich.console import Console

console = Console()

# Красивый вывод структур данных
print({"key": "value", "list": [1, 2, 3]})

# Детальный inspect объекта
inspect(my_object, methods=True)

# Трассировка с подсветкой
console.print_exception()
```

## Traceback и исключения

```python
import traceback

try:
    risky_operation()
except Exception as e:
    # Полный traceback
    traceback.print_exc()

    # Получить как строку
    tb_str = traceback.format_exc()

    # Информация об исключении
    print(f"Тип: {type(e).__name__}")
    print(f"Сообщение: {e}")
```

## Assert для проверок

```python
def divide(a, b):
    assert b != 0, "Делитель не может быть нулём"
    assert isinstance(a, (int, float)), f"Ожидается число, получено {type(a)}"
    return a / b
```

Assert отключается при запуске с флагом `-O`:

```bash
python -O script.py  # assert не выполняется
```

## Профилирование для поиска узких мест

```python
import cProfile
import pstats

# Профилирование функции
cProfile.run("my_function()", "output.prof")

# Анализ результатов
stats = pstats.Stats("output.prof")
stats.sort_stats("cumulative")
stats.print_stats(10)  # Top 10 функций

# Декоратор для профилирования
def profile(func):
    def wrapper(*args, **kwargs):
        import cProfile
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.print_stats(sort='cumulative')
        return result
    return wrapper
```

## Частые вопросы

**Как отлаживать асинхронный код?**
Используйте `breakpoint()` в async функциях. В pdb можно выполнять `await` выражения.

**Как отлаживать многопоточный код?**
Используйте логирование вместо print. В IDE можно переключаться между потоками.

**Как найти утечку памяти?**

```python
import tracemalloc
tracemalloc.start()
# ... код ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```

**Как отлаживать код в production?**
Используйте логирование с достаточным уровнем детализации. Для критических ошибок — Sentry или аналоги.
