# Poetry — управление зависимостями Python

## Что такое Poetry

Poetry — это современный инструмент для управления зависимостями и пакетами Python. Он объединяет функции pip, venv и setuptools в одном инструменте, использует файл `pyproject.toml` для конфигурации и создаёт lock-файл для воспроизводимых сборок.

## Установка Poetry

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Проверка установки
poetry --version
```

## Создание проекта

```bash
# Новый проект
poetry new my-project

# Инициализация в существующей папке
poetry init
```

Структура нового проекта:

```
my-project/
├── pyproject.toml
├── README.md
├── my_project/
│   └── __init__.py
└── tests/
    └── __init__.py
```

## pyproject.toml

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "Описание проекта"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.109.0"
pydantic = "^2.5.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
black = "^24.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Управление зависимостями

### Добавление пакетов

```bash
poetry add fastapi              # Основная зависимость
poetry add pytest --group dev   # Dev зависимость
poetry add "uvicorn[standard]"  # С extras
poetry add fastapi@^0.109.0     # Определённая версия
```

### Удаление пакетов

```bash
poetry remove fastapi
```

### Обновление пакетов

```bash
poetry update                   # Все пакеты
poetry update fastapi           # Конкретный пакет
poetry show --outdated          # Показать устаревшие
```

## Виртуальное окружение

```bash
# Создание и активация окружения
poetry install                  # Установить зависимости и создать venv
poetry shell                    # Активировать окружение

# Запуск команд без активации
poetry run python main.py
poetry run pytest

# Информация об окружении
poetry env info
poetry env list
```

## Lock-файл

`poetry.lock` содержит точные версии всех зависимостей (включая транзитивные) для воспроизводимых установок.

```bash
# Установка из lock-файла (точные версии)
poetry install

# Обновить lock-файл без установки
poetry lock
```

## Публикация пакета

```bash
# Сборка пакета
poetry build

# Публикация на PyPI
poetry publish

# Публикация на приватный репозиторий
poetry config repositories.private https://private.pypi.org
poetry publish -r private
```

## Полезные команды

```bash
poetry show                     # Список установленных пакетов
poetry show fastapi             # Информация о пакете
poetry check                    # Проверка pyproject.toml
poetry export -f requirements.txt -o requirements.txt  # Экспорт в requirements.txt
```

## Конфигурация

```bash
# Создавать venv в папке проекта
poetry config virtualenvs.in-project true

# Показать конфигурацию
poetry config --list
```

## Частые вопросы

**Чем Poetry лучше pip + venv?**

- Lock-файл для воспроизводимых сборок
- Разделение dev и production зависимостей
- Разрешение конфликтов версий
- Встроенная публикация пакетов
- Единый файл конфигурации

**Как мигрировать с requirements.txt?**

```bash
poetry init
cat requirements.txt | xargs poetry add
```

**Как использовать приватный PyPI?**

```bash
poetry source add private https://private.pypi.org/simple/
poetry add package --source private
```

**Где хранится виртуальное окружение?**
По умолчанию в `~/.cache/pypoetry/virtualenvs/`. Для хранения в проекте:

```bash
poetry config virtualenvs.in-project true
```
