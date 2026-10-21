from typing import List, Optional
from config.database import get_db_cursor
from models.reader import Reader


class ReaderDAO:

    @staticmethod
    def get_all(keyword: str = "", status_filter: str = "Tất cả") -> List[Reader]:
        query = """
            SELECT reader_id, card_number, full_name, gender, dob, phone, email, address, status, is_active, created_at
            FROM Readers
            WHERE is_active = 1
        """
        params = []
        if keyword:
            query += """
                AND (
                    card_number LIKE ?
                    OR full_name LIKE ?
                    OR phone LIKE ?
                    OR email LIKE ?
                    OR address LIKE ?
                )
            """
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw, kw])

        if status_filter and status_filter != "Tất cả":
            query += " AND status LIKE ?"
            params.append(f"%{status_filter}%")

        query += " ORDER BY reader_id ASC"

        readers = []
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                readers.append(
                    Reader(
                        reader_id=row[0],
                        card_number=row[1],
                        full_name=row[2],
                        gender=row[3] or "Nam",
                        dob=row[4],
                        phone=row[5],
                        email=row[6] or "",
                        address=row[7] or "",
                        status=row[8],
                        is_active=bool(row[9]),
                        created_at=row[10],
                    )
                )
        return readers

    @staticmethod
    def get_by_id(reader_id: int) -> Optional[Reader]:
        query = """
            SELECT reader_id, card_number, full_name, gender, dob, phone, email, address, status, is_active, created_at
            FROM Readers
            WHERE reader_id = ? AND is_active = 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (reader_id,))
            row = cursor.fetchone()
            if row:
                return Reader(
                    reader_id=row[0],
                    card_number=row[1],
                    full_name=row[2],
                    gender=row[3] or "Nam",
                    dob=row[4],
                    phone=row[5],
                    email=row[6] or "",
                    address=row[7] or "",
                    status=row[8],
                    is_active=bool(row[9]),
                    created_at=row[10],
                )
        return None

    @staticmethod
    def insert(reader: Reader) -> None:
        query = """
            INSERT INTO Readers (card_number, full_name, gender, dob, phone, email, address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    reader.card_number,
                    reader.full_name,
                    reader.gender,
                    reader.dob,
                    reader.phone,
                    reader.email or None,
                    reader.address or None,
                    reader.status,
                ),
            )

    @staticmethod
    def update(reader: Reader) -> None:
        query = """
            UPDATE Readers
            SET card_number = ?, full_name = ?, gender = ?, dob = ?,
                phone = ?, email = ?, address = ?, status = ?
            WHERE reader_id = ?
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    reader.card_number,
                    reader.full_name,
                    reader.gender,
                    reader.dob,
                    reader.phone,
                    reader.email or None,
                    reader.address or None,
                    reader.status,
                    reader.reader_id,
                ),
            )

    @staticmethod
    def soft_delete(reader_id: int) -> None:
        query = "UPDATE Readers SET is_active = 0 WHERE reader_id = ?"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (reader_id,))
