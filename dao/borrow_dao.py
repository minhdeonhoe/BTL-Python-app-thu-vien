from decimal import Decimal
from typing import Dict, List, Optional
from config.database import get_db_cursor
from models.borrow import Borrow


class BorrowDAO:
    """Tầng truy cập dữ liệu (DAO) cho bảng Borrows và thống kê"""

    @staticmethod
    def get_all(keyword: str = "", status_filter: str = "Tất cả") -> List[Borrow]:
        query = """
            SELECT b.borrow_id, b.reader_id, b.book_id, b.user_id,
                   b.borrow_date, b.due_date, b.return_date, b.status,
                   b.fine_amount, b.note,
                   r.full_name AS reader_name, r.card_number,
                   bk.title AS book_title,
                   u.full_name AS staff_name
            FROM Borrows b
            JOIN Readers r ON b.reader_id = r.reader_id
            JOIN Books bk ON b.book_id = bk.book_id
            JOIN Users u ON b.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        if keyword:
            query += """
                AND (
                    CAST(b.borrow_id AS VARCHAR(20)) LIKE ?
                    OR r.full_name LIKE ?
                    OR r.card_number LIKE ?
                    OR bk.title LIKE ?
                    OR u.full_name LIKE ?
                )
            """
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw, kw])

        if status_filter and status_filter != "Tất cả":
            query += " AND b.status LIKE ?"
            params.append(f"%{status_filter}%")

        query += " ORDER BY b.borrow_id DESC"

        borrows = []
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                borrows.append(
                    Borrow(
                        borrow_id=row[0],
                        reader_id=row[1],
                        book_id=row[2],
                        user_id=row[3],
                        borrow_date=row[4],
                        due_date=row[5],
                        return_date=row[6],
                        status=row[7],
                        fine_amount=Decimal(str(row[8] or 0)),
                        note=row[9] or "",
                        reader_name=row[10],
                        card_number=row[11],
                        book_title=row[12],
                        staff_name=row[13],
                    )
                )
        return borrows

    @staticmethod
    def get_by_reader_id(reader_id: int) -> List[Borrow]:
        """Lấy toàn bộ lịch sử mượn trả của một độc giả cụ thể"""
        query = """
            SELECT b.borrow_id, b.reader_id, b.book_id, b.user_id,
                   b.borrow_date, b.due_date, b.return_date, b.status,
                   b.fine_amount, b.note,
                   r.full_name AS reader_name, r.card_number,
                   bk.title AS book_title,
                   u.full_name AS staff_name
            FROM Borrows b
            JOIN Readers r ON b.reader_id = r.reader_id
            JOIN Books bk ON b.book_id = bk.book_id
            JOIN Users u ON b.user_id = u.user_id
            WHERE b.reader_id = ?
            ORDER BY b.borrow_id DESC
        """
        borrows = []
        with get_db_cursor() as cursor:
            cursor.execute(query, (reader_id,))
            for row in cursor.fetchall():
                borrows.append(
                    Borrow(
                        borrow_id=row[0],
                        reader_id=row[1],
                        book_id=row[2],
                        user_id=row[3],
                        borrow_date=row[4],
                        due_date=row[5],
                        return_date=row[6],
                        status=row[7],
                        fine_amount=Decimal(str(row[8] or 0)),
                        note=row[9] or "",
                        reader_name=row[10],
                        card_number=row[11],
                        book_title=row[12],
                        staff_name=row[13],
                    )
                )
        return borrows

    @staticmethod
    def get_by_id(borrow_id: int) -> Optional[Borrow]:
        query = """
            SELECT borrow_id, reader_id, book_id, user_id,
                   borrow_date, due_date, return_date, status, fine_amount, note
            FROM Borrows
            WHERE borrow_id = ?
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (borrow_id,))
            row = cursor.fetchone()
            if row:
                return Borrow(
                    borrow_id=row[0],
                    reader_id=row[1],
                    book_id=row[2],
                    user_id=row[3],
                    borrow_date=row[4],
                    due_date=row[5],
                    return_date=row[6],
                    status=row[7],
                    fine_amount=Decimal(str(row[8] or 0)),
                    note=row[9] or "",
                )
        return None

    @staticmethod
    def insert_borrow_and_decrease_stock(
        reader_id: int, book_id: int, user_id: int, due_date: str, note: Optional[str] = None
    ) -> None:
        """Thêm bản ghi phiếu mượn và giảm số lượng sách sẵn có trong cùng 1 transaction"""
        insert_sql = """
            INSERT INTO Borrows (reader_id, book_id, user_id, borrow_date, due_date, status, fine_amount, note)
            VALUES (?, ?, ?, CAST(GETDATE() AS DATE), ?, N'Đang mượn', 0, ?)
        """
        update_book_sql = """
            UPDATE Books
            SET available_quantity = available_quantity - 1
            WHERE book_id = ?
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(insert_sql, (reader_id, book_id, user_id, due_date, note))
            cursor.execute(update_book_sql, (book_id,))

    @staticmethod
    def update_return_and_restore_stock(
        borrow_id: int,
        book_id: int,
        new_status: str,
        fine_amount: float,
        note: Optional[str] = None,
        restore_stock: bool = True,
    ) -> None:
        """Cập nhật phiếu mượn khi trả/báo mất sách và hoàn lại số lượng kho trong cùng 1 transaction"""
        update_borrow_sql = """
            UPDATE Borrows
            SET return_date = CAST(GETDATE() AS DATE),
                status = ?,
                fine_amount = ?,
                note = ?
            WHERE borrow_id = ?
        """
        restore_book_sql = """
            UPDATE Books
            SET available_quantity = CASE
                WHEN available_quantity < total_quantity THEN available_quantity + 1
                ELSE total_quantity
            END
            WHERE book_id = ?
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(update_borrow_sql, (new_status, fine_amount, note, borrow_id))
            if restore_stock:
                cursor.execute(restore_book_sql, (book_id,))

    @staticmethod
    def get_dashboard_stats() -> Dict[str, int]:
        stats = {
            "total_books": 0,
            "available_books": 0,
            "total_readers": 0,
            "active_borrows": 0,
            "overdue_borrows": 0,
        }
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*), ISNULL(SUM(available_quantity), 0) FROM Books WHERE is_active = 1")
            b_row = cursor.fetchone()
            if b_row:
                stats["total_books"] = b_row[0] or 0
                stats["available_books"] = b_row[1] or 0

            cursor.execute("SELECT COUNT(*) FROM Readers WHERE is_active = 1")
            r_row = cursor.fetchone()
            if r_row:
                stats["total_readers"] = r_row[0] or 0

            cursor.execute("SELECT COUNT(*) FROM Borrows WHERE status = N'Đang mượn'")
            br_row = cursor.fetchone()
            if br_row:
                stats["active_borrows"] = br_row[0] or 0

            cursor.execute(
                """
                SELECT COUNT(*) FROM Borrows
                WHERE status = N'Quá hạn'
                   OR (status = N'Đang mượn' AND due_date < CAST(GETDATE() AS DATE))
                """
            )
            ov_row = cursor.fetchone()
            if ov_row:
                stats["overdue_borrows"] = ov_row[0] or 0

        return stats
