import customtkinter as ctk
from models.user import User
from utils.helpers import center_window, enable_ime_font_fix
from views.login_view import LoginView
from views.main_view import MainView


class LibraryApp(ctk.CTk):
    """Cửa sổ gốc điều phối luồng màn hình Đăng nhập <-> Màn hình chính"""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.title("Hệ thống Quản lý Thư viện - LibraryManagement")
        self.minsize(1100, 680)
        center_window(self, 1220, 720)

        enable_ime_font_fix(self)

        self.active_view = None
        self.show_login()

    def show_login(self):
        if self.active_view is not None:
            self.active_view.destroy()
        self.active_view = LoginView(self, on_login_success=self.show_main)
        self.active_view.pack(fill="both", expand=True)

    def show_main(self, user: User):
        if self.active_view is not None:
            self.active_view.destroy()
        self.active_view = MainView(self, current_user=user, on_logout=self.show_login)
        self.active_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()

