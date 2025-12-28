from datetime import datetime
from typing import Optional
import time

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from sqlalchemy.exc import OperationalError

from app.models import Term
from app.schemas import TermCreate, TermUpdate


def retry_on_lock(func):
    """Decorator to retry database operations on lock errors."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        db = args[0] if args else kwargs.get('db')
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if db:
                    db.rollback()
                
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.05 * (2 ** attempt))  # 50ms, 100ms, 200ms
                    continue
                raise
        return func(*args, **kwargs)
    return wrapper


def get_terms(db: Session, sort_by: str = "created_at", order: str = "desc") -> list[Term]:
    sort_column = getattr(Term, sort_by, Term.created_at)
    order_func = desc if order == "desc" else asc
    return db.query(Term).order_by(order_func(sort_column)).all()


def get_term_by_term(db: Session, term: str) -> Optional[Term]:
    return db.query(Term).filter(Term.term == term).first()


@retry_on_lock
def create_term(db: Session, term_data: TermCreate) -> Term:
    db_term = Term(
        term=term_data.term,
        definition=term_data.definition
    )
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term


@retry_on_lock
def update_term(db: Session, db_term: Term, term_data: TermUpdate) -> Term:
    db_term.definition = term_data.definition
    db_term.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_term)
    return db_term


@retry_on_lock
def delete_term(db: Session, db_term: Term) -> None:
    db.delete(db_term)
    db.commit()

