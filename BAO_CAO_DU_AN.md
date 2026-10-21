# 📚 BÁO CÁO BÀI TẬP LỚN & KỊCH BẢN THUYẾT TRÌNH
## Đề tài: Hệ Thống Quản Lý Thư Viện (Library Management System)

---

## PHẦN 1: TỔNG QUAN DỰ ÁN (INTRODUCTION)

### 1.1. Lý do chọn đề tài & Bài toán thực tế
Trong công tác quản lý thư viện truyền thống (bằng sổ sách hoặc file bảng tính rời rạc), thủ thư thường gặp phải các vấn đề:
- **Khó tra cứu tồn kho tức thời:** Không biết chính xác một đầu sách còn bao nhiêu cuốn sẵn sàng trên kệ hay đang được ai mượn.
- **Sai sót khi mượn – trả:** Dễ cho mượn nhầm sách đã hết trong kho, quên thu tiền phạt quá hạn, hoặc cho thẻ độc giả đang bị khóa mượn sách.
- **Mất mát lịch sử dữ liệu:** Khi xóa nhầm một cuốn sách hoặc một độc giả, toàn bộ lịch sử phiếu mượn liên quan bị mất hoặc lỗi khóa ngoại.
- **Thiếu phân quyền bảo mật:** Không tách biệt được quyền của **Quản trị viên (Admin)** và **Thủ thư (Librarian)**.

### 1.2. Mục tiêu của hệ thống
Xây dựng phần mềm Desktop **Quản Lý Thư Viện** hiện đại, trực quan, giải quyết triệt để các vấn đề trên với:
1. **Kiến trúc phân tầng rõ ràng (3-Layer Architecture + DAO + Models)** giúp code sạch, dễ bảo trì và mở rộng.
2. **Giao diện người dùng hiện đại (CustomTkinter)** hỗ trợ tiếng Việt mượt mà, bố cục trực quan theo từng phân hệ.
3. **Cơ sở dữ liệu quan hệ chặt chẽ (Microsoft SQL Server)** đảm bảo toàn vẹn dữ liệu, giao dịch (Transaction) và cơ chế **Xóa mềm (Soft Delete)**.

### 1.3. Công nghệ sử dụng (Tech Stack)
| Thành phần | Công nghệ / Thư viện | Vai trò trong dự án |
| :--- | :--- | :--- |
| **Ngôn ngữ lập trình** | Python 3.x | Ngôn ngữ chính xử lý toàn bộ logic và giao diện |
| **Giao diện (GUI)** | `CustomTkinter` & `tkinter.ttk` | Thiết kế giao diện phẳng hiện đại, bảng dữ liệu `Treeview` |
| **Hệ quản trị CSDL** | Microsoft SQL Server | Lưu trữ dữ liệu tập trung, kiểm soát ràng buộc (`CHECK`, `FK`, `UNIQUE`) |
| **Kết nối CSDL** | `pyodbc` + Context Manager | Giao tiếp SQL Server an toàn, tự động `commit`/`rollback` và đóng kết nối |
| **Xử lý hệ thống** | `ctypes` (Win32 IMM32 API) | Đồng bộ font bộ gõ tiếng Việt (UniKey/EVKey) không bị nhảy chữ in đậm |

---

## PHẦN 2: KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Dự án tuân thủ nghiêm ngặt mô hình **Kiến trúc 3 tầng (3-Layer Architecture)** kết hợp mẫu thiết kế **DAO (Data Access Object)**:

- **Tầng 1 - Presentation Layer (`views/`):**
  - `login_view.py`: Giao diện đăng nhập.
  - `main_view.py`: Khung điều hướng Sidebar & Màn hình Tổng quan (Dashboard).
  - `book_view.py`: Giao diện Quản lý Sách.
  - `reader_view.py`: Giao diện Quản lý Độc giả & Lịch sử mượn cá nhân.
  - `borrow_view.py`: Giao diện Quản lý Mượn - Trả sách & Tính tiền phạt.
  - `user_view.py`: Giao diện Quản lý Nhân sự (dành riêng cho Admin).
- **Tầng 2 - Business Logic Layer (`services/`):**
  - `auth_service.py`: Xác thực đăng nhập, kiểm soát phân quyền và bảo vệ tài khoản Admin duy nhất.
  - `book_service.py`: Kiểm tra dữ liệu sách, năm xuất bản, tồn kho và chuẩn hóa 6 kệ sách (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`).
  - `reader_service.py`: Kiểm tra dữ liệu thẻ độc giả.
  - `borrow_service.py`: Kiểm tra điều kiện mượn/trả sách và điều phối tăng/giảm tồn kho.
- **Tầng 3 - Data Access Layer (`dao/` & `config/`):**
  - `config/database.py`: Cung cấp `DatabaseConnection` và Context Manager `get_db_cursor()`.
  - `user_dao.py`, `book_dao.py`, `reader_dao.py`, `borrow_dao.py`: Thực thi câu lệnh SQL tham số hóa (`?`).
- **Models & Utils (`models/`, `utils/`):**
  - `models/`: Định nghĩa các thực thể `User`, `Book`, `Reader`, `Borrow`.
  - `utils/helpers.py`: Định dạng ngày `dd-mm-yyyy`, tiền tệ VNĐ, style bảng Treeview và sửa lỗi font IME tiếng Việt.

---

## PHẦN 3: THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN)

Hệ cơ sở dữ liệu `LibraryManagementDB` (`database/library.sql`) gồm **4 bảng chính**:

1. **Bảng `Users` (Nhân sự hệ thống):**
   - `user_id` (PK), `username` (UNIQUE), `password_hash`, `full_name`, `email`, `role` (`Admin` | `Librarian`), `is_active`, `created_at`.
2. **Bảng `Books` (Kho sách):**
   - `book_id` (PK), `isbn` (UNIQUE), `title`, `author`, `category`, `publisher`, `publish_year`, `total_quantity`, `available_quantity`, `location` (`A1`..`C2`), `is_active`, `created_at`.
   - Ràng buộc: `CHK_Book_Quantity CHECK (available_quantity <= total_quantity)`.
3. **Bảng `Readers` (Độc giả):**
   - `reader_id` (PK), `card_number` (UNIQUE), `full_name`, `gender`, `dob`, `phone`, `email`, `address`, `status` (`Hoạt động` | `Khóa thẻ`), `is_active`, `created_at`.
4. **Bảng `Borrows` (Phiếu mượn - trả):**
   - `borrow_id` (PK), `reader_id` (FK), `book_id` (FK), `user_id` (FK), `borrow_date`, `due_date`, `return_date`, `status` (`Đang mượn` | `Đã trả` | `Quá hạn` | `Mất sách`), `fine_amount`, `note`.

---

## PHẦN 4: KỊCH BẢN THUYẾT TRÌNH (5 - 7 PHÚT)

### Bước 1: Mở đầu (30 giây)
- Giới thiệu tên đề tài: **Hệ thống Quản lý Thư viện (Library Management System)** bằng **Python CustomTkinter** và **SQL Server**.
- Nêu mục tiêu: Tự động hóa quản lý đầu sách, độc giả, phân quyền nhân sự và đồng bộ tồn kho tự động khi mượn – trả.

### Bước 2: Trình bày Kiến trúc & CSDL (1.5 phút)
- Trình bày mô hình 3 tầng (`Views` -> `Services` -> `DAO` -> `Database`).
- Giải thích 2 điểm nhấn CSDL:
  1. Tách biệt **Tổng số lượng (`total_quantity`)** và **Số lượng sẵn có (`available_quantity`)**.
  2. Sử dụng **Xóa mềm (`is_active = 0`)** để bảo toàn lịch sử mượn trả.

### Bước 3: Demo trực tiếp phần mềm (3 - 4 phút)
1. **Đăng nhập & Dashboard:** Đăng nhập tài khoản `admin` / `123456`, giới thiệu 5 chỉ số thống kê thời gian thực.
2. **Quản lý Sách:** Tìm kiếm theo `LIKE`, thêm/sửa sách, chọn kệ cố định (`A1` -> `C2`).
3. **Quản lý Độc giả:** Thêm/sửa độc giả (ngày sinh `dd-mm-yyyy`), mở hộp thoại **Lịch sử mượn** của độc giả.
4. **Quản lý Mượn – Trả:**
   - Lập phiếu mượn mới -> Kiểm tra số lượng sẵn có tự động trừ 1.
   - Xử lý trả sách -> Hệ thống tự gợi ý tiền phạt nếu quá hạn (`5.000đ/ngày`) -> Khi chọn "Đã trả", số lượng sẵn có tự động cộng 1.
5. **Quản lý Nhân sự:** Demo cơ chế bảo vệ tài khoản Admin duy nhất (không cho tự hạ quyền hoặc tự khóa).

### Bước 4: Kết luận & Hỏi đáp (Q&A)
- Tổng kết các kết quả đạt được và lắng nghe câu hỏi từ giảng viên.

