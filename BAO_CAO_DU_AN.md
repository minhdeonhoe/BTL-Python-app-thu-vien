# BÁO CÁO BÀI TẬP LỚN
## ĐỀ TÀI: HỆ THỐNG QUẢN LÝ THƯ VIỆN (LIBRARY MANAGEMENT SYSTEM)

---

## 1. MÔ TẢ BÀI TOÁN, MỤC TIÊU VÀ CÁC CHỨC NĂNG CHÍNH

### 1.1. Mô tả bài toán
Trong công tác vận hành thư viện trường học, việc quản lý đầu sách, thẻ bạn đọc và theo dõi phiếu mượn – trả nếu thực hiện thủ công hoặc qua các bảng tính rời rạc thường dẫn đến nhiều bất cập:
- Khó kiểm soát số lượng sách thực tế đang còn sẵn trên kệ so với tổng số sách của thư viện.
- Dễ xảy ra sai sót khi lập phiếu mượn (cho mượn sách đã hết kho, cho độc giả đang bị khóa thẻ mượn sách) hoặc tính nhầm tiền phạt quá hạn.
- Khi xóa nhầm sách hoặc độc giả sẽ làm mất toàn bộ lịch sử mượn trả trước đó.
- Thiếu cơ chế phân quyền rõ ràng giữa Quản trị viên (Admin) và Thủ thư (Librarian).

### 1.2. Mục tiêu của sản phẩm
Xây dựng phần mềm Desktop **Hệ thống Quản lý Thư viện** có giao diện trực quan, tốc độ phản hồi nhanh, tự động hóa hoàn toàn quy trình kiểm tra điều kiện mượn – trả, tự động đồng bộ tồn kho sách và đảm bảo tính toàn vẹn dữ liệu trên hệ quản trị cơ sở dữ liệu quan hệ.

### 1.3. Các chức năng chính của sản phẩm
1. **Xác thực và Phân quyền người dùng:**
   - Đăng nhập bảo mật theo vai trò (`Admin` và `Librarian`): Thủ thư (`Librarian`) có đầy đủ quyền quản lý Sách, quản lý Độc giả và quản lý Mượn – Trả sách; Quản trị viên (`Admin`) có thêm quyền quản lý Tài khoản nhân sự.
   - Cơ chế bảo vệ **1 Admin duy nhất**: Tài khoản Admin không thể tự hạ quyền hoặc tự khóa tài khoản của chính mình; chỉ Admin mới được phép quản lý danh sách Thủ thư.
2. **Bảng điều khiển Tổng quan (Dashboard):**
   - Thống kê trực quan theo thời gian thực 5 chỉ số: Tổng đầu sách, Sách sẵn có trên kệ, Độc giả đang hoạt động, Phiếu đang mượn và Phiếu quá hạn.
3. **Quản lý Kho sách:**
   - Thêm, sửa, xóa mềm (`Soft Delete`) và tra cứu đa tiêu chí (`LIKE`) theo tên sách, tác giả, mã ISBN, nhà xuất bản, lọc theo thể loại.
   - Quản lý tách biệt **Tổng số lượng (`total_quantity`)** và **Số lượng sẵn có (`available_quantity`)** tại 6 vị trí kệ cố định (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`).
4. **Quản lý Độc giả:**
   - Quản lý hồ sơ bạn đọc (Mã thẻ, Họ tên, Giới tính, Ngày sinh chuẩn `DD-MM-YYYY`, Số điện thoại 10 chữ số, Email chuẩn `@gmail.com`, Trạng thái thẻ `Hoạt động` / `Khóa thẻ`).
   - Xem lịch sử mượn – trả và thống kê tiền phạt riêng của từng độc giả.
5. **Quản lý Mượn – Trả sách & Tính phạt tự động:**
   - Lập phiếu mượn: Tự động kiểm tra trạng thái thẻ bạn đọc, kiểm tra tồn kho và tự động trừ số lượng sách sẵn có (`-1`).
   - Xử lý trả sách / quá hạn / mất sách: Tự động gợi ý tiền phạt quá hạn (`5.000 VNĐ/ngày trễ`), tự động hoàn lại kho (`+1`) khi trả sách hoặc giữ nguyên kho nếu báo mất sách.

---

## 2. PHÂN TÍCH VÀ LỰA CHỌN GIẢI PHÁP

### 2.1. Lựa chọn kiến trúc phần mềm: Kiến trúc 3 tầng (3-Layer Architecture) kết hợp DAO
Thay vì viết toàn bộ giao diện và truy vấn SQL chung trong một tệp mã nguồn, nhóm lựa chọn tách biệt hệ thống thành các tầng độc lập:
- **Presentation Layer (`views/`):** Chỉ đảm nhận hiển thị giao diện và nhận thao tác từ người dùng.
- **Business Logic Layer (`services/`):** Kiểm tra toàn bộ quy tắc nghiệp vụ (định dạng dữ liệu, điều kiện mượn trả, phân quyền).
- **Data Access Layer (`dao/` & `config/`):** Chứa các câu lệnh SQL giao tiếp với CSDL thông qua đối tượng thực thể (`models/`).

**Lý do lựa chọn:** Giúp mã nguồn rõ ràng, dễ kiểm thử, dễ bảo trì và dễ dàng phân chia công việc cho các thành viên trong nhóm mà không bị xung đột mã nguồn.

### 2.2. Giải pháp đảm bảo toàn vẹn dữ liệu
- **Sử dụng Transaction khi Mượn – Trả:** Đảm bảo thao tác tạo/cập nhật phiếu mượn và thao tác trừ/cộng số lượng sách trong kho luôn thành công cùng nhau hoặc cùng `rollback` nếu có lỗi.
- **Sử dụng kỹ thuật Xóa mềm (Soft Delete):** Dùng cờ `is_active = 0` khi xóa Sách hoặc Độc giả thay vì lệnh `DELETE` vật lý, giúp giữ nguyên lịch sử các phiếu mượn cũ để phục vụ tra cứu và đối soát.

---

## 3. THIẾT KẾ CHƯƠNG TRÌNH / HỆ THỐNG

### 3.1. Cấu trúc phân tầng của hệ thống
- **`main.py`**: Điểm khởi chạy chương trình, khởi tạo cửa sổ gốc và điều phối chuyển màn hình Đăng nhập <-> Màn hình chính.
- **`config/database.py`**: Quản lý chuỗi kết nối SQL Server và Context Manager `get_db_cursor`.
- **`models/`**: Định nghĩa 4 lớp thực thể dữ liệu: `User`, `Book`, `Reader`, `Borrow`.
- **`dao/`**: Thực thi các truy vấn SQL tham số hóa (`user_dao.py`, `book_dao.py`, `reader_dao.py`, `borrow_dao.py`).
- **`services/`**: Xử lý kiểm tra nghiệp vụ (`auth_service.py`, `book_service.py`, `reader_service.py`, `borrow_service.py`).
- **`views/`**: Xây dựng giao diện người dùng (`login_view.py`, `main_view.py`, `book_view.py`, `reader_view.py`, `borrow_view.py`, `user_view.py`).
- **`utils/helpers.py`**: Cung cấp hàm định dạng ngày `DD-MM-YYYY`, tiền tệ `VNĐ`, cấu hình bảng `Treeview` và vá lỗi font bộ gõ tiếng Việt.

### 3.2. Thiết kế Cơ sở dữ liệu (`LibraryManagementDB`)
Hệ cơ sở dữ liệu (`database/library.sql`) gồm 4 bảng chính:
1. **Bảng `Users` (Nhân sự):** `user_id` (PK), `username` (UNIQUE), `password_hash`, `full_name`, `email`, `role` (`Admin` | `Librarian`), `is_active`, `created_at`.
2. **Bảng `Books` (Kho sách):** `book_id` (PK), `isbn` (UNIQUE), `title`, `author`, `category`, `publisher`, `publish_year`, `total_quantity`, `available_quantity`, `location`, `is_active`, `created_at` (Ràng buộc: `available_quantity <= total_quantity`).
3. **Bảng `Readers` (Độc giả):** `reader_id` (PK), `card_number` (UNIQUE), `full_name`, `gender`, `dob`, `phone`, `email`, `address`, `status` (`Hoạt động` | `Khóa thẻ`), `is_active`, `created_at`.
4. **Bảng `Borrows` (Phiếu mượn - trả):** `borrow_id` (PK), `reader_id` (FK), `book_id` (FK), `user_id` (FK), `borrow_date`, `due_date`, `return_date`, `status` (`Đang mượn` | `Đã trả` | `Quá hạn` | `Mất sách`), `fine_amount`, `note`.

---

## 4. CÁC THƯ VIỆN, FRAMEWORK VÀ CÔNG NGHỆ SỬ DỤNG

| Nhóm công nghệ | Tên công nghệ / Thư viện | Mục đích sử dụng trong dự án |
| :--- | :--- | :--- |
| **Ngôn ngữ lập trình** | **Python 3.x** | Ngôn ngữ chính xây dựng toàn bộ ứng dụng (`dataclasses`, `typing`, `datetime`, `decimal`, `contextlib`). |
| **Giao diện (GUI)** | **CustomTkinter** & **tkinter.ttk** | Xây dựng giao diện Desktop hiện đại, kết hợp `ttk.Treeview` hiển thị bảng dữ liệu lớn. |
| **Hệ quản trị CSDL** | **Microsoft SQL Server** | Lưu trữ dữ liệu tập trung, đảm bảo ràng buộc toàn vẹn (`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK`). |
| **Thư viện kết nối CSDL** | **pyodbc** | Kết nối Python với SQL Server qua ODBC Driver, hỗ trợ Parameterized Query chống SQL Injection. |
| **Thư viện hệ thống** | **ctypes (Win32 IMM32 API)** | Can thiệp tầng Windows API để đồng bộ font chữ khi gõ tiếng Việt có dấu (UniKey/EVKey) trên ô nhập liệu. |

---

## 5. KẾT QUẢ THỰC HIỆN VÀ MINH HỌA KỸ THUẬT TRỌNG TÂM

### 5.1. Quản lý kết nối và Transaction tự động với Context Manager (`config/database.py`)
```python
@contextmanager
def get_db_cursor(commit: bool = False):
    conn = None
    cursor = None
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

### 5.2. Đồng bộ tồn kho tự động trong 1 Transaction khi Mượn – Trả sách (`dao/borrow_dao.py`)
```python
@staticmethod
def insert_borrow_and_decrease_stock(
    reader_id: int, book_id: int, user_id: int, due_date: str, note: Optional[str] = None
) -> None:
    insert_sql = """
        INSERT INTO Borrows (reader_id, book_id, user_id, borrow_date, due_date, status, fine_amount, note)
        VALUES (?, ?, ?, CAST(GETDATE() AS DATE), ?, N'Đang mượn', 0, ?)
    """
    update_book_sql = """
        UPDATE Books
        SET available_quantity = available_quantity - 1
        WHERE book_id = ?
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (reader_id, book_id, user_id, due_date, note))
        cursor.execute(update_book_sql, (book_id,))
```

### 5.3. Kiểm tra ràng buộc dữ liệu đầu vào (`services/reader_service.py`)
```python
if not reader.phone.isdigit() or len(reader.phone) != 10:
    raise ValueError("Số điện thoại không hợp lệ! Số điện thoại phải gồm đúng 10 chữ số.")

if (
    not reader.email
    or not reader.email.lower().endswith("@gmail.com")
    or reader.email.count("@") != 1
    or reader.email.startswith("@")
    or " " in reader.email
):
    raise ValueError("Email không hợp lệ! Email bắt buộc phải có đuôi @gmail.com.")
```

---

## 6. KẾT LUẬN

### 6.1. Kết quả đạt được
- Xây dựng hoàn chỉnh ứng dụng Quản lý Thư viện đáp ứng đầy đủ các yêu cầu nghiệp vụ thực tế.
- Áp dụng thành công kiến trúc 3 tầng (`Views` – `Services` – `DAO`) kết hợp CSDL SQL Server có tính toàn vẹn cao.
- Giao diện thân thiện, đồng nhất định dạng ngày tháng `DD-MM-YYYY`, tiền tệ `VNĐ` và khắc phục triệt để lỗi hiển thị font khi gõ tiếng Việt trên Windows.

### 6.2. Hạn chế và Hướng phát triển
- **Hạn chế:** Mỗi phiếu mượn hiện tại thiết kế cho 1 đầu sách để đơn giản hóa việc theo dõi hạn trả và tiền phạt trên từng cuốn; chưa tích hợp xuất báo cáo ra tệp Excel/PDF.
- **Hướng phát triển:** Bổ sung tính năng xuất phiếu mượn ra file PDF/Excel, tích hợp quét mã vạch (Barcode/QR Code) và gửi email nhắc hạn trả sách tự động.

---

## 7. PHÂN CÔNG CÔNG VIỆC CỤ THỂ CHO TỪNG THÀNH VIÊN

| STT | Họ và tên thành viên | MSSV | Công việc được phân công | Mức độ hoàn thành |
| :-: | :--- | :---: | :--- | :---: |
| 1 | **[Điền Họ tên TV 1 - Nhóm trưởng]** | `[MSSV 1]` | - Thiết kế CSDL SQL Server (`database/library.sql`) và cấu hình kết nối (`config/database.py`).<br>- Xây dựng phân hệ **Mượn – Trả sách** (`borrow_dao.py`, `borrow_service.py`, `borrow_view.py`) và màn hình **Tổng quan (Dashboard)**.<br>- Tích hợp hệ thống và kiểm thử chung. | 100% |
| 2 | **[Điền Họ tên TV 2]** | `[MSSV 2]` | - Xây dựng phân hệ **Quản lý Kho sách** (`book.py`, `book_dao.py`, `book_service.py`, `book_view.py`).<br>- Xây dựng bộ công cụ tiện ích định dạng ngày tháng, tiền tệ, giao diện bảng (`utils/helpers.py`). | 100% |
| 3 | **[Điền Họ tên TV 3]** | `[MSSV 3]` | - Xây dựng phân hệ **Quản lý Độc giả** & **Tra cứu lịch sử mượn cá nhân** (`reader.py`, `reader_dao.py`, `reader_service.py`, `reader_view.py`).<br>- Xây dựng phân hệ **Đăng nhập & Quản lý Nhân sự** (`user.py`, `user_dao.py`, `auth_service.py`, `login_view.py`, `user_view.py`).<br>- Tổng hợp báo cáo và chuẩn bị slide thuyết trình. | 100% |

---

## 8. KHAI BÁO VIỆC SỬ DỤNG CÁC CÔNG CỤ AI

| Công cụ AI đã sử dụng | Mục đích và phạm vi sử dụng | Kiểm soát của nhóm |
| :--- | :--- | :--- |
| **Google Antigravity / Trợ lý lập trình AI (LLM)** | 1. **Tư vấn kiến trúc:** Gợi ý cách tổ chức thư mục chuẩn theo mô hình 3 tầng (`views`, `services`, `dao`, `models`) và cách sử dụng `@contextmanager` cho kết nối `pyodbc`.<br>2. **Hỗ trợ gỡ lỗi (Debug) giao diện:** Tìm giải pháp sử dụng thư viện `ctypes` (Win32 IMM32 API) để khắc phục lỗi nhảy font chữ in đậm của CustomTkinter khi gõ tiếng Việt bằng bộ gõ UniKey/EVKey.<br>3. **Rà soát ràng buộc nghiệp vụ:** Hỗ trợ kiểm tra các trường hợp biên như ràng buộc 1 Admin duy nhất, định dạng ngày `DD-MM-YYYY`, kiểm tra email `@gmail.com`, số điện thoại 10 chữ số.<br>4. **Hỗ trợ trình bày tài liệu:** Gợi ý bố cục trình bày báo cáo và vẽ sơ đồ Mermaid (ERD, Sequence Diagram). | Toàn bộ mã nguồn, câu lệnh truy vấn SQL và luồng nghiệp vụ đều được các thành viên trong nhóm trực tiếp đọc hiểu, kiểm thử thực tế trên SQL Server, chỉnh sửa và chịu trách nhiệm hoàn toàn về tính chính xác của sản phẩm. |
