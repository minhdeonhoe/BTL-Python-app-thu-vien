from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Borrow:
    borrow_id: Optional[int] = None
    reader_id: int = 0
    book_id: int = 0
    user_id: int = 0
    borrow_date: Optional[date] = None
    due_date: Optional[date] = None
    return_date: Optional[date] = None
    status: str = "Đang mượn"
    fine_amount: Decimal = Decimal("0.00")
    note: Optional[str] = ""
    reader_name: Optional[str] = ""
    card_number: Optional[str] = ""
    book_title: Optional[str] = ""
    staff_name: Optional[str] = ""

