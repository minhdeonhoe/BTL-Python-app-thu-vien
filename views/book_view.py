from datetime import datetime
from tkinter import ttk, messagebox
from typing import Optional
import customtkinter as ctk
from models.book import Book
from services.book_service import BookService
from utils.helpers import apply_treeview_style, center_window


class BookFormDialog(ctk.CTkToplevel):
    """Hộp thoại Thêm mới / Cập nhật thông tin sách"""

    def __init__(self, master, on_save_callback, book: Optional[Book] = None):
        super().__init__(master)
        self.on_save_callback = on_save_callback
        self.book = book
        self.is_edit = book is not None

        self.title("Cập nhật sách" if self.is_edit else "Thêm sách mới")
        center_window(self, 520, 560)
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
            text="✏️ Cập nhật sách" if self.is_edit else "➕ Thêm sách mới",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        header.pack(anchor="w", pady=(0, 15))

        form_grid = ctk.CTkFrame(container, fg_color="transparent")
        form_grid.pack(fill="both", expand=True)
        form_grid.grid_columnconfigure(1, weight=1)

        fields = [
            ("Mã ISBN:", "isbn_entry", "VD: 978-604-1-12345"),
            ("Tên sách (*):", "title_entry", "Nhập tên sách"),
            ("Tác giả (*):", "author_entry", "Nhập tên tác giả"),
            ("Thể loại (*):", "category_entry", "VD: Công nghệ thông tin"),
            ("Nhà xuất bản:", "publisher_entry", "VD: NXB Giáo Dục"),
            ("Năm xuất bản:", "year_entry", f"1901 - {datetime.now().year}"),
            ("Tổng số lượng (*):", "total_qty_entry", "Nhập số nguyên >= 0"),
            ("Số lượng sẵn có (*):", "avail_qty_entry", "Nhập số nguyên <= Tổng SL"),
        ]

        self.entries = {}
        for idx, (label_text, attr_name, placeholder) in enumerate(fields):
            lbl = ctk.CTkLabel(
                form_grid,
                text=label_text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
                anchor="w",
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=6, padx=(0, 12))

            entry = ctk.CTkEntry(
                form_grid,
                placeholder_text=placeholder,
                height=34,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            )
            entry.grid(row=idx, column=1, sticky="ew", pady=6)
            self.entries[attr_name] = entry

        # Vị trí kệ: chỉ cho chọn trong 6 kệ mặc định
        shelf_row = len(fields)
        ctk.CTkLabel(
            form_grid,
            text="Vị trí kệ (*):",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            anchor="w",
        ).grid(row=shelf_row, column=0, sticky="w", pady=6, padx=(0, 12))

        self.location_cb = ctk.CTkComboBox(
            form_grid,
            values=BookService.SHELF_LOCATIONS,
            state="readonly",
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
        )
        self.location_cb.set(BookService.SHELF_LOCATIONS[0])
        self.location_cb.grid(row=shelf_row, column=1, sticky="ew", pady=6)

        # Nút bấm
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Hủy",
            fg_color="gray50",
            hover_color="gray40",
            width=110,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Lưu thông tin",
            width=140,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._handle_save,
        )
        save_btn.pack(side="right")

    def _populate_data(self):
        b = self.book
        self.entries["isbn_entry"].insert(0, b.isbn or "")
        self.entries["title_entry"].insert(0, b.title or "")
        self.entries["author_entry"].insert(0, b.author or "")
        self.entries["category_entry"].insert(0, b.category or "")
        self.entries["publisher_entry"].insert(0, b.publisher or "")
        if b.publish_year:
            self.entries["year_entry"].insert(0, str(b.publish_year))
        self.entries["total_qty_entry"].insert(0, str(b.total_quantity))
        self.entries["avail_qty_entry"].insert(0, str(b.available_quantity))
        location = BookService.normalize_location(b.location)
        if location in BookService.SHELF_LOCATIONS:
            self.location_cb.set(location)

    def _handle_save(self):
        isbn = self.entries["isbn_entry"].get().strip()
        title = self.entries["title_entry"].get().strip()
        author = self.entries["author_entry"].get().strip()
        category = self.entries["category_entry"].get().strip()
        publisher = self.entries["publisher_entry"].get().strip()
        year_str = self.entries["year_entry"].get().strip()
        total_str = self.entries["total_qty_entry"].get().strip()
        avail_str = self.entries["avail_qty_entry"].get().strip()
        location = self.location_cb.get().strip()

        if not title or not author or not category:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ Tên sách, Tác giả và Thể loại!", parent=self)
            return

        publish_year = None
        if year_str:
            try:
                publish_year = int(year_str)
                current_year = datetime.now().year
                if publish_year <= 1900 or publish_year > current_year:
                    messagebox.showwarning(
                        "Năm không hợp lệ",
                        f"Năm xuất bản phải nằm trong khoảng 1901 đến {current_year}!",
                        parent=self,
                    )
                    return
            except ValueError:
                messagebox.showwarning("Lỗi định dạng", "Năm xuất bản phải là số nguyên!", parent=self)
                return

        try:
            total_qty = int(total_str)
            avail_qty = int(avail_str)
            if total_qty < 0 or avail_qty < 0:
                raise ValueError()
            if avail_qty > total_qty:
                messagebox.showwarning(
                    "Ràng buộc số lượng",
                    "Số lượng sẵn có không được lớn hơn Tổng số lượng!",
                    parent=self,
                )
                return
        except ValueError:
            messagebox.showwarning("Lỗi định dạng", "Số lượng phải là số nguyên không âm!", parent=self)
            return

        book_obj = Book(
            book_id=self.book.book_id if self.is_edit else None,
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            publisher=publisher,
            publish_year=publish_year,
            total_quantity=total_qty,
            available_quantity=avail_qty,
            location=location,
        )

        try:
            if self.is_edit:
                BookService.update_book(book_obj)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin sách!", parent=self)
            else:
                BookService.add_book(book_obj)
                messagebox.showinfo("Thành công", "Đã thêm sách mới vào thư viện!", parent=self)

            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu thông tin sách:\n{e}", parent=self)


class BookView(ctk.CTkFrame):
    """Màn hình Quản lý Sách"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.books_cache = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # Thanh tiêu đề & nút chức năng
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 12))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="📘 Quản lý kho sách",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        title_lbl.pack(side="left")

        del_btn = ctk.CTkButton(
            top_bar,
            text="🗑️ Xóa sách",
            fg_color="#d9534f",
            hover_color="#b52b27",
            width=110,
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
            text="➕ Thêm sách mới",
            fg_color="#28a745",
            hover_color="#1e7e34",
            width=135,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_add_dialog,
        )
        add_btn.pack(side="right")

        filter_bar = ctk.CTkFrame(self, corner_radius=10)
        filter_bar.pack(fill="x", pady=(0, 12), ipady=6)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Tìm theo tên sách, tác giả hoặc mã ISBN...",
            width=340,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
        )
        self.search_entry.pack(side="left", padx=(14, 10), pady=6)
        self.search_entry.bind("<Return>", lambda _: self.load_data())

        cat_lbl = ctk.CTkLabel(filter_bar, text="Thể loại:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"))
        cat_lbl.pack(side="left", padx=(6, 6))

        self.category_cb = ctk.CTkComboBox(
            filter_bar,
            values=["Tất cả"],
            width=190,
            height=34,
            command=lambda _: self.load_data(),
        )
        self.category_cb.set("Tất cả")
        self.category_cb.pack(side="left", padx=(0, 10))

        search_btn = ctk.CTkButton(
            filter_bar,
            text="Tìm kiếm",
            width=95,
            height=34,
            command=self.load_data,
        )
        search_btn.pack(side="left", padx=(0, 8))

        reset_btn = ctk.CTkButton(
            filter_bar,
            text="Làm mới",
            width=90,
            height=34,
            fg_color="gray50",
            hover_color="gray40",
            command=self._reset_filters,
        )
        reset_btn.pack(side="left")
        
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        row_alt = apply_treeview_style()

        columns = (
            "book_id",
            "isbn",
            "title",
            "author",
            "category",
            "publisher",
            "publish_year",
            "available",
            "total",
            "location",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        headers = {
            "book_id": ("ID", 50, "center"),
            "isbn": ("Mã ISBN", 125, "w"),
            "title": ("Tên sách", 230, "w"),
            "author": ("Tác giả", 150, "w"),
            "category": ("Thể loại", 140, "w"),
            "publisher": ("Nhà xuất bản", 120, "w"),
            "publish_year": ("Năm XB", 75, "center"),
            "available": ("Còn lại", 70, "center"),
            "total": ("Tổng SL", 70, "center"),
            "location": ("Vị trí", 85, "center"),
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
        self.category_cb.set("Tất cả")
        self.load_data()

    def load_data(self):
        try:
            categories = ["Tất cả"] + BookService.get_categories()
            current_cat = self.category_cb.get()
            self.category_cb.configure(values=categories)
            if current_cat not in categories:
                self.category_cb.set("Tất cả")

            keyword = self.search_entry.get().strip()
            selected_cat = self.category_cb.get()
            books = BookService.get_all_books(keyword=keyword, category=selected_cat)

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.books_cache.clear()
            for idx, b in enumerate(books):
                self.books_cache[b.book_id] = b
                tag = ("alt",) if idx % 2 == 1 else ()
                self.tree.insert(
                    "",
                    "end",
                    iid=str(b.book_id),
                    values=(
                        b.book_id,
                        b.isbn,
                        b.title,
                        b.author,
                        b.category,
                        b.publisher,
                        b.publish_year or "",
                        b.available_quantity,
                        b.total_quantity,
                        b.location,
                    ),
                    tags=tag,
                )
        except Exception as e:
            messagebox.showerror("Lỗi tải dữ liệu sách", str(e))

    def _open_add_dialog(self):
        BookFormDialog(self, on_save_callback=self.load_data)

    def _edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn sách", "Vui lòng chọn một cuốn sách trong bảng để sửa!")
            return
        book_id = int(selected[0])
        book = self.books_cache.get(book_id)
        if book:
            BookFormDialog(self, on_save_callback=self.load_data, book=book)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn sách", "Vui lòng chọn một cuốn sách cần xóa!")
            return
        book_id = int(selected[0])
        book = self.books_cache.get(book_id)
        if not book:
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa mềm",
            f"Bạn có chắc chắn muốn ẩn/xóa cuốn sách:\n'{book.title}' (ID: {book.book_id}) không?",
        )
        if confirm:
            try:
                BookService.delete_book(book_id)
                self.load_data()
                messagebox.showinfo("Thành công", "Đã xóa mềm sách khỏi danh sách hiển thị.")
            except Exception as e:
                messagebox.showerror("Lỗi khi xóa", str(e))
