from typing import List, Optional
from config.database import get_db_cursor
from models.book import Book


class BookDAO:

    @staticmethod
    def get_all(keyword: str = "", category: str = "Tất cả") -> List[Book]:
        query = """
            SELECT book_id, isbn, title, author, category, publisher,
                   publish_year, total_quantity, available_quantity, location, is_active, created_at
            FROM Books
            WHERE is_active = 1
        """
        params = []
        if keyword:
            query += """
                AND (
                    title LIKE ?
                    OR author LIKE ?
                    OR isbn LIKE ?
                    OR category LIKE ?
                    OR publisher LIKE ?
                    OR location LIKE ?
                )
            """
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw, kw, kw])

        if category and category != "Tất cả":
            query += " AND category LIKE ?"
            params.append(f"%{category}%")

        query += " ORDER BY book_id ASC"

        books = []
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                books.append(
                    Book(
                        book_id=row[0],
                        isbn=row[1] or "",
                        title=row[2],
                        author=row[3],
                        category=row[4],
                        publisher=row[5] or "",
                        publish_year=row[6],
                        total_quantity=row[7],
                        available_quantity=row[8],
                        location=row[9] or "",
                        is_active=bool(row[10]),
                        created_at=row[11],
                    )
                )
        return books

    @staticmethod
    def get_by_id(book_id: int) -> Optional[Book]:
        query = """
            SELECT book_id, isbn, title, author, category, publisher,
                   publish_year, total_quantity, available_quantity, location, is_active, created_at
            FROM Books
            WHERE book_id = ? AND is_active = 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (book_id,))
            row = cursor.fetchone()
            if row:
                return Book(
                    book_id=row[0],
                    isbn=row[1] or "",
                    title=row[2],
                    author=row[3],
                    category=row[4],
                    publisher=row[5] or "",
                    publish_year=row[6],
                    total_quantity=row[7],
                    available_quantity=row[8],
                    location=row[9] or "",
                    is_active=bool(row[10]),
                    created_at=row[11],
                )
        return None

    @staticmethod
    def get_categories() -> List[str]:
        query = "SELECT DISTINCT category FROM Books WHERE is_active = 1 ORDER BY category"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall() if row[0]]

    @staticmethod
    def insert(book: Book) -> None:
        query = """
            INSERT INTO Books (isbn, title, author, category, publisher, publish_year,
                               total_quantity, available_quantity, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    book.isbn or None,
                    book.title,
                    book.author,
                    book.category,
                    book.publisher or None,
                    book.publish_year,
                    book.total_quantity,
                    book.available_quantity,
                    book.location or None,
                ),
            )

    @staticmethod
    def update(book: Book) -> None:
        query = """
            UPDATE Books
            SET isbn = ?, title = ?, author = ?, category = ?, publisher = ?,
                publish_year = ?, total_quantity = ?, available_quantity = ?, location = ?
            WHERE book_id = ?
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    book.isbn or None,
                    book.title,
                    book.author,
                    book.category,
                    book.publisher or None,
                    book.publish_year,
                    book.total_quantity,
                    book.available_quantity,
                    book.location or None,
                    book.book_id,
                ),
            )

    @staticmethod
    def soft_delete(book_id: int) -> None:
        query = "UPDATE Books SET is_active = 0 WHERE book_id = ?"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (book_id,))
