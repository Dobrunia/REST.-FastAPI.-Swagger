from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.database import get_db, init_db
from app.schemas import TermCreate, TermUpdate, TermResponse, MessageResponse
from app import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация БД при запуске приложения."""
    init_db()
    yield


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def root():
    """Корневой эндпоинт - редирект на документацию."""
    return RedirectResponse(url="/docs")


@app.get("/terms", response_model=list[TermResponse], tags=["Terms"])
def get_terms(
    sort_by: Optional[str] = Query("created_at", description="Поле для сортировки (term, created_at, updated_at)"),
    order: Optional[str] = Query("desc", description="Порядок сортировки (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Получить список всех терминов.
    
    Поддерживает сортировку по полям: term, created_at, updated_at.
    """
    return crud.get_terms(db, sort_by=sort_by, order=order)


@app.get("/terms/{term}", response_model=TermResponse, tags=["Terms"])
def get_term(term: str, db: Session = Depends(get_db)):
    """
    Получить термин по ключевому слову.
    
    Возвращает HTTP 404, если термин не найден.
    """
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Термин '{term}' не найден"
        )
    return db_term


@app.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED, tags=["Terms"])
def create_term(term_data: TermCreate, db: Session = Depends(get_db)):
    """
    Добавить новый термин в глоссарий.
    
    Возвращает HTTP 409, если термин уже существует.
    """
    existing_term = crud.get_term_by_term(db, term_data.term)
    if existing_term:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Термин '{term_data.term}' уже существует"
        )
    return crud.create_term(db, term_data)


@app.put("/terms/{term}", response_model=TermResponse, tags=["Terms"])
def update_term(term: str, term_data: TermUpdate, db: Session = Depends(get_db)):
    """
    Обновить описание существующего термина.
    
    Возвращает HTTP 404, если термин не найден.
    """
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Термин '{term}' не найден"
        )
    return crud.update_term(db, db_term, term_data)


@app.delete("/terms/{term}", response_model=MessageResponse, tags=["Terms"])
def delete_term(term: str, db: Session = Depends(get_db)):
    """
    Удалить термин из глоссария.
    
    Возвращает HTTP 404, если термин не найден.
    """
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Термин '{term}' не найден"
        )
    crud.delete_term(db, db_term)
    return MessageResponse(message=f"Термин '{term}' успешно удален")

