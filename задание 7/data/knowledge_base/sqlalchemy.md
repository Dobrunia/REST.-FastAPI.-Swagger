# SQLAlchemy — ORM для Python

## Что такое SQLAlchemy

SQLAlchemy — это популярная библиотека Python для работы с базами данных. Она предоставляет два основных подхода: Core (низкоуровневый SQL) и ORM (объектно-реляционное отображение). ORM позволяет работать с таблицами базы данных как с Python-классами.

## Установка

```bash
pip install sqlalchemy
# Для асинхронной работы
pip install sqlalchemy[asyncio] aiosqlite
```

## Определение моделей (ORM)

```python
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)

    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
```

## Создание подключения

```python
# SQLite
engine = create_engine("sqlite:///app.db", echo=True)

# PostgreSQL
engine = create_engine("postgresql://user:pass@localhost:5432/dbname")

# Создание таблиц
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()
```

## CRUD операции

### Create (создание)

```python
new_user = User(name="John", email="john@example.com")
session.add(new_user)
session.commit()
```

### Read (чтение)

```python
# Получить по ID
user = session.get(User, 1)

# Фильтрация
users = session.query(User).filter(User.name == "John").all()

# Первый результат
user = session.query(User).filter_by(email="john@example.com").first()

# Все записи
all_users = session.query(User).all()
```

### Update (обновление)

```python
user = session.get(User, 1)
user.name = "John Updated"
session.commit()
```

### Delete (удаление)

```python
user = session.get(User, 1)
session.delete(user)
session.commit()
```

## Запросы

```python
from sqlalchemy import and_, or_, desc

# Сложные условия
users = session.query(User).filter(
    and_(
        User.name.like("%John%"),
        User.id > 5
    )
).all()

# Сортировка
users = session.query(User).order_by(desc(User.id)).limit(10).all()

# JOIN
posts_with_authors = session.query(Post).join(User).filter(
    User.name == "John"
).all()
```

## Асинхронный SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///app.db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.get(User, user_id)
        return result
```

## Миграции с Alembic

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

## Частые вопросы

**Как избежать N+1 запросов?**
Используйте eager loading:

```python
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.posts)).all()
```

**Как выполнить raw SQL?**

```python
result = session.execute("SELECT * FROM users WHERE id = :id", {"id": 1})
```

**Как использовать транзакции?**

```python
try:
    session.add(user)
    session.add(post)
    session.commit()
except:
    session.rollback()
    raise
```
