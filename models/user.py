from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    email: Optional[str] = None
    role: str = "Librarian"
    is_active: bool = True
    created_at: Optional[datetime] = None

