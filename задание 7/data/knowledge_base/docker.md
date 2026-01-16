# Docker — контейнеризация приложений

## Что такое Docker

Docker — это платформа для разработки, доставки и запуска приложений в контейнерах. Контейнер — это изолированная среда, которая содержит всё необходимое для работы приложения: код, библиотеки, системные инструменты и настройки.

## Основные концепции

- **Image (образ)** — шаблон для создания контейнеров, содержит файловую систему и настройки
- **Container (контейнер)** — запущенный экземпляр образа
- **Dockerfile** — инструкция для сборки образа
- **Docker Hub** — публичный реестр образов

## Основные команды

### Работа с образами

```bash
docker images                       # Список образов
docker pull <image>                 # Скачать образ
docker build -t <name> .            # Собрать образ из Dockerfile
docker rmi <image>                  # Удалить образ
```

### Работа с контейнерами

```bash
docker ps                           # Список запущенных контейнеров
docker ps -a                        # Все контейнеры
docker run <image>                  # Запустить контейнер
docker run -d <image>               # Запустить в фоне
docker run -p 8080:80 <image>       # С проброской портов
docker run -v /host:/container <image>  # С монтированием тома
docker stop <container>             # Остановить контейнер
docker rm <container>               # Удалить контейнер
docker exec -it <container> bash    # Войти в контейнер
docker logs <container>             # Посмотреть логи
```

## Пример Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## Docker Compose

Docker Compose позволяет запускать многоконтейнерные приложения.

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - '8000:8000'
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=pass

volumes:
  postgres_data:
```

### Команды Docker Compose

```bash
docker-compose up                   # Запустить все сервисы
docker-compose up -d                # Запустить в фоне
docker-compose down                 # Остановить и удалить
docker-compose logs                 # Посмотреть логи
docker-compose build                # Пересобрать образы
```

## Частые вопросы

**Чем контейнер отличается от виртуальной машины?**
Контейнеры используют ядро хост-системы и изолируют только приложение, а VM включает полную ОС. Контейнеры легче и быстрее запускаются.

**Как уменьшить размер образа?**

- Используйте alpine или slim базовые образы
- Объединяйте RUN команды
- Используйте multi-stage builds
- Добавьте `.dockerignore`
