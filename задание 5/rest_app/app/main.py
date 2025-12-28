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
    return RedirectResponse(url="/docs")


@app.get("/terms", response_model=list[TermResponse], tags=["Terms"])
def get_terms(
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db)
):
    return crud.get_terms(db, sort_by=sort_by, order=order)


@app.get("/terms/{term}", response_model=TermResponse, tags=["Terms"])
def get_term(term: str, db: Session = Depends(get_db)):
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term}' not found"
        )
    return db_term


@app.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED, tags=["Terms"])
def create_term(term_data: TermCreate, db: Session = Depends(get_db)):
    existing_term = crud.get_term_by_term(db, term_data.term)
    if existing_term:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Term '{term_data.term}' already exists"
        )
    return crud.create_term(db, term_data)


@app.put("/terms/{term}", response_model=TermResponse, tags=["Terms"])
def update_term(term: str, term_data: TermUpdate, db: Session = Depends(get_db)):
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term}' not found"
        )
    return crud.update_term(db, db_term, term_data)


@app.delete("/terms/{term}", response_model=MessageResponse, tags=["Terms"])
def delete_term(term: str, db: Session = Depends(get_db)):
    db_term = crud.get_term_by_term(db, term)
    if db_term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term}' not found"
        )
    crud.delete_term(db, db_term)
    return MessageResponse(message=f"Term '{term}' deleted")

