from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Reader:
    reader_id: Optional[int] = None
    card_number: str = ""
    full_name: str = ""
    gender: str = "Nam"
    dob: Optional[date] = None
    phone: str = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    status: str = "Hoạt động"
    is_active: bool = True
    created_at: Optional[datetime] = None

