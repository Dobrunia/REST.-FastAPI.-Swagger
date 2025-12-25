from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/db/glossary.db"

# API metadata
API_TITLE = "Glossary API"
API_DESCRIPTION = """
REST API для глоссария терминов.

## Возможности

* **Получение списка терминов** - GET /terms
* **Получение термина по ключевому слову** - GET /terms/{term}
* **Добавление нового термина** - POST /terms
* **Обновление термина** - PUT /terms/{term}
* **Удаление термина** - DELETE /terms/{term}
"""
API_VERSION = "1.0.0"

