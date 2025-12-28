from datetime import datetime
from pydantic import BaseModel, Field


class TermBase(BaseModel):
    term: str = Field(..., min_length=1)
    definition: str = Field(..., min_length=1)


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    definition: str = Field(..., min_length=1)


class TermResponse(TermBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str

