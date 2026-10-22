from datetime import date, datetime, timedelta
from tkinter import ttk, messagebox
import customtkinter as ctk
from models.borrow import Borrow
from models.user import User
from services.book_service import BookService
from services.borrow_service import BorrowService
from services.reader_service import ReaderService
from utils.helpers import apply_treeview_style, center_window, format_currency, format_date


class CreateBorrowDialog(ctk.CTkToplevel):

    def __init__(self, master, current_user: User, on_save_callback):
        super().__init__(master)
        self.current_user = current_user
        self.on_save_callback = on_save_callback

        self.title("Lập phiếu mượn sách")
        center_window(self, 560, 470)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.readers_map = {}
        self.books_map = {}
        self._build_form()
        self._filter_readers()
        self._filter_books()

    def _build_form(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        header = ctk.CTkLabel(
            container,
            text="📋 Lập phiếu mượn sách",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        header.pack(anchor="w", pady=(0, 14))

        form_grid = ctk.CTkFrame(container, fg_color="transparent")
        form_grid.pack(fill="both", expand=True)
        form_grid.grid_columnconfigure(1, weight=1)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")


        ctk.CTkLabel(form_grid, text="Tìm độc giả:", font=input_font).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self.reader_search_entry = ctk.CTkEntry(
            form_grid,
            placeholder_text="🔍 Gõ tên hoặc mã thẻ độc giả để lọc...",
            height=32,
            font=input_font,
        )
        self.reader_search_entry.grid(row=0, column=1, sticky="ew", pady=6)
        self.reader_search_entry.bind("<KeyRelease>", lambda _: self._filter_readers())

        ctk.CTkLabel(form_grid, text="Chọn độc giả (*):", font=input_font).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self.reader_cb = ctk.CTkComboBox(form_grid, values=["Không có độc giả hoạt động"], height=34, font=input_font)
        self.reader_cb.grid(row=1, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Tìm sách:", font=input_font).grid(row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        self.book_search_entry = ctk.CTkEntry(
            form_grid,
            placeholder_text="🔍 Gõ tên sách, tác giả hoặc ISBN để lọc...",
            height=32,
            font=input_font,
        )
        self.book_search_entry.grid(row=2, column=1, sticky="ew", pady=6)
        self.book_search_entry.bind("<KeyRelease>", lambda _: self._filter_books())

        ctk.CTkLabel(form_grid, text="Chọn sách (*):", font=input_font).grid(row=3, column=0, sticky="w", pady=6, padx=(0, 12))
        self.book_cb = ctk.CTkComboBox(form_grid, values=["Không có sách sẵn sàng"], height=34, font=input_font)
        self.book_cb.grid(row=3, column=1, sticky="ew", pady=6)

        default_due = (date.today() + timedelta(days=30)).strftime("%d-%m-%Y")
        ctk.CTkLabel(form_grid, text="Hạn trả (DD-MM-YYYY):", font=input_font).grid(row=4, column=0, sticky="w", pady=6, padx=(0, 12))
        self.due_entry = ctk.CTkEntry(form_grid, height=34, font=input_font)
        self.due_entry.insert(0, default_due)
        self.due_entry.grid(row=4, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(form_grid, text="Ghi chú:", font=input_font).grid(row=5, column=0, sticky="w", pady=6, padx=(0, 12))
        self.note_entry = ctk.CTkEntry(
            form_grid,
            placeholder_text="Nhập ghi chú tình trạng sách (không bắt buộc)...",
            height=34,
            font=input_font,
        )
        self.note_entry.grid(row=5, column=1, sticky="ew", pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(14, 0))

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
            text="Tạo phiếu mượn",
            width=150,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._handle_create,
        ).pack(side="right")

    def _filter_readers(self):
        kw = self.reader_search_entry.get().strip()
        active_readers = ReaderService.get_all_readers(keyword=kw, status_filter="Hoạt động")
        self.readers_map.clear()
        reader_options = []
        for r in active_readers:
            label = f"{r.card_number} - {r.full_name}"
            reader_options.append(label)
            self.readers_map[label] = r.reader_id
        if reader_options:
            self.reader_cb.configure(values=reader_options)
            self.reader_cb.set(reader_options[0])
        else:
            self.reader_cb.configure(values=["Không tìm thấy độc giả phù hợp"])
            self.reader_cb.set("Không tìm thấy độc giả phù hợp")

    def _filter_books(self):
        kw = self.book_search_entry.get().strip()
        matched_books = BookService.get_all_books(keyword=kw)
        self.books_map.clear()
        book_options = []
        for b in matched_books:
            if b.available_quantity > 0:
                label = f"[ID:{b.book_id}] {b.title} (Còn: {b.available_quantity})"
                book_options.append(label)
                self.books_map[label] = b.book_id
        if book_options:
            self.book_cb.configure(values=book_options)
            self.book_cb.set(book_options[0])
        else:
            self.book_cb.configure(values=["Không tìm thấy sách sẵn sàng"])
            self.book_cb.set("Không tìm thấy sách sẵn sàng")

    def _handle_create(self):
        r_label = self.reader_cb.get()
        b_label = self.book_cb.get()
        due_str = self.due_entry.get().strip()
        note = self.note_entry.get().strip()

        reader_id = self.readers_map.get(r_label)
        book_id = self.books_map.get(b_label)

        if not reader_id or not book_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn độc giả và sách hợp lệ!", parent=self)
            return

        try:
            due_date = datetime.strptime(due_str, "%d-%m-%Y").date()
            if due_date < date.today():
                messagebox.showwarning("Ngày không hợp lệ", "Hạn trả không được nhỏ hơn ngày hôm nay!", parent=self)
                return
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Hạn trả phải theo định dạng DD-MM-YYYY (VD: 25-10-2026)!", parent=self)
            return

        try:
            BorrowService.create_borrow(
                reader_id=reader_id,
                book_id=book_id,
                user_id=self.current_user.user_id,
                due_date=due_date.strftime("%Y-%m-%d"),
                note=note,
            )
            messagebox.showinfo("Thành công", "Đã tạo phiếu mượn sách thành công!", parent=self)
            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi lập phiếu", str(e), parent=self)


class ReturnBookDialog(ctk.CTkToplevel):
    """Hộp thoại Xử lý Trả sách / Phạt quá hạn / Báo mất sách"""

    def __init__(self, master, borrow: Borrow, on_save_callback):
        super().__init__(master)
        self.borrow = borrow
        self.on_save_callback = on_save_callback

        self.title(f"Xử lý phiếu mượn #{borrow.borrow_id}")
        center_window(self, 480, 410)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._build_form()

    def _build_form(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        header = ctk.CTkLabel(
            container,
            text=f"✓ Xử lý trả sách (Mã phiếu #{self.borrow.borrow_id})",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
        )
        header.pack(anchor="w", pady=(0, 12))

        info_text = (
            f"Độc giả: {self.borrow.reader_name} ({self.borrow.card_number})\n"
            f"Sách: {self.borrow.book_title}\n"
            f"Ngày mượn: {format_date(self.borrow.borrow_date)}   |   Hạn trả: {format_date(self.borrow.due_date)}"
        )
        info_box = ctk.CTkLabel(
            container,
            text=info_text,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
        )
        info_box.pack(fill="x", pady=(0, 14))

        form_grid = ctk.CTkFrame(container, fg_color="transparent")
        form_grid.pack(fill="both", expand=True)
        form_grid.grid_columnconfigure(1, weight=1)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

       
        ctk.CTkLabel(form_grid, text="Trạng thái xử lý:", font=input_font).grid(row=0, column=0, sticky="w", pady=8, padx=(0, 12))
        self.status_cb = ctk.CTkComboBox(
            form_grid,
            values=["Đã trả", "Quá hạn", "Mất sách"],
            height=34,
            font=input_font,
        )
        self.status_cb.set("Đã trả")
        self.status_cb.grid(row=0, column=1, sticky="ew", pady=8)


        suggested_fine = float(self.borrow.fine_amount or 0)
        if suggested_fine == 0 and self.borrow.due_date and date.today() > self.borrow.due_date:
            overdue_days = (date.today() - self.borrow.due_date).days
            suggested_fine = overdue_days * 5000

        ctk.CTkLabel(form_grid, text="Tiền phạt (VNĐ):", font=input_font).grid(row=1, column=0, sticky="w", pady=8, padx=(0, 12))
        self.fine_entry = ctk.CTkEntry(form_grid, height=34, font=input_font)
        self.fine_entry.insert(0, f"{int(suggested_fine)}")
        self.fine_entry.grid(row=1, column=1, sticky="ew", pady=8)

        ctk.CTkLabel(form_grid, text="Ghi chú khi trả:", font=input_font).grid(row=2, column=0, sticky="w", pady=8, padx=(0, 12))
        self.note_entry = ctk.CTkEntry(form_grid, placeholder_text="Nhập ghi chú khi trả...", height=34, font=input_font)
        if self.borrow.note:
            self.note_entry.insert(0, self.borrow.note)
        self.note_entry.grid(row=2, column=1, sticky="ew", pady=8)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(14, 0))

        ctk.CTkButton(
            btn_frame,
            text="Đóng",
            fg_color="gray50",
            hover_color="gray40",
            width=100,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="Xác nhận cập nhật",
            fg_color="#28a745",
            hover_color="#1e7e34",
            width=155,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._handle_return,
        ).pack(side="right")

    def _handle_return(self):
        new_status = self.status_cb.get()
        fine_str = self.fine_entry.get().strip()
        note = self.note_entry.get().strip()

        try:
            fine_amount = float(fine_str or 0)
            if fine_amount < 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Lỗi định dạng", "Tiền phạt phải là số >= 0!", parent=self)
            return

        try:
            BorrowService.return_book(
                borrow_id=self.borrow.borrow_id,
                new_status=new_status,
                fine_amount=fine_amount,
                note=note,
            )
            messagebox.showinfo("Thành công", "Đã cập nhật trạng thái phiếu mượn!", parent=self)
            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi xử lý", str(e), parent=self)


class BorrowView(ctk.CTkFrame):
    """Màn hình Quản lý Mượn - Trả sách"""

    def __init__(self, master, current_user: User):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.borrows_cache = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 12))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="📋 Quản lý mượn - trả sách",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        title_lbl.pack(side="left")

        return_btn = ctk.CTkButton(
            top_bar,
            text="✓ Trả sách / Xử lý phiếu",
            fg_color="#17a2b8",
            hover_color="#117a8b",
            width=165,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_return_dialog,
        )
        return_btn.pack(side="right", padx=(8, 0))

        create_btn = ctk.CTkButton(
            top_bar,
            text="➕ Lập phiếu mượn",
            fg_color="#28a745",
            hover_color="#1e7e34",
            width=145,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_create_dialog,
        )
        create_btn.pack(side="right")

      
        filter_bar = ctk.CTkFrame(self, corner_radius=10)
        filter_bar.pack(fill="x", pady=(0, 12), ipady=6)

        input_font = ctk.CTkFont(family="Segoe UI", size=13, weight="normal")

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Tìm theo tên độc giả, mã thẻ hoặc tên sách...",
            width=340,
            height=34,
            font=input_font,
        )
        self.search_entry.pack(side="left", padx=(14, 10), pady=6)
        self.search_entry.bind("<Return>", lambda _: self.load_data())

        ctk.CTkLabel(filter_bar, text="Trạng thái:", font=input_font).pack(side="left", padx=(6, 6))

        self.status_cb = ctk.CTkComboBox(
            filter_bar,
            values=["Tất cả", "Đang mượn", "Đã trả", "Quá hạn", "Mất sách"],
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

        columns = (
            "borrow_id",
            "card_number",
            "reader_name",
            "book_title",
            "borrow_date",
            "due_date",
            "return_date",
            "status",
            "fine_amount",
            "staff_name",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "borrow_id": ("Mã phiếu", 70, "center"),
            "card_number": ("Mã thẻ", 95, "center"),
            "reader_name": ("Độc giả", 150, "w"),
            "book_title": ("Tên sách", 200, "w"),
            "borrow_date": ("Ngày mượn", 95, "center"),
            "due_date": ("Hạn trả", 95, "center"),
            "return_date": ("Ngày trả", 95, "center"),
            "status": ("Trạng thái", 95, "center"),
            "fine_amount": ("Tiền phạt", 95, "e"),
            "staff_name": ("Người lập", 130, "w"),
        }
        for col, (text, width, anchor) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("alt", background=row_alt)
        self.tree.bind("<Double-1>", lambda _: self._open_return_dialog())

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
            borrows = BorrowService.get_all_borrows(keyword=keyword, status_filter=status_filter)

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.borrows_cache.clear()
            for idx, br in enumerate(borrows):
                self.borrows_cache[br.borrow_id] = br
                tag = ("alt",) if idx % 2 == 1 else ()
                self.tree.insert(
                    "",
                    "end",
                    iid=str(br.borrow_id),
                    values=(
                        br.borrow_id,
                        br.card_number,
                        br.reader_name,
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
            messagebox.showerror("Lỗi tải lịch sử mượn trả", str(e))

    def _open_create_dialog(self):
        CreateBorrowDialog(self, current_user=self.current_user, on_save_callback=self.load_data)

    def _open_return_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn phiếu", "Vui lòng chọn một phiếu mượn trong bảng để xử lý trả sách!")
            return
        borrow_id = int(selected[0])
        borrow = self.borrows_cache.get(borrow_id)
        if borrow:
            if borrow.status == "Đã trả":
                messagebox.showinfo("Thông báo", "Phiếu mượn này đã hoàn tất trả sách!")
                return
            ReturnBookDialog(self, borrow=borrow, on_save_callback=self.load_data)
