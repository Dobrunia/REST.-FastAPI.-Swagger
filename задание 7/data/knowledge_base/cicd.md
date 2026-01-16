# CI/CD — непрерывная интеграция и доставка

## Что такое CI/CD

**CI (Continuous Integration)** — практика частой интеграции кода в общий репозиторий с автоматическим тестированием каждого изменения.

**CD (Continuous Delivery/Deployment)** — автоматическая доставка протестированного кода на staging/production серверы.

## Основные инструменты

- **GitHub Actions** — встроенный CI/CD в GitHub
- **GitLab CI** — встроенный CI/CD в GitLab
- **Jenkins** — self-hosted решение
- **CircleCI**, **Travis CI** — облачные сервисы

## GitHub Actions

### Базовая структура

Файл `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Матрица тестирования

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Кэширование зависимостей

```yaml
- name: Cache pip
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## GitLab CI

Файл `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: '$CI_PROJECT_DIR/.cache/pip'

cache:
  paths:
    - .cache/pip

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t myapp:$CI_COMMIT_SHA .
    - docker push registry.example.com/myapp:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - ssh server "docker pull myapp:$CI_COMMIT_SHA && docker-compose up -d"
  only:
    - main
  when: manual
```

## Типичный пайплайн Python проекта

```yaml
name: Python CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff black mypy
      - run: ruff check .
      - run: black --check .
      - run: mypy src/

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -v --cov=src
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/postgres

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          # Deployment commands
```

## Секреты и переменные окружения

```yaml
# В GitHub: Settings -> Secrets -> Actions
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

## Частые вопросы

**Когда запускать CI?**

- На каждый push в feature ветки
- На каждый pull request
- При слиянии в main/develop

**Что должно быть в CI пайплайне?**

1. Линтинг (ruff, flake8)
2. Форматирование (black)
3. Type checking (mypy)
4. Unit тесты
5. Integration тесты
6. Security scan (bandit)

**Как ускорить CI?**

- Кэшировать зависимости
- Запускать jobs параллельно
- Использовать матрицу только для критичных комбинаций
