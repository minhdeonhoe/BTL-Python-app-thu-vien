from tkinter import ttk, messagebox
import customtkinter as ctk
from models.user import User
from services.borrow_service import BorrowService
from utils.helpers import apply_treeview_style, format_currency, format_date
from views.book_view import BookView
from views.borrow_view import BorrowView
from views.reader_view import ReaderView
from views.user_view import UserView


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build_ui()
        self.load_dashboard()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 14))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="🏠 Tổng quan hệ thống thư viện",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        title_lbl.pack(side="left")

        refresh_btn = ctk.CTkButton(
            top_bar,
            text="🔄 Làm mới số liệu",
            width=140,
            height=34,
            command=self.load_dashboard,
        )
        refresh_btn.pack(side="right")

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 18))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat")

        self.card_total_books = self._create_stat_card(
            cards_frame, 0, "📘 Đầu sách & Bản sẵn có", "0 / 0", "#1f538d"
        )
        self.card_readers = self._create_stat_card(
            cards_frame, 1, "👥 Độc giả hoạt động", "0", "#28a745"
        )
        self.card_borrows = self._create_stat_card(
            cards_frame, 2, "📋 Phiếu đang mượn", "0", "#f0ad4e"
        )
        self.card_overdue = self._create_stat_card(
            cards_frame, 3, "⚠️ Phiếu quá hạn", "0", "#d9534f"
        )

        recent_lbl = ctk.CTkLabel(
            self,
            text="📌 Hoạt động Mượn - Trả gần đây",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )
        recent_lbl.pack(anchor="w", pady=(4, 8))

        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        row_alt = apply_treeview_style()
        columns = ("borrow_id", "reader_name", "book_title", "borrow_date", "due_date", "status", "fine")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "borrow_id": ("Mã phiếu", 80, "center"),
            "reader_name": ("Độc giả", 180, "w"),
            "book_title": ("Tên sách", 240, "w"),
            "borrow_date": ("Ngày mượn", 110, "center"),
            "due_date": ("Hạn trả", 110, "center"),
            "status": ("Trạng thái", 110, "center"),
            "fine": ("Tiền phạt", 110, "e"),
        }
        for col, (text, width, anchor) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("alt", background=row_alt)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def _create_stat_card(self, parent, col: int, title: str, value: str, accent_color: str):
        card = ctk.CTkFrame(parent, corner_radius=12, height=110)
        card.grid(row=0, column=col, sticky="ew", padx=6)
        card.pack_propagate(False)

        strip = ctk.CTkFrame(card, height=6, fg_color=accent_color, corner_radius=4)
        strip.pack(fill="x", padx=12, pady=(10, 8))

        lbl_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray35", "gray75"),
        )
        lbl_title.pack(anchor="w", padx=16)

        lbl_val = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        )
        lbl_val.pack(anchor="w", padx=16, pady=(4, 0))
        return lbl_val

    def load_dashboard(self):
        try:
            stats = BorrowService.get_dashboard_stats()
            self.card_total_books.configure(
                text=f"{stats['total_books']} đầu ({stats['available_books']} cuốn)"
            )
            self.card_readers.configure(text=str(stats["total_readers"]))
            self.card_borrows.configure(text=str(stats["active_borrows"]))
            self.card_overdue.configure(text=str(stats["overdue_borrows"]))

            for item in self.tree.get_children():
                self.tree.delete(item)

            recent_borrows = BorrowService.get_all_borrows()[:15]
            for idx, br in enumerate(recent_borrows):
                tag = ("alt",) if idx % 2 == 1 else ()
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        f"#{br.borrow_id}",
                        f"{br.reader_name} ({br.card_number})",
                        br.book_title,
                        format_date(br.borrow_date),
                        format_date(br.due_date),
                        br.status,
                        format_currency(br.fine_amount),
                    ),
                    tags=tag,
                )
        except Exception as e:
            messagebox.showerror("Lỗi tải thống kê", str(e))


class MainView(ctk.CTkFrame):
   

    def __init__(self, master, current_user: User, on_logout):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.current_frame = None

        self._build_layout()
        self.switch_tab("dashboard")

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand_lbl = ctk.CTkLabel(
            self.sidebar,
            text="📚 LIBRARY",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        brand_lbl.pack(pady=(24, 6), padx=20, anchor="w")


        user_card = ctk.CTkFrame(self.sidebar, corner_radius=10)
        user_card.pack(fill="x", padx=16, pady=(6, 20))

        ctk.CTkLabel(
            user_card,
            text=f"👤 {self.current_user.full_name}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 2))

        is_admin = self.current_user.role == "Admin"
        role_vn = "Quản trị viên (Admin)" if is_admin else "Thủ thư (Librarian)"
        ctk.CTkLabel(
            user_card,
            text=f"Quyền: {role_vn}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray70"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))
        reader_label = "👥  Quản lý Độc giả"
        menu_items = [
            ("dashboard", "🏠  Tổng quan"),
            ("books", "📘  Quản lý Sách"),
            ("readers", reader_label),
            ("borrows", "📋  Mượn - Trả sách"),
        ]
        if is_admin:
            menu_items.append(("users", "🛡  Quản lý Tài khoản"))

        for key, label in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=42,
                corner_radius=8,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                fg_color="transparent",
                text_color=("gray15", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self.switch_tab(k),
            )
            btn.pack(fill="x", padx=16, pady=4)
            self.nav_buttons[key] = btn

        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Đăng xuất",
            fg_color="#d9534f",
            hover_color="#b52b27",
            height=38,
            command=self.on_logout,
        )
        logout_btn.pack(side="bottom", fill="x", padx=16, pady=(8, 20))


        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(side="left", fill="both", expand=True, padx=20, pady=18)

    def switch_tab(self, tab_key: str):
        for key, btn in self.nav_buttons.items():
            if key == tab_key:
                btn.configure(fg_color=("#1f538d", "#1f538d"), text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=("gray15", "gray90"))

        if self.current_frame is not None:
            self.current_frame.destroy()

        if tab_key == "dashboard":
            self.current_frame = DashboardFrame(self.content_area)
        elif tab_key == "books":
            self.current_frame = BookView(self.content_area)
        elif tab_key == "readers":
            self.current_frame = ReaderView(self.content_area, current_user=self.current_user)
        elif tab_key == "borrows":
            self.current_frame = BorrowView(self.content_area, current_user=self.current_user)
        elif tab_key == "users" and self.current_user.role == "Admin":
            self.current_frame = UserView(self.content_area, current_user=self.current_user)

        if self.current_frame is not None:
            self.current_frame.pack(fill="both", expand=True)
