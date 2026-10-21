
USE master;
GO
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'LibraryManagementDB')
BEGIN
    ALTER DATABASE LibraryManagementDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE LibraryManagementDB;
END
GO


CREATE DATABASE LibraryManagementDB;
GO

USE LibraryManagementDB;
GO

CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name NVARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'Librarian' CHECK (role IN ('Admin', 'Librarian')),
    is_active BIT NOT NULL DEFAULT 1, 
    created_at DATETIME DEFAULT GETDATE()
);
GO


CREATE TABLE Books (
    book_id INT IDENTITY(1,1) PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title NVARCHAR(200) NOT NULL,
    author NVARCHAR(100) NOT NULL,
    category NVARCHAR(100) NOT NULL,
    publisher NVARCHAR(100),
    publish_year INT CHECK (publish_year > 1900 AND publish_year <= YEAR(GETDATE())),
    total_quantity INT NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
    available_quantity INT NOT NULL DEFAULT 0 CHECK (available_quantity >= 0),
    location NVARCHAR(50), 
    is_active BIT NOT NULL DEFAULT 1, 
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT CHK_Book_Quantity CHECK (available_quantity <= total_quantity)
);
GO


CREATE TABLE Readers (
    reader_id INT IDENTITY(1,1) PRIMARY KEY,
    card_number VARCHAR(20) NOT NULL UNIQUE, 
    full_name NVARCHAR(100) NOT NULL,
    gender NVARCHAR(10) CHECK (gender IN (N'Nam', N'Nữ', N'Khác')),
    dob DATE,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address NVARCHAR(255),
    status NVARCHAR(20) NOT NULL DEFAULT N'Hoạt động' CHECK (status IN (N'Hoạt động', N'Khóa thẻ')),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE Borrows (
    borrow_id INT IDENTITY(1,1) PRIMARY KEY,
    reader_id INT NOT NULL,
    book_id INT NOT NULL,
    user_id INT NOT NULL, 
    borrow_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    due_date DATE NOT NULL, 
    return_date DATE NULL,  
    status NVARCHAR(20) NOT NULL DEFAULT N'Đang mượn' 
        CHECK (status IN (N'Đang mượn', N'Đã trả', N'Quá hạn', N'Mất sách')),
    fine_amount DECIMAL(10, 2) DEFAULT 0 CHECK (fine_amount >= 0), 
    note NVARCHAR(255),

    CONSTRAINT FK_Borrows_Readers FOREIGN KEY (reader_id) REFERENCES Readers(reader_id),
    CONSTRAINT FK_Borrows_Books FOREIGN KEY (book_id) REFERENCES Books(book_id),
    CONSTRAINT FK_Borrows_Users FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
GO


INSERT INTO Users (username, password_hash, full_name, email, role) VALUES
('admin', '123456', N'Nguyễn Quản Trị', 'admin@gmail.com', 'Admin'),
('thuthu1', '123456', N'Trần Thị Thu Thủy', 'thuytt@gmail.com', 'Librarian'),
('thuthu2', '123456', N'Lê Văn Nam', 'namlv@gmail.com', 'Librarian');

INSERT INTO Books (isbn, title, author, category, publisher, publish_year, total_quantity, available_quantity, location) VALUES
('978-604-1-12345', N'Lập trình Python cơ bản', N'Nguyễn Văn A', N'Công nghệ thông tin', N'NXB Giáo Dục', 2023, 15, 14, N'A1'),
('978-604-2-54321', N'Cấu trúc dữ liệu', N'Lê Minh Hoàng', N'Công nghệ thông tin', N'NXB ĐHQG', 2022, 10, 9, N'A1'),
('978-604-3-67890', N'Cơ sở dữ liệu SQL', N'Trần Trọng B', N'Công nghệ thông tin', N'NXB KHKT', 2021, 12, 12, N'A2'),
('978-604-4-11223', N'Đắc Nhân Tâm', N'Dale Carnegie', N'Kỹ năng sống', N'NXB Tổng Hợp', 2020, 20, 20, N'B1'),
('978-604-5-99887', N'Nhà Giả Kim', N'Paulo Coelho', N'Văn học', N'NXB Hội Nhà Văn', 2021, 8, 7, N'C1');

INSERT INTO Readers (card_number, full_name, gender, dob, phone, email, address, status) VALUES
('SV2024001', N'Phạm Minh Tuấn', N'Nam', '15-07-2006', '0901234567', 'tuanpm@gmail.com', N'Cầu Giấy, Hà Nội', N'Hoạt động'),
('SV2024002', N'Hoàng Thu Trang', N'Nữ', '20-08-2005', '0912345678', 'tranght@gmail.com', N'Đống Đa, Hà Nội', N'Hoạt động'),
('SV2024003', N'Ngô Kiến Huy', N'Nam', '10-11-2003', '0987654321', 'huynk@gmail.com', N'Thanh Xuân, Hà Nội', N'Khóa thẻ');

INSERT INTO Borrows (reader_id, book_id, user_id, borrow_date, due_date, return_date, status, fine_amount, note) VALUES
(1, 1, 2, '2025-02-01', '2025-02-15', NULL, N'Đang mượn', 0, N'Sách mới nguyên vẹn'),
(2, 2, 2, '2025-01-10', '2025-01-24', NULL, N'Quá hạn', 15000, N'Chưa mang trả'),
(1, 5, 3, '2025-01-05', '2025-01-19', '2025-01-18', N'Đã trả', 0, N'Trả đúng hạn');
GO