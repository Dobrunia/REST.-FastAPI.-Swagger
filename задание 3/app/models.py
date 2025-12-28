from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Index

from app.database import Base


class Term(Base):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, nullable=False, index=True)
    definition = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_terms_term_lower", "term"),
    )

