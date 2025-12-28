# Glossary API

REST API сервис для управления глоссарием терминов.

## Описание проекта

### Цель сервиса

Предоставление REST API для хранения и управления словарём терминов с их определениями. Сервис поддерживает полный набор CRUD-операций и автоматически документируется через Swagger/OpenAPI.

### Архитектура

- **FastAPI** — веб-фреймворк для создания API
- **SQLAlchemy** — ORM для работы с базой данных
- **SQLite** — легковесная база данных для хранения терминов
- **Pydantic** — валидация входных и выходных данных
- **Uvicorn** — ASGI-сервер для запуска приложения

### Структура проекта

```
glossary-api/
├── app/
│   ├── __init__.py        # Инициализация пакета
│   ├── main.py            # Точка входа FastAPI, эндпоинты
│   ├── database.py        # Подключение к БД, сессии
│   ├── models.py          # SQLAlchemy модель Term
│   ├── schemas.py         # Pydantic схемы валидации
│   ├── crud.py            # CRUD-операции с БД
│   ├── config.py          # Конфигурация приложения
│   └── db/                # Директория для SQLite БД
├── Dockerfile             # Docker-образ
├── docker-compose.yml     # Docker Compose конфигурация
├── requirements.txt       # Зависимости Python
├── README.md              # Документация
└── .gitignore
```

## Инструкция по запуску

### Локальный запуск (venv + uvicorn)

1. **Клонировать репозиторий:**

   ```bash
   git clone <repository-url>
   cd glossary-api
   ```

2. **Создать виртуальное окружение:**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **Установить зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Запустить сервер:**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Открыть в браузере:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Запуск через Docker

1. **Сборка и запуск через Docker Compose:**

   ```bash
   docker-compose up --build
   ```

2. **Или через Docker напрямую:**
   ```bash
   docker build -t glossary-api .
   docker run -p 8000:8000 glossary-api
   ```

## API Эндпоинты

### Получение списка терминов

```
GET /terms
```

**Query параметры:**

- `sort_by` — поле для сортировки (`term`, `created_at`, `updated_at`). По умолчанию: `created_at`
- `order` — порядок сортировки (`asc`, `desc`). По умолчанию: `desc`

**Пример запроса:**

```bash
curl -X GET "http://localhost:8000/terms?sort_by=term&order=asc"
```

**Пример ответа:**

```json
[
  {
    "id": 1,
    "term": "API",
    "definition": "Application Programming Interface",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### Получение термина по ключевому слову

```
GET /terms/{term}
```

**Пример запроса:**

```bash
curl -X GET "http://localhost:8000/terms/API"
```

**Ответы:**

- `200 OK` — термин найден
- `404 Not Found` — термин не найден

### Добавление нового термина

```
POST /terms
```

**Тело запроса:**

```json
{
  "term": "API",
  "definition": "Application Programming Interface"
}
```

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/terms" \
  -H "Content-Type: application/json" \
  -d '{"term": "REST", "definition": "Representational State Transfer"}'
```

**Ответы:**

- `201 Created` — термин создан
- `409 Conflict` — термин уже существует
- `422 Unprocessable Entity` — ошибка валидации

### Обновление термина

```
PUT /terms/{term}
```

**Тело запроса:**

```json
{
  "definition": "Новое описание термина"
}
```

**Пример запроса:**

```bash
curl -X PUT "http://localhost:8000/terms/API" \
  -H "Content-Type: application/json" \
  -d '{"definition": "Updated: Application Programming Interface"}'
```

**Ответы:**

- `200 OK` — термин обновлён
- `404 Not Found` — термин не найден

### Удаление термина

```
DELETE /terms/{term}
```

**Пример запроса:**

```bash
curl -X DELETE "http://localhost:8000/terms/API"
```

**Ответы:**

- `200 OK` — термин удалён
- `404 Not Found` — термин не найден

## Swagger / OpenAPI

После запуска сервера документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs — интерактивная документация с возможностью тестирования запросов
- **ReDoc**: http://localhost:8000/redoc — альтернативная документация в формате ReDoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json — спецификация OpenAPI в формате JSON

### Модели данных

#### TermCreate (входные данные для POST)

| Поле       | Тип    | Обязательное | Описание                         |
| ---------- | ------ | ------------ | -------------------------------- |
| term       | string | Да           | Ключевое слово (min. 1 символ)   |
| definition | string | Да           | Описание термина (min. 1 символ) |

#### TermUpdate (входные данные для PUT)

| Поле       | Тип    | Обязательное | Описание                               |
| ---------- | ------ | ------------ | -------------------------------------- |
| definition | string | Да           | Новое описание термина (min. 1 символ) |

#### TermResponse (выходные данные)

| Поле       | Тип      | Описание                   |
| ---------- | -------- | -------------------------- |
| id         | integer  | Уникальный идентификатор   |
| term       | string   | Ключевое слово             |
| definition | string   | Описание термина           |
| created_at | datetime | Дата создания              |
| updated_at | datetime | Дата последнего обновления |

## Технологии

- Python 3.11+
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Pydantic 2.5.3
- Uvicorn 0.27.0
- SQLite
- Docker

## Лицензия

MIT License
