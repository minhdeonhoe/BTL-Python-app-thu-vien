from typing import List, Optional
from dao.user_dao import UserDAO
from models.user import User


class AuthService:

    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        clean_user = username.strip()
        clean_pwd = password.strip()
        if not clean_user or not clean_pwd:
            return None
        return UserDAO.get_by_credentials(clean_user, clean_pwd)

    @staticmethod
    def get_all_users(keyword: str = "", role_filter: str = "Tất cả") -> List[User]:
        return UserDAO.get_all(keyword=keyword.strip(), role_filter=role_filter)

    @staticmethod
    def _validate_user(user: User, is_edit: bool = False) -> User:
        user.username = (user.username or "").strip()
        user.password_hash = (user.password_hash or "").strip()
        user.full_name = (user.full_name or "").strip()
        user.email = (user.email or "").strip()

        if not user.username or not user.password_hash or not user.full_name:
            raise ValueError("Tên đăng nhập, Mật khẩu và Họ tên không được để trống!")

        if (
            not user.email
            or not user.email.lower().endswith("@gmail.com")
            or user.email.count("@") != 1
            or user.email.startswith("@")
            or " " in user.email
        ):
            raise ValueError("Email không hợp lệ! Email bắt buộc phải có đuôi @gmail.com.")

        if user.role not in ("Admin", "Librarian"):
            raise ValueError("Quyền (Role) chỉ được phép là 'Admin' hoặc 'Librarian'!")

        existing = UserDAO.get_by_username(user.username)
        if existing:
            if not is_edit or existing.user_id != user.user_id:
                raise ValueError(f"Tên đăng nhập '{user.username}' đã tồn tại trong hệ thống!")

        return user

    @staticmethod
    def add_user(current_user: User, new_user: User) -> None:
        if current_user.role != "Admin":
            raise PermissionError("Chỉ Quản trị viên (Admin) mới có quyền thêm tài khoản!")
        if new_user.role == "Admin":
            raise ValueError("Hệ thống chỉ cho phép duy nhất 1 Admin! Chỉ được thêm tài khoản Thủ thư (Librarian).")
        new_user.role = "Librarian"

        validated = AuthService._validate_user(new_user, is_edit=False)
        UserDAO.insert(validated)

    @staticmethod
    def update_user(current_user: User, target_user: User) -> None:
        if current_user.role != "Admin":
            raise PermissionError("Chỉ Quản trị viên (Admin) mới có quyền cập nhật tài khoản!")
        if not target_user.user_id:
            raise ValueError("Thiếu ID tài khoản cần cập nhật!")

        original_user = UserDAO.get_by_id(target_user.user_id)
        if not original_user:
            raise ValueError("Không tìm thấy tài khoản cần cập nhật!")
        if original_user.role == "Admin" or target_user.user_id == current_user.user_id:
            if target_user.role != "Admin":
                raise ValueError("Tài khoản Admin duy nhất không thể tự chuyển hoặc hạ quyền của mình!")
            if not target_user.is_active:
                raise ValueError("Không thể khóa tài khoản Admin duy nhất của hệ thống!")
            target_user.role = "Admin"
            target_user.is_active = True
        else:
            # Nếu là tài khoản Thủ thư: không được chuyển quyền thành Admin
            if target_user.role == "Admin":
                raise ValueError("Hệ thống chỉ có duy nhất 1 Admin, không thể chuyển quyền Admin cho tài khoản khác!")
            target_user.role = "Librarian"

        validated = AuthService._validate_user(target_user, is_edit=True)
        UserDAO.update(validated)

    @staticmethod
    def toggle_user_status(current_user: User, target_user_id: int, is_active: bool) -> None:
        if current_user.role != "Admin":
            raise PermissionError("Chỉ Quản trị viên (Admin) mới có quyền khóa/mở khóa tài khoản!")

        target_user = UserDAO.get_by_id(target_user_id)
        if not target_user:
            raise ValueError("Không tìm thấy tài khoản!")

        if target_user.role == "Admin" or target_user_id == current_user.user_id:
            raise ValueError("Không thể khóa tài khoản Admin duy nhất của hệ thống!")

        UserDAO.set_active_status(target_user_id, is_active)
