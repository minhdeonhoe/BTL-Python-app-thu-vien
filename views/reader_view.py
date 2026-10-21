from datetime import datetime
from tkinter import ttk, messagebox
from typing import Optional
import customtkinter as ctk
from models.reader import Reader
from models.user import User
from services.borrow_service import BorrowService
from services.reader_service import ReaderService
from utils.helpers import apply_treeview_style, center_window, format_currency, format_date


class ReaderBorrowHistoryDialog(ctk.CTkToplevel):
   

    def __init__(self, master, reader: Reader):
        super().__init__(master)
        self.reader = reader

        self.title(f"Thông tin & Lịch sử mượn trả - {reader.full_name}")
        center_window(self, 820, 500)
        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=18)
        info_card = ctk.CTkFrame(container, corner_radius=10)
        info_card.pack(fill="x", pady=(0, 14))

        r = self.reader
        header_lbl = ctk.CTkLabel(
            info_card,
            text=f"👤 Độc giả: {r.full_name} ({r.card_number}) — [{r.status}]",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )
        header_lbl.pack(anchor="w", padx=16, pady=(12, 4))

        details_text = (
            f"Giới tính: {r.gender}   |   Ngày sinh: {format_date(r.dob) or 'Chưa cập nhật'}   |   "
            f"SĐT: {r.phone}   |   Email: {r.email or 'Không có'}\n"
            f"Địa chỉ: {r.address or 'Chưa cập nhật'}"
        )
        ctk.CTkLabel(
            info_card,
            text=details_text,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
        ).pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(
            container,
            text="📜 Lịch sử Mượn - Trả của độc giả này:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 6))

        table_frame = ctk.CTkFrame(container, corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        row_alt = apply_treeview_style()
        columns = ("borrow_id", "book_title", "borrow_date", "due_date", "return_date", "status", "fine_amount", "staff_name")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "borrow_id": ("Mã phiếu", 70, "center"),
            "book_title": ("Tên sách", 210, "w"),
            "borrow_date": ("Ngày mượn", 95, "center"),
            "due_date": ("Hạn trả", 95, "center"),
            "return_date": ("Ngày trả", 95, "center"),
            "status": ("Trạng thái", 95, "center"),
            "fine_amount": ("Tiền phạt", 90, "e"),
            "staff_name": ("Thủ thư lập", 120, "w"),
        }
        for col, (text, width, anchor) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("alt", background=row_alt)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side="right", fill="y", padx=8, pady=8)
        try:
            borrows = BorrowService.get_borrows_by_reader(r.reader_id)
            for idx, br in enumerate(borrows):
                tag = ("alt",) if idx % 2 == 1 else ()
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        f"#{br.borrow_id}",
                        br.book_title,
                        format_date(br.borrow_date),
                        format_date(br.due_date),
                        format_date(br.return_date) or "-",
                        br.status,
                        format_currency(br.fine_amount),
                        br.staff_name,
                    ),
                    tags=tag,
                )
        except Exception as e:
            messagebox.showerror("Lỗi tải lịch sử", str(e), parent=self)

        ctk.CTkButton(
            container,
            text="Đóng",
            width=110,
            fg_color="gray50",
            hover_color="gray40",
            command=self.destroy,
        ).pack(anchor="e", pady=(12, 0))


class ReaderFormDialog(ctk.CTkToplevel):

    def __init__(self, master, on_save_callback, reader: Optional[Reader] = None):
        super().__init__(master)
        self.on_save_callback = on_save_callback
        self.reader = reader
        self.is_edit = reader is not None

        self.title("Cập nhật độc giả" if self.is_edit else "Thêm độc giả mới")
        center_window(self, 500, 520)
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
            text="✏️ Cập nhật độc giả" if self.is_edit else "➕ Thêm độc giả mới",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        header.pack(anchor="w", pady=(0, 15))

        form_grid = ctk.CTkFrame(container, fg_color="transparent")
        form_grid.pack(fill="both", expand=True)
        form_grid.grid_columnconfigure(1, weight=1)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

        ctk.CTkLabel(form_grid, text="Mã thẻ / MSSV (*):", font=input_font).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.card_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: SV2024005", height=34, font=input_font)
        self.card_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Họ và tên (*):", font=input_font).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.name_entry = ctk.CTkEntry(form_grid, placeholder_text="Nhập họ và tên độc giả", height=34, font=input_font)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Giới tính:", font=input_font).grid(row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        self.gender_cb = ctk.CTkComboBox(form_grid, values=["Nam", "Nữ", "Khác"], height=34, font=input_font)
        self.gender_cb.set("Nam")
        self.gender_cb.grid(row=2, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Ngày sinh (DD-MM-YYYY):", font=input_font).grid(row=3, column=0, sticky="w", pady=6, padx=(0, 12))
        self.dob_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: 15-05-2004", height=34, font=input_font)
        self.dob_entry.grid(row=3, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Số điện thoại (*):", font=input_font).grid(row=4, column=0, sticky="w", pady=6, padx=(0, 12))
        self.phone_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: 0901234567", height=34, font=input_font)
        self.phone_entry.grid(row=4, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Email (*):", font=input_font).grid(row=5, column=0, sticky="w", pady=6, padx=(0, 12))
        self.email_entry = ctk.CTkEntry(form_grid, placeholder_text="VD: example@gmail.com", height=34, font=input_font)
        self.email_entry.grid(row=5, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Địa chỉ:", font=input_font).grid(row=6, column=0, sticky="w", pady=6, padx=(0, 12))
        self.address_entry = ctk.CTkEntry(form_grid, placeholder_text="Nhập địa chỉ", height=34, font=input_font)
        self.address_entry.grid(row=6, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Trạng thái thẻ:", font=input_font).grid(row=7, column=0, sticky="w", pady=6, padx=(0, 12))
        self.status_cb = ctk.CTkComboBox(form_grid, values=["Hoạt động", "Khóa thẻ"], height=34, font=input_font)
        self.status_cb.set("Hoạt động")
        self.status_cb.grid(row=7, column=1, sticky="ew", pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_frame,
            text="Hủy",
            fg_color="gray50",
            hover_color="gray40",
            width=110,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="Lưu độc giả",
            width=140,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._handle_save,
        ).pack(side="right")

    def _populate_data(self):
        r = self.reader
        self.card_entry.insert(0, r.card_number or "")
        self.name_entry.insert(0, r.full_name or "")
        self.gender_cb.set(r.gender or "Nam")
        if r.dob:
            self.dob_entry.insert(0, format_date(r.dob))
        self.phone_entry.insert(0, r.phone or "")
        self.email_entry.insert(0, r.email or "")
        self.address_entry.insert(0, r.address or "")
        self.status_cb.set(r.status or "Hoạt động")

    def _handle_save(self):
        card_number = self.card_entry.get().strip()
        full_name = self.name_entry.get().strip()
        gender = self.gender_cb.get()
        dob_str = self.dob_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()
        status = self.status_cb.get()

        if not card_number or not full_name or not phone:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ Mã thẻ, Họ tên và Số điện thoại!",
                parent=self,
            )
            return

        if (
            not email
            or not email.lower().endswith("@gmail.com")
            or email.count("@") != 1
            or email.startswith("@")
            or " " in email
        ):
            messagebox.showwarning(
                "Sai định dạng Email",
                "Email bắt buộc phải có đuôi @gmail.com (VD: example@gmail.com)!",
                parent=self,
            )
            return

        dob_val = None
        if dob_str:
            try:
                dob_val = datetime.strptime(dob_str, "%d-%m-%Y").date()
            except ValueError:
                messagebox.showwarning(
                    "Sai định dạng ngày",
                    "Ngày sinh phải có định dạng DD-MM-YYYY (VD: 15-05-2004)!",
                    parent=self,
                )
                return

        reader_obj = Reader(
            reader_id=self.reader.reader_id if self.is_edit else None,
            card_number=card_number,
            full_name=full_name,
            gender=gender,
            dob=dob_val,
            phone=phone,
            email=email,
            address=address,
            status=status,
        )

        try:
            if self.is_edit:
                ReaderService.update_reader(reader_obj)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin độc giả!", parent=self)
            else:
                ReaderService.add_reader(reader_obj)
                messagebox.showinfo("Thành công", "Đã thêm độc giả mới!", parent=self)

            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu thông tin độc giả:\n{e}", parent=self)


class ReaderView(ctk.CTkFrame):

    def __init__(self, master, current_user: User):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.is_admin = current_user.role == "Admin"
        self.readers_cache = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 12))

        title_text = "👥 Quản lý độc giả" if self.is_admin else "👥 Tra cứu độc giả & lịch sử mượn"
        title_lbl = ctk.CTkLabel(
            top_bar,
            text=title_text,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        title_lbl.pack(side="left")

        history_btn = ctk.CTkButton(
            top_bar,
            text="📜 Xem lịch sử mượn trả",
            fg_color="#17a2b8",
            hover_color="#117a8b",
            width=170,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._view_reader_history,
        )
        history_btn.pack(side="right", padx=(8, 0))
        if self.is_admin:
            del_btn = ctk.CTkButton(
                top_bar,
                text="🗑️ Xóa độc giả",
                fg_color="#d9534f",
                hover_color="#b52b27",
                width=120,
                command=self._delete_selected,
            )
            del_btn.pack(side="right", padx=(8, 0))

            edit_btn = ctk.CTkButton(
                top_bar,
                text="✏️ Sửa thông tin",
                fg_color="#f0ad4e",
                hover_color="#d58512",
                width=125,
                command=self._edit_selected,
            )
            edit_btn.pack(side="right", padx=(8, 0))

            add_btn = ctk.CTkButton(
                top_bar,
                text="➕ Thêm độc giả",
                fg_color="#28a745",
                hover_color="#1e7e34",
                width=135,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                command=lambda: ReaderFormDialog(self, on_save_callback=self.load_data),
            )
            add_btn.pack(side="right")

        filter_bar = ctk.CTkFrame(self, corner_radius=10)
        filter_bar.pack(fill="x", pady=(0, 12), ipady=6)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Tìm theo mã thẻ, họ tên hoặc số điện thoại...",
            width=340,
            height=34,
            font=input_font,
        )
        self.search_entry.pack(side="left", padx=(14, 10), pady=6)
        self.search_entry.bind("<Return>", lambda _: self.load_data())

        ctk.CTkLabel(filter_bar, text="Trạng thái:", font=input_font).pack(side="left", padx=(6, 6))

        self.status_cb = ctk.CTkComboBox(
            filter_bar,
            values=["Tất cả", "Hoạt động", "Khóa thẻ"],
            width=150,
            height=34,
            font=input_font,
            command=lambda _: self.load_data(),
        )
        self.status_cb.set("Tất cả")
        self.status_cb.pack(side="left", padx=(0, 10))

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

        columns = ("reader_id", "card_number", "full_name", "gender", "dob", "phone", "email", "address", "status")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "reader_id": ("ID", 50, "center"),
            "card_number": ("Mã thẻ", 110, "center"),
            "full_name": ("Họ và tên", 170, "w"),
            "gender": ("Giới tính", 75, "center"),
            "dob": ("Ngày sinh", 100, "center"),
            "phone": ("Điện thoại", 110, "center"),
            "email": ("Email", 160, "w"),
            "address": ("Địa chỉ", 170, "w"),
            "status": ("Trạng thái", 100, "center"),
        }
        for col, (text, width, anchor) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("alt", background=row_alt)
        self.tree.bind(
            "<Double-1>",
            lambda _: self._edit_selected() if self.is_admin else self._view_reader_history(),
        )

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side="right", fill="y", padx=8, pady=8)

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_cb.set("Tất cả")
        self.load_data()

    def load_data(self):
        try:
            keyword = self.search_entry.get().strip()
            status_filter = self.status_cb.get()
            readers = ReaderService.get_all_readers(keyword=keyword, status_filter=status_filter)

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.readers_cache.clear()
            for idx, r in enumerate(readers):
                self.readers_cache[r.reader_id] = r
                tag = ("alt",) if idx % 2 == 1 else ()
                self.tree.insert(
                    "",
                    "end",
                    iid=str(r.reader_id),
                    values=(
                        r.reader_id,
                        r.card_number,
                        r.full_name,
                        r.gender,
                        format_date(r.dob),
                        r.phone,
                        r.email,
                        r.address,
                        r.status,
                    ),
                    tags=tag,
                )
        except Exception as e:
            messagebox.showerror("Lỗi tải dữ liệu độc giả", str(e))

    def _view_reader_history(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Chưa chọn độc giả",
                "Vui lòng chọn một độc giả trong bảng để kiểm tra thông tin và lịch sử mượn trả!",
            )
            return
        reader_id = int(selected[0])
        reader = self.readers_cache.get(reader_id)
        if reader:
            ReaderBorrowHistoryDialog(self, reader=reader)

    def _edit_selected(self):
        if not self.is_admin:
            messagebox.showwarning("Không đủ quyền", "Chỉ Admin mới có quyền chỉnh sửa thông tin độc giả!")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn độc giả", "Vui lòng chọn một độc giả trong bảng để sửa!")
            return
        reader_id = int(selected[0])
        reader = self.readers_cache.get(reader_id)
        if reader:
            ReaderFormDialog(self, on_save_callback=self.load_data, reader=reader)

    def _delete_selected(self):
        if not self.is_admin:
            messagebox.showwarning("Không đủ quyền", "Chỉ Admin mới có quyền xóa độc giả!")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn độc giả", "Vui lòng chọn một độc giả cần xóa!")
            return
        reader_id = int(selected[0])
        reader = self.readers_cache.get(reader_id)
        if not reader:
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa mềm",
            f"Bạn có chắc chắn muốn ẩn/xóa độc giả:\n'{reader.full_name}' ({reader.card_number}) không?",
        )
        if confirm:
            try:
                ReaderService.delete_reader(reader_id)
                self.load_data()
                messagebox.showinfo("Thành công", "Đã xóa mềm độc giả khỏi danh sách.")
            except Exception as e:
                messagebox.showerror("Lỗi khi xóa", str(e))
