from datetime import datetime
from typing import List
from dao.book_dao import BookDAO
from models.book import Book


class BookService:
    """Tầng xử lý nghiệp vụ quản lý Sách (chỉ gọi qua BookDAO)"""

    @staticmethod
    def get_all_books(keyword: str = "", category: str = "Tất cả") -> List[Book]:
        return BookDAO.get_all(keyword=keyword.strip(), category=category)

    @staticmethod
    def get_categories() -> List[str]:
        return BookDAO.get_categories()

    @staticmethod
    def _validate_book(book: Book) -> Book:
        book.isbn = (book.isbn or "").strip()
        book.title = (book.title or "").strip()
        book.author = (book.author or "").strip()
        book.category = (book.category or "").strip()
        book.publisher = (book.publisher or "").strip()
        book.location = (book.location or "").strip()

        if not book.title or not book.author or not book.category:
            raise ValueError("Tên sách, Tác giả và Thể loại không được để trống!")

        if book.publish_year is not None:
            current_year = datetime.now().year
            if book.publish_year <= 1900 or book.publish_year > current_year:
                raise ValueError(f"Năm xuất bản phải nằm trong khoảng 1901 - {current_year}!")

        if book.total_quantity < 0 or book.available_quantity < 0:
            raise ValueError("Số lượng sách không được nhỏ hơn 0!")

        if book.available_quantity > book.total_quantity:
            raise ValueError("Số lượng sẵn có không được lớn hơn tổng số lượng!")

        return book

    @staticmethod
    def add_book(book: Book) -> None:
        validated = BookService._validate_book(book)
        BookDAO.insert(validated)

    @staticmethod
    def update_book(book: Book) -> None:
        if not book.book_id:
            raise ValueError("Thiếu ID sách cần cập nhật!")
        validated = BookService._validate_book(book)
        BookDAO.update(validated)

    @staticmethod
    def delete_book(book_id: int) -> None:
        if not book_id:
            raise ValueError("Thiếu ID sách cần xóa!")
        BookDAO.soft_delete(book_id)
