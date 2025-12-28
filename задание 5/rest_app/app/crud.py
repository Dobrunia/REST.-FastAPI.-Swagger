from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.models import Term
from app.schemas import TermCreate, TermUpdate


def get_terms(db: Session, sort_by: str = "created_at", order: str = "desc") -> list[Term]:
    sort_column = getattr(Term, sort_by, Term.created_at)
    order_func = desc if order == "desc" else asc
    return db.query(Term).order_by(order_func(sort_column)).all()


def get_term_by_term(db: Session, term: str) -> Optional[Term]:
    return db.query(Term).filter(Term.term == term).first()


def create_term(db: Session, term_data: TermCreate) -> Term:
    db_term = Term(
        term=term_data.term,
        definition=term_data.definition
    )
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term


def update_term(db: Session, db_term: Term, term_data: TermUpdate) -> Term:
    db_term.definition = term_data.definition
    db_term.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_term)
    return db_term


def delete_term(db: Session, db_term: Term) -> None:
    db.delete(db_term)
    db.commit()

