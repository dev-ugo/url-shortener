"""API request and response schemas."""

from datetime import datetime

from pydantic import BaseModel

class LinkCreate(BaseModel):
    """Payload for creating a short link."""

    url: str


class LinkRead(BaseModel):
    """Public representation of a stored short link."""

    slug: str
    original_url: str
    short_url: str
    created_at: datetime
