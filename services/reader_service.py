from typing import List
from dao.reader_dao import ReaderDAO
from models.reader import Reader


class ReaderService:
    """Tầng xử lý nghiệp vụ quản lý Độc giả (chỉ gọi qua ReaderDAO)"""

    @staticmethod
    def get_all_readers(keyword: str = "", status_filter: str = "Tất cả") -> List[Reader]:
        return ReaderDAO.get_all(keyword=keyword.strip(), status_filter=status_filter)

    @staticmethod
    def _validate_reader(reader: Reader) -> Reader:
        reader.card_number = (reader.card_number or "").strip()
        reader.full_name = (reader.full_name or "").strip()
        reader.phone = (reader.phone or "").strip()
        reader.email = (reader.email or "").strip()
        reader.address = (reader.address or "").strip()

        if not reader.card_number or not reader.full_name or not reader.phone:
            raise ValueError("Mã thẻ, Họ tên và Số điện thoại không được để trống!")

        if (
            not reader.email
            or not reader.email.lower().endswith("@gmail.com")
            or reader.email.count("@") != 1
            or reader.email.startswith("@")
            or " " in reader.email
        ):
            raise ValueError("Email không hợp lệ! Email bắt buộc phải có đuôi @gmail.com.")

        if reader.gender not in ("Nam", "Nữ", "Khác"):
            reader.gender = "Nam"

        if reader.status not in ("Hoạt động", "Khóa thẻ"):
            reader.status = "Hoạt động"

        return reader

    @staticmethod
    def add_reader(reader: Reader) -> None:
        validated = ReaderService._validate_reader(reader)
        ReaderDAO.insert(validated)

    @staticmethod
    def update_reader(reader: Reader) -> None:
        if not reader.reader_id:
            raise ValueError("Thiếu ID độc giả cần cập nhật!")
        validated = ReaderService._validate_reader(reader)
        ReaderDAO.update(validated)

    @staticmethod
    def delete_reader(reader_id: int) -> None:
        if not reader_id:
            raise ValueError("Thiếu ID độc giả cần xóa!")
        ReaderDAO.soft_delete(reader_id)
