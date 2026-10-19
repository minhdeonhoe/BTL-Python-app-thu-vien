from tkinter import messagebox
import customtkinter as ctk
from services.auth_service import AuthService


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # Khung thẻ đăng nhập ở chính giữa
        card = ctk.CTkFrame(self, width=420, height=470, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Tiêu đề & biểu tượng
        title_lbl = ctk.CTkLabel(
            card,
            text="📚 Hệ thống Thư viện",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        )
        title_lbl.pack(pady=(35, 6))

        subtitle_lbl = ctk.CTkLabel(
            card,
            text="Đăng nhập để tiếp tục quản lý",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            text_color=("gray40", "gray70"),
        )
        subtitle_lbl.pack(pady=(0, 28))

        # Tài khoản
        user_lbl = ctk.CTkLabel(
            card,
            text="Tên đăng nhập",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            anchor="w",
        )
        user_lbl.pack(fill="x", padx=40, pady=(0, 4))

        self.username_entry = ctk.CTkEntry(
            card,
            placeholder_text="Nhập tên đăng nhập",
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
        )
        self.username_entry.pack(fill="x", padx=40, pady=(0, 16))

        # Mật khẩu
        pwd_lbl = ctk.CTkLabel(
            card,
            text="Mật khẩu",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            anchor="w",
        )
        pwd_lbl.pack(fill="x", padx=40, pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Nhập mật khẩu",
            show="•",
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
        )
        self.password_entry.pack(fill="x", padx=40, pady=(0, 24))

        # Nút Đăng nhập
        login_btn = ctk.CTkButton(
            card,
            text="Đăng nhập",
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._handle_login,
        )
        login_btn.pack(fill="x", padx=40, pady=(0, 16))

        # Gợi ý tài khoản mẫu từ library.sql
        # hint_lbl = ctk.CTkLabel(
        #     card,
        #     text="Tài khoản mẫu: admin / 123456 hoặc thuthu1 / 123456",
        #     font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),
        #     text_color=("gray45", "gray65"),
        # )
        # hint_lbl.pack(pady=(6, 0))

        # Bắt sự kiện nhấn phím Enter
        self.username_entry.bind("<Return>", lambda _: self._handle_login())
        self.password_entry.bind("<Return>", lambda _: self._handle_login())

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return

        try:
            user = AuthService.login(username, password)
            if user:
                self.on_login_success(user)
            else:
                messagebox.showerror(
                    "Đăng nhập thất bại",
                    "Tên đăng nhập hoặc mật khẩu không chính xác, hoặc tài khoản đã bị khóa!",
                )
        except Exception as e:
            messagebox.showerror(
                "Lỗi kết nối CSDL",
                f"Không thể kết nối tới SQL Server.\nHãy kiểm tra file .env và database LibraryManagementDB.\n\nChi tiết: {e}",
            )
