Dưới đây là nội dung mẫu hoàn chỉnh cho file `README.md` của dự án:

```markdown
# Scribd Document Downloader

Ứng dụng hỗ trợ trích xuất và tải tài liệu Scribd về máy tính dưới định dạng PDF với giao diện đồ họa (GUI) trực quan, tự động dọn dẹp các thanh công cụ, cuộn trang chống mất nội dung và lưu file trực tiếp.

---

## 🌟 Tính năng nổi bật

- **Tự động nhận diện tài liệu**: Tự bóc tách Document ID và tạo tên file gợi ý từ đường dẫn (URL) Scribd[cite: 7].
- **Hỗ trợ đa trình duyệt**: Tùy chọn linh hoạt giữa Google Chrome và Mozilla Firefox[cite: 3].
- **Chống trắng/mất trang**: Cơ chế cuộn hai chiều kết hợp đồng bộ hóa tài nguyên hình ảnh/canvas giúp khắc phục hiện tượng lazy-load của Scribd.
- **Tự động lưu PDF hoàn toàn**: Sử dụng giao thức CDP (Chrome DevTools Protocol) để xuất tệp PDF trực tiếp vào thư mục chỉ định mà không cần xác nhận hộp thoại in thủ công.
- **Tùy biến tên và đường dẫn lưu trữ**: Dễ dàng đổi tên file xuất ra và chọn thư mục lưu mong muốn[cite: 6].

---

## 📁 Cấu trúc thư mục

```text
ScribdDownload/
│
├── UI/
│   ├── GUI.ui             # File thiết kế giao diện Qt Designer
│   └── ico_1.ico          # File icon ứng dụng
│
├── app.py                 # Mã nguồn chính của chương trình
├── requirements.txt       # Danh sách thư viện phụ thuộc
├── install.bat            # Script tự động tạo môi trường và cài đặt (Conda)
├── run.bat                # Script khởi chạy nhanh ứng dụng
└── README.md              # Tài liệu hướng dẫn sử dụng

```

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### Cách 1: Sử dụng qua Conda (Khuyên dùng khi phát triển)

1. **Cài đặt môi trường:**
* Nhấp đúp vào file `install.bat` để script tự động tạo môi trường Conda `QT_env` (Python 3.11) và cài đặt các thư viện cần thiết.


2. **Khởi chạy ứng dụng:**
* Nhấp đúp vào file `run.bat` (hoặc chạy lệnh sau trong terminal):
```bash
conda activate QT_env
python app.py

```





### Cách 2: Cài đặt thủ công bằng `pip`

```bash
pip install -r requirements.txt
python app.py

```

---

## 📦 Hướng dẫn đóng gói thành file `.exe` duy nhất

Để chia sẻ chương trình sang các máy tính khác chạy trực tiếp mà không cần cài đặt Python hay Conda:

1. Kích hoạt môi trường và cài đặt `pyinstaller`:
```bash
pip install pyinstaller

```


2. Chạy lệnh đóng gói:
```bash
pyinstaller --noconsole --onefile --collect-all selenium --icon="UI/ico_1.ico" --add-data "UI;UI" app.py

```


3. File thực thi độc lập sẽ xuất hiện tại thư mục `dist/app.exe`.

---

## 🛠️ Yêu cầu hệ thống

* Hệ điều hành: Windows 10 / 11
* Trình duyệt: Google Chrome (khuyên dùng để xuất PDF tự động ngầm) hoặc Mozilla Firefox.

---

## 📄 Bản quyền & Ghi nhận

* Ý tưởng & Logic bóc tách gốc: [tuyenubuntu (GitHub)](https://github.com/tuyenubuntu)

* Phát triển giao diện & Tối ưu hóa: Truong Thanh Tuyen

```

```