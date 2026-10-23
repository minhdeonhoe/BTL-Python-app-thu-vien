from tkinter import ttk, messagebox
from typing import Optional
import customtkinter as ctk
from models.user import User
from services.auth_service import AuthService
from utils.helpers import apply_treeview_style, center_window, format_date


class UserFormDialog(ctk.CTkToplevel):

    def __init__(self, master, current_user: User, on_save_callback, target_user: Optional[User] = None):
        super().__init__(master)
        self.current_user = current_user
        self.on_save_callback = on_save_callback
        self.target_user = target_user
        self.is_edit = target_user is not None
        self.is_editing_admin = self.is_edit and target_user.role == "Admin"

        self.title("Cập nhật tài khoản" if self.is_edit else "Thêm tài khoản Thủ thư")
        center_window(self, 480, 460)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._build_form()
        if self.is_edit:
            self._populate_data()

    def _build_form(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        header = ctk.CTkLabel(
            container,
            text="✏️ Cập nhật tài khoản" if self.is_edit else "➕ Thêm tài khoản Thủ thư",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
        )
        header.pack(anchor="w", pady=(0, 15))

        form_grid = ctk.CTkFrame(container, fg_color="transparent")
        form_grid.pack(fill="both", expand=True)
        form_grid.grid_columnconfigure(1, weight=1)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

       
        ctk.CTkLabel(form_grid, text="Tên đăng nhập (*):", font=input_font).grid(row=0, column=0, sticky="w", pady=7, padx=(0, 12))
        self.username_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: thuthu3", height=34, font=input_font)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=7)

        
        ctk.CTkLabel(form_grid, text="Mật khẩu (*):", font=input_font).grid(row=1, column=0, sticky="w", pady=7, padx=(0, 12))
        self.password_entry = ctk.CTkEntry(form_grid, placeholder_text="Nhập mật khẩu", height=34, font=input_font)
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=7)

       
        ctk.CTkLabel(form_grid, text="Họ và tên (*):", font=input_font).grid(row=2, column=0, sticky="w", pady=7, padx=(0, 12))
        self.fullname_entry = ctk.CTkEntry(form_grid, placeholder_text="Nhập họ và tên nhân sự", height=34, font=input_font)
        self.fullname_entry.grid(row=2, column=1, sticky="ew", pady=7)

       
        ctk.CTkLabel(form_grid, text="Email (*):", font=input_font).grid(row=3, column=0, sticky="w", pady=7, padx=(0, 12))
        self.email_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: staff@gmail.com", height=34, font=input_font)
        self.email_entry.grid(row=3, column=1, sticky="ew", pady=7)

        
        ctk.CTkLabel(form_grid, text="Vai trò (Role):", font=input_font).grid(row=4, column=0, sticky="w", pady=7, padx=(0, 12))
        fixed_role = "Admin" if self.is_editing_admin else "Librarian"
        self.role_cb = ctk.CTkComboBox(form_grid, values=[fixed_role], height=34, font=input_font)
        self.role_cb.set(fixed_role)
        self.role_cb.configure(state="disabled")
        self.role_cb.grid(row=4, column=1, sticky="ew", pady=7)

       
        ctk.CTkLabel(form_grid, text="Trạng thái:", font=input_font).grid(row=5, column=0, sticky="w", pady=7, padx=(0, 12))
        self.status_cb = ctk.CTkComboBox(form_grid, values=["Đang hoạt động", "Đã khóa"], height=34, font=input_font)
        self.status_cb.set("Đang hoạt động")
        if self.is_editing_admin:
            self.status_cb.configure(state="disabled")
        self.status_cb.grid(row=5, column=1, sticky="ew", pady=7)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_frame,
            text="Hủy",
            fg_color="gray50",
            hover_color="gray40",
            width=105,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="Lưu tài khoản",
            width=140,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._handle_save,
        ).pack(side="right")

    def _populate_data(self):
        u = self.target_user
        self.username_entry.insert(0, u.username or "")
        self.password_entry.insert(0, u.password_hash or "")
        self.fullname_entry.insert(0, u.full_name or "")
        self.email_entry.insert(0, u.email or "")
        self.status_cb.set("Đang hoạt động" if u.is_active else "Đã khóa")

    def _handle_save(self):
        fixed_role = "Admin" if self.is_editing_admin else "Librarian"
        is_active_val = True if self.is_editing_admin else (self.status_cb.get() == "Đang hoạt động")
        email = self.email_entry.get().strip()

        if (
            not email
            or not email.lower().endswith("@gmail.com")
            or email.count("@") != 1
            or email.startswith("@")
            or " " in email
        ):
            messagebox.showwarning(
                "Sai định dạng Email",
                "Email bắt buộc phải có đuôi @gmail.com (VD: staff@gmail.com)!",
                parent=self,
            )
            return

        user_obj = User(
            user_id=self.target_user.user_id if self.is_edit else None,
            username=self.username_entry.get().strip(),
            password_hash=self.password_entry.get().strip(),
            full_name=self.fullname_entry.get().strip(),
            email=email,
            role=fixed_role,
            is_active=is_active_val,
        )

        try:
            if self.is_edit:
                AuthService.update_user(self.current_user, user_obj)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin tài khoản!", parent=self)
            else:
                AuthService.add_user(self.current_user, user_obj)
                messagebox.showinfo("Thành công", "Đã thêm tài khoản Thủ thư mới!", parent=self)

            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi lưu tài khoản", str(e), parent=self)


class UserView(ctk.CTkFrame):
    """Màn hình Quản lý Tài khoản hệ thống (1 Admin duy nhất & các Thủ thư) - Chỉ dành cho Admin"""

    def __init__(self, master, current_user: User):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.users_cache = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 12))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="🛡️ Quản lý tài khoản & thủ thư",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        title_lbl.pack(side="left")

        toggle_btn = ctk.CTkButton(
            top_bar,
            text="🔒 Khóa / Mở khóa",
            fg_color="#d9534f",
            hover_color="#b52b27",
            width=135,
            command=self._toggle_selected_status,
        )
        toggle_btn.pack(side="right", padx=(8, 0))

        edit_btn = ctk.CTkButton(
            top_bar,
            text="✏️ Sửa tài khoản",
            fg_color="#f0ad4e",
            hover_color="#d58512",
            width=125,
            command=self._edit_selected,
        )
        edit_btn.pack(side="right", padx=(8, 0))

        add_btn = ctk.CTkButton(
            top_bar,
            text="➕ Thêm Thủ thư",
            fg_color="#28a745",
            hover_color="#1e7e34",
            width=145,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_add_dialog,
        )
        add_btn.pack(side="right")

        
        filter_bar = ctk.CTkFrame(self, corner_radius=10)
        filter_bar.pack(fill="x", pady=(0, 12), ipady=6)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Tìm theo tên đăng nhập, họ tên hoặc email...",
            width=340,
            height=34,
            font=input_font,
        )
        self.search_entry.pack(side="left", padx=(14, 10), pady=6)
        self.search_entry.bind("<Return>", lambda _: self.load_data())

        ctk.CTkLabel(filter_bar, text="Vai trò:", font=input_font).pack(side="left", padx=(6, 6))

        self.role_cb = ctk.CTkComboBox(
            filter_bar,
            values=["Tất cả", "Librarian", "Admin"],
            width=150,
            height=34,
            font=input_font,
            command=lambda _: self.load_data(),
        )
        self.role_cb.set("Tất cả")
        self.role_cb.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filter_bar,
            text="Tìm kiếm",
            width=95,
            height=34,
            command=self.load_data,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            filter_bar,
            text="Làm mới",
            width=90,
            height=34,
            fg_color="gray50",
            hover_color="gray40",
            command=self._reset_filters,
        ).pack(side="left")

        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        row_alt = apply_treeview_style()

        columns = ("user_id", "username", "full_name", "email", "role", "status", "created_at")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "user_id": ("ID", 55, "center"),
            "username": ("Tên đăng nhập", 140, "w"),
            "full_name": ("Họ và tên", 200, "w"),
            "email": ("Email", 200, "w"),
            "role": ("Vai trò (Role)", 130, "center"),
            "status": ("Trạng thái", 130, "center"),
            "created_at": ("Ngày tạo", 120, "center"),
        }
        for col, (text, width, anchor) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("alt", background=row_alt)
        self.tree.bind("<Double-1>", lambda _: self._edit_selected())

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side="right", fill="y", padx=8, pady=8)

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.role_cb.set("Tất cả")
        self.load_data()

    def load_data(self):
        try:
            keyword = self.search_entry.get().strip()
            role_filter = self.role_cb.get()
            users = AuthService.get_all_users(keyword=keyword, role_filter=role_filter)

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.users_cache.clear()
            for idx, u in enumerate(users):
                self.users_cache[u.user_id] = u
                tag = ("alt",) if idx % 2 == 1 else ()
                role_display = "Admin (Quản trị)" if u.role == "Admin" else "Librarian (Thủ thư)"
                status_display = "Đang hoạt động" if u.is_active else "Đã khóa"
                self.tree.insert(
                    "",
                    "end",
                    iid=str(u.user_id),
                    values=(
                        u.user_id,
                        u.username,
                        u.full_name,
                        u.email,
                        role_display,
                        status_display,
                        format_date(u.created_at),
                    ),
                    tags=tag,
                )
        except Exception as e:
            messagebox.showerror("Lỗi tải danh sách tài khoản", str(e))

    def _open_add_dialog(self):
        UserFormDialog(self, current_user=self.current_user, on_save_callback=self.load_data)

    def _edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn tài khoản", "Vui lòng chọn một tài khoản trong bảng để sửa!")
            return
        user_id = int(selected[0])
        target_user = self.users_cache.get(user_id)
        if target_user:
            UserFormDialog(
                self,
                current_user=self.current_user,
                on_save_callback=self.load_data,
                target_user=target_user,
            )

    def _toggle_selected_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn tài khoản", "Vui lòng chọn một tài khoản để khóa hoặc mở khóa!")
            return
        user_id = int(selected[0])
        target_user = self.users_cache.get(user_id)
        if not target_user:
            return

        if target_user.role == "Admin":
            messagebox.showwarning(
                "Không thể khóa Admin",
                "Đây là tài khoản Admin duy nhất của hệ thống, không thể khóa!",
            )
            return

        new_state = not target_user.is_active
        action_name = "MỞ KHÓA" if new_state else "KHÓA"
        confirm = messagebox.askyesno(
            f"Xác nhận {action_name}",
            f"Bạn có chắc chắn muốn {action_name} tài khoản '{target_user.username}' ({target_user.full_name}) không?",
        )
        if confirm:
            try:
                AuthService.toggle_user_status(self.current_user, user_id, new_state)
                self.load_data()
                messagebox.showinfo("Thành công", f"Đã {action_name.lower()} tài khoản '{target_user.username}'.")
            except Exception as e:
                messagebox.showerror("Không thể thực hiện", str(e))
