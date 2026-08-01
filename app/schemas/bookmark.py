from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    name: str
    url: str


class BookmarkUpdate(BaseModel):
    name: Optional[str] = None
    is_favorite: Optional[bool] = None


class BookmarkOut(BaseModel):
    id: int
    name: str
    url: str
    favicon_url: Optional[str]
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True
