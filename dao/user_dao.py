from typing import List, Optional
from config.database import get_db_cursor
from models.user import User


class UserDAO:
    """Tầng truy cập dữ liệu (DAO) cho bảng Users"""

    @staticmethod
    def get_by_credentials(username: str, password_hash: str) -> Optional[User]:
        query = """
            SELECT user_id, username, password_hash, full_name, email, role, is_active, created_at
            FROM Users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (username, password_hash))
            row = cursor.fetchone()
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    full_name=row[3],
                    email=row[4] or "",
                    role=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                )
        return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        query = """
            SELECT user_id, username, password_hash, full_name, email, role, is_active, created_at
            FROM Users
            WHERE user_id = ?
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    full_name=row[3],
                    email=row[4] or "",
                    role=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                )
        return None

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        query = """
            SELECT user_id, username, password_hash, full_name, email, role, is_active, created_at
            FROM Users
            WHERE username = ?
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    full_name=row[3],
                    email=row[4] or "",
                    role=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                )
        return None

    @staticmethod
    def get_all(keyword: str = "", role_filter: str = "Tất cả") -> List[User]:
        query = """
            SELECT user_id, username, password_hash, full_name, email, role, is_active, created_at
            FROM Users
            WHERE 1=1
        """
        params = []
        if keyword:
            query += " AND (username LIKE ? OR full_name LIKE ? OR email LIKE ? OR role LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw])

        if role_filter and role_filter != "Tất cả":
            query += " AND role LIKE ?"
            params.append(f"%{role_filter}%")

        query += " ORDER BY user_id DESC"

        users = []
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                users.append(
                    User(
                        user_id=row[0],
                        username=row[1],
                        password_hash=row[2],
                        full_name=row[3],
                        email=row[4] or "",
                        role=row[5],
                        is_active=bool(row[6]),
                        created_at=row[7],
                    )
                )
        return users

    @staticmethod
    def insert(user: User) -> None:
        query = """
            INSERT INTO Users (username, password_hash, full_name, email, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    user.username,
                    user.password_hash,
                    user.full_name,
                    user.email or None,
                    user.role,
                    1 if user.is_active else 0,
                ),
            )

    @staticmethod
    def update(user: User) -> None:
        query = """
            UPDATE Users
            SET username = ?, password_hash = ?, full_name = ?, email = ?, role = ?, is_active = ?
            WHERE user_id = ?
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    user.username,
                    user.password_hash,
                    user.full_name,
                    user.email or None,
                    user.role,
                    1 if user.is_active else 0,
                    user.user_id,
                ),
            )

    @staticmethod
    def set_active_status(user_id: int, is_active: bool) -> None:
        query = "UPDATE Users SET is_active = ? WHERE user_id = ?"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (1 if is_active else 0, user_id))
