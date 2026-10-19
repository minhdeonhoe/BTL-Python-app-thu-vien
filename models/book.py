from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    book_id: Optional[int] = None
    isbn: str = ""
    title: str = ""
    author: str = ""
    category: str = ""
    publisher: Optional[str] = ""
    publish_year: Optional[int] = None
    total_quantity: int = 0
    available_quantity: int = 0
    location: Optional[str] = ""
    is_active: bool = True
    created_at: Optional[datetime] = None

