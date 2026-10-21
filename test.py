from config.database import get_db_cursor

def run_all_tests():
    print("[*] Đang kiểm tra toàn diện cơ sở dữ liệu LibraryManagementDB...")
    try:
        with get_db_cursor() as cursor:
            # 1. Kiểm tra tài khoản Users
            cursor.execute("SELECT user_id, username, full_name, role FROM Users")
            users = cursor.fetchall()
            print(f"\n1. Danh sách Users ({len(users)} người dùng):")
            for u in users:
                print(f"   - [ID: {u[0]}] {u[1]} ({u[2]}) - Quyền: {u[3]}")

            # 2. Kiểm tra sách Books
            cursor.execute("SELECT book_id, title, author, category, available_quantity, total_quantity FROM Books")
            books = cursor.fetchall()
            print(f"\n2. Danh sách Sách ({len(books)} cuốn):")
            for b in books:
                print(f"   - [ID: {b[0]}] {b[1]} | TG: {b[2]} | Thể loại: {b[3]} | Còn: {b[4]}/{b[5]}")

            # 3. Kiểm tra độc giả Readers
            cursor.execute("SELECT reader_id, card_number, full_name, phone, status FROM Readers")
            readers = cursor.fetchall()
            print(f"\n3. Danh sách Độc giả ({len(readers)} người):")
            for r in readers:
                print(f"   - [ID: {r[0]}] {r[1]} - {r[2]} ({r[3]}) - Trạng thái: {r[4]}")

            # 4. Kiểm tra phiếu mượn Borrows
            query_borrows = """
                SELECT b.borrow_id, r.full_name, bk.title, b.borrow_date, b.due_date, b.status
                FROM Borrows b
                JOIN Readers r ON b.reader_id = r.reader_id
                JOIN Books bk ON b.book_id = bk.book_id
            """
            cursor.execute(query_borrows)
            borrows = cursor.fetchall()
            print(f"\n4. Lịch sử Mượn/Trả ({len(borrows)} phiếu):")
            for br in borrows:
                print(f"   - [Mã phiếu: {br[0]}] {br[1]} mượn '{br[2]}' | Hạn: {br[4]} | Trạng thái: {br[5]}")

            print("\n" + "=" * 50)
            print(">>> TẤT CẢ CÁC BẢNG HOẠT ĐỘNG HOÀN TOÀN BÌNH THƯỜNG! <<<")
            print("=" * 50)

    except Exception as e:
        print(f"\n[X] Lỗi truy vấn cơ sở dữ liệu: {e}")

if __name__ == "__main__":
    run_all_tests()