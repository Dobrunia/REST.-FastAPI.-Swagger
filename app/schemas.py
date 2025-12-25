from datetime import datetime
from pydantic import BaseModel, Field


class TermBase(BaseModel):
    """Базовая схема термина."""
    term: str = Field(..., min_length=1, description="Ключевое слово")
    definition: str = Field(..., min_length=1, description="Описание термина")


class TermCreate(TermBase):
    """Схема для создания термина."""
    pass


class TermUpdate(BaseModel):
    """Схема для обновления термина."""
    definition: str = Field(..., min_length=1, description="Новое описание термина")


class TermResponse(TermBase):
    """Схема ответа с полной информацией о термине."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Схема для сообщений об операциях."""
    message: str

