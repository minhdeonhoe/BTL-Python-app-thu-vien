from typing import Dict, List
from dao.book_dao import BookDAO
from dao.borrow_dao import BorrowDAO
from dao.reader_dao import ReaderDAO
from models.borrow import Borrow


class BorrowService:
    @staticmethod
    def get_all_borrows(keyword: str = "", status_filter: str = "Tất cả") -> List[Borrow]:
        return BorrowDAO.get_all(keyword=keyword.strip(), status_filter=status_filter)

    @staticmethod
    def get_borrows_by_reader(reader_id: int) -> List[Borrow]:
        return BorrowDAO.get_by_reader_id(reader_id)

    @staticmethod
    def create_borrow(reader_id: int, book_id: int, user_id: int, due_date: str, note: str = "") -> None:
        reader = ReaderDAO.get_by_id(reader_id)
        if not reader:
            raise ValueError("Không tìm thấy độc giả hợp lệ!")
        if reader.status != "Hoạt động":
            raise ValueError("Thẻ độc giả hiện đang bị khóa, không thể mượn sách!")
        
        
        book = BookDAO.get_by_id(book_id)
        if not book:
            raise ValueError("Không tìm thấy sách trong hệ thống!")
        if book.available_quantity <= 0:
            raise ValueError("Sách này đã hết bản có sẵn trong kho!")
        clean_note = note.strip() or None
        
        
        BorrowDAO.insert_borrow_and_decrease_stock(
            reader_id=reader_id,
            book_id=book_id,
            user_id=user_id,
            due_date=due_date,
            note=clean_note,
        )

    @staticmethod
    def return_book(borrow_id: int, new_status: str = "Đã trả", fine_amount: float = 0, note: str = "") -> None:
        borrow = BorrowDAO.get_by_id(borrow_id)
        if not borrow:
            raise ValueError("Không tìm thấy phiếu mượn!")
        if borrow.status == "Đã trả":
            raise ValueError("Phiếu mượn này đã được trả trước đó!")
        if fine_amount < 0:
            raise ValueError("Tiền phạt không được nhỏ hơn 0!")
        restore_stock = new_status == "Đã trả"
        clean_note = note.strip() or None

        BorrowDAO.update_return_and_restore_stock(
            borrow_id=borrow_id,
            book_id=borrow.book_id,
            new_status=new_status,
            fine_amount=fine_amount,
            note=clean_note,
            restore_stock=restore_stock,
        )

    @staticmethod
    def get_dashboard_stats() -> Dict[str, int]:
        return BorrowDAO.get_dashboard_stats()
