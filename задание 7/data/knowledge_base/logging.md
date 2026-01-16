# Logging — логирование в Python

## Что такое логирование

Логирование — это процесс записи сообщений о работе программы. В отличие от print(), логирование позволяет настраивать уровни важности, форматирование, направлять вывод в файлы и фильтровать сообщения.

## Уровни логирования

```python
import logging

logging.debug("Отладочная информация")      # 10
logging.info("Информационное сообщение")    # 20
logging.warning("Предупреждение")           # 30
logging.error("Ошибка")                     # 40
logging.critical("Критическая ошибка")      # 50
```

По умолчанию показываются только WARNING и выше.

## Базовая настройка

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("Приложение запущено")
```

## Логирование в файл

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()  # Также в консоль
    ]
)
```

## Именованные логгеры

```python
# module_a.py
logger = logging.getLogger(__name__)

def process():
    logger.info("Обработка данных")
    try:
        # ...
    except Exception as e:
        logger.exception("Ошибка при обработке")  # Включает traceback

# main.py
logger = logging.getLogger(__name__)
logger.info("Запуск приложения")
```

## Продвинутая конфигурация

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Создание логгера
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Форматтер
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)

# Handler для консоли
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Handler для файла с ротацией по размеру
file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Добавление handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

## Конфигурация через словарь

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "DEBUG"
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## Логирование исключений

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.error("Деление на ноль", exc_info=True)
    # или
    logger.exception("Деление на ноль")  # Автоматически добавляет traceback
```

## Структурированное логирование

```python
# С использованием extra
logger.info("Пользователь вошёл", extra={"user_id": 123, "ip": "192.168.1.1"})

# JSON логирование (с библиотекой python-json-logger)
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter())
logger.addHandler(handler)
```

## Частые вопросы

**Почему не использовать print()?**

- Нельзя настроить уровни важности
- Нет меток времени и контекста
- Сложно перенаправить в файл
- Нельзя отключить в production

**Как логировать в нескольких модулях?**
Используйте `logging.getLogger(__name__)` в каждом модуле. Все логгеры наследуют настройки от root logger.

**Как отключить логи библиотек?**

```python
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
```

**Какой уровень использовать?**

- DEBUG: детальная отладочная информация
- INFO: подтверждение нормальной работы
- WARNING: что-то неожиданное, но не ошибка
- ERROR: ошибка, функция не выполнена
- CRITICAL: серьёзная ошибка, приложение может упасть
