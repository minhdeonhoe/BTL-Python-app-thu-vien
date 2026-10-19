import os
import pyodbc
from dotenv import load_dotenv
from contextlib import contextmanager

# Đọc cấu hình từ file .env
load_dotenv()

class DatabaseConnection:
    @staticmethod
    def get_connection():
        driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
        server = os.getenv("DB_SERVER", r"MINH\SQLEXPRESS")
        database = os.getenv("DB_NAME", "LibraryManagementDB")
        user = os.getenv("DB_USER", "sa")
        password = os.getenv("DB_PASSWORD", "")

        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
        )

        try:
            conn = pyodbc.connect(conn_str, timeout=5)
            return conn
        except pyodbc.Error as ex:
            print(f"[!] Lỗi kết nối CSDL: {ex}")
            raise ex

@contextmanager
def get_db_cursor(commit: bool = False):
    """Context manager tự động mở kết nối, cấp cursor và đóng an toàn"""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()