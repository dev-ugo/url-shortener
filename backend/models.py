"""Database models used by the URL shortener."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Link(SQLModel, table=True):
    """Stored short link mapping."""

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True, max_length=10)
    original_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
