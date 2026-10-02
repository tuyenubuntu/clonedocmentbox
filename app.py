import sys
import os
import re
import time
import base64
import urllib.parse
import ctypes

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver

# Định danh App ID riêng để Windows không gộp icon vào Python trên Taskbar
try:
    myappid = "scribddownloader.desktop.app.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


def resource_path(relative_path):
    """Lấy đường dẫn tài nguyên tuyệt đối, tương thích khi chạy code và khi đã đóng gói thành file .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def parse_scribd_url(url):
    match = re.search(r'https://www\.scribd\.com/document/(\d+)(?:/([^?#]+))?', url)
    if not match:
        return None, None, ""

    doc_id = match.group(1)
    embed_url = f'https://www.scribd.com/embeds/{doc_id}/content'
    
    raw_slug = match.group(2)
    suggested_name = ""
    if raw_slug:
        decoded = urllib.parse.unquote(raw_slug)
        suggested_name = decoded.replace("-", " ").strip()

    return doc_id, embed_url, suggested_name


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()


class ScribdWorker(QThread):
    progress_changed = Signal(int)
    log_message = Signal(str)
    finished = Signal()

    def __init__(self, link, browser_choice, save_filepath):
        super().__init__()
        self.link = link
        self.browser_choice = browser_choice
        self.save_filepath = save_filepath

    def run(self):
        driver = None
        try:
            self.log_message.emit("Đang khởi tạo trình duyệt...")
            self.progress_changed.emit(5)

            if self.browser_choice == "Google Chrome":
                options = ChromeOptions()
                options.add_experimental_option("detach", True)
                options.add_argument("--kiosk-printing")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(options=options)
            else:
                options = FirefoxOptions()
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Firefox(options=options)

            self.log_message.emit(f"Đang mở liên kết: {self.link}")
            driver.get(self.link)
            time.sleep(3)

            self.log_message.emit("Đang quét và đồng bộ các trang tài liệu...")
            self.progress_changed.emit(15)

            # Lấy danh sách các trang
            page_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='page']")
            total_pages = len(page_elements)

            if total_pages > 0:
                self.log_message.emit(f"Tìm thấy {total_pages} trang. Bắt đầu xử lý chống trang trắng...")

                # LƯỢT 1: Cuộn từng trang và chờ trang tải xong ảnh/canvas
                for idx, page in enumerate(page_elements):
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page)
                    
                    # Kiểm tra xem ảnh trong trang đã load xong chưa (tránh trắng trang)
                    driver.execute_script("""
                        var elem = arguments[0];
                        var imgs = elem.querySelectorAll('img');
                        imgs.forEach(function(img) {
                            if (!img.complete) {
                                img.loading = 'eager';
                            }
                        });
                    """, page)

                    time.sleep(0.6 if self.browser_choice == "Google Chrome" else 1.0)
                    pct = int(15 + ((idx + 1) / total_pages) * 55)
                    self.progress_changed.emit(pct)

                self.log_message.emit("Đang kiểm tra và kích hoạt lại các trang bị lazy-load...")
                time.sleep(1.5)

                # LƯỢT 2: Cuộn ngược lại để bù các trang bị Scribd tự động gỡ bỏ khỏi DOM
                for idx in reversed(range(total_pages)):
                    driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", page_elements[idx])
                    time.sleep(0.2)

                # Đưa màn hình về đầu trang
                driver.execute_script("window.scrollTo(0, 0);")
                self.progress_changed.emit(75)
                self.log_message.emit("Tất cả dữ liệu hình ảnh và văn bản đã được tải xong.")
            else:
                self.log_message.emit("Không tìm thấy cấu trúc trang tiêu chuẩn, chuẩn bị xuất...")
                self.progress_changed.emit(75)

            time.sleep(1.5)

            # Xóa các toolbar và thanh cuộn cản trở view in
            self.log_message.emit("Đang dọn dẹp các thanh công cụ...")
            driver.execute_script("""
                var toolbarTop = document.querySelector('.toolbar_top');
                if (toolbarTop) { toolbarTop.parentNode.removeChild(toolbarTop); }
                var toolbarBottom = document.querySelector('.toolbar_bottom');
                if (toolbarBottom) { toolbarBottom.parentNode.removeChild(toolbarBottom); }
            """)

            elements = driver.find_elements(By.CLASS_NAME, "document_scroller")
            for el in elements:
                driver.execute_script("arguments[0].setAttribute('class', '');", el)

            self.progress_changed.emit(85)
            time.sleep(1)

            # =========================================================================
            # BƯỚC KHẮC PHỤC: Tiêm CSS ép buộc ngắt trang chính xác cho từng trang tài liệu
            # =========================================================================
            self.log_message.emit("Đang tối ưu kích thước trang chống cắt đuôi...")

            css_page_fix = """
                var style = document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = `
                    @media print {
                        @page {
                            size: A4 portrait;
                            margin: 0 !important;
                        }
                        html, body {
                            margin: 0 !important;
                            padding: 0 !important;
                            background: white !important;
                            -webkit-print-color-adjust: exact !important;
                            print-color-adjust: exact !important;
                        }
                        /* Xóa bỏ khoảng cách, viền và bóng đổ làm dài trang */
                        .document_scroller, .document_column, .between_page_portal_root {
                            margin: 0 !important;
                            padding: 0 !important;
                        }
                        /* Khóa từng trang vừa khít 100% chiều cao trang A4 */
                        [class*='page'], .outer_page {
                            page-break-before: always !important;
                            break-before: page !important;
                            page-break-after: avoid !important;
                            break-after: avoid !important;
                            page-break-inside: avoid !important;
                            break-inside: avoid !important;
                            
                            margin: 0 auto !important;
                            box-shadow: none !important;
                            border: none !important;
                            
                            /* Đảm bảo trang vừa vặn chiều cao in A4 */
                            max-height: 100vh !important;
                            box-sizing: border-box !important;
                            display: block !important;
                            position: relative !important;
                        }
                        /* Trang đầu tiên không cần ngắt trước */
                        [class*='page']:first-of-type, .outer_page:first-of-type {
                            page-break-before: auto !important;
                            break-before: auto !important;
                        }
                    }
                `;
                document.head.appendChild(style);
            """
            driver.execute_script(css_page_fix)
            time.sleep(1)

            # Lưu file PDF
            if self.browser_choice == "Google Chrome":
                self.log_message.emit("Đang xuất file PDF qua Chrome DevTools...")
                print_params = {
                    'landscape': False,
                    'displayHeaderFooter': False,
                    'printBackground': True,
                    'preferCSSPageSize': False,     # Tắt prefer CSS để ép chặt khổ giấy A4
                    'paperWidth': 8.27,             # Khổ rộng A4 (inch)
                    'paperHeight': 11.50,           # Chiều cao A4 (inch)
                    'marginTop': 0,
                    'marginBottom': 0,
                    'marginLeft': 0,
                    'marginRight': 0,
                    'scale': 0.98                   # Co nhẹ 2% để phần chân trang nằm trọn vẹn trong 1 trang giấy
                }
                pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_params)

                with open(self.save_filepath, "wb") as f:
                    f.write(base64.b64decode(pdf_data['data']))

                self.progress_changed.emit(100)
                self.log_message.emit(f"Thành công! Đã lưu tại:\n{self.save_filepath}")
            else:
                self.log_message.emit("Đang mở hộp thoại in (Firefox)...")
                driver.execute_script("window.print();")
                self.progress_changed.emit(100)
                self.log_message.emit(f"Vui lòng lưu file với tên: {os.path.basename(self.save_filepath)}")

        except Exception as e:
            self.log_message.emit(f"Lỗi: {str(e)}")
        finally:
            self.finished.emit()


class ScribdApp:
    def __init__(self):
        loader = QUiLoader()
        # Nạp giao diện qua resource_path để an toàn khi đóng gói .exe
        ui_file_path = resource_path("UI/GUI.ui")
        self.window = loader.load(ui_file_path)

        # Cài đặt icon cho cửa sổ
        self.set_icon()

        # Cấu hình giá trị ban đầu
        self.window.progressBar.setValue(0)
        self.window.groupBox.setTitle("Trạng thái")

        default_dir = os.path.abspath("./Downloads")
        os.makedirs(default_dir, exist_ok=True)
        self.window.folderpathEdit.setText(default_dir)

        # Trích xuất tên tự động khi dán liên kết
        self.window.linkEdit.textChanged.connect(self.on_link_changed)

        # Gán sự kiện click cho các nút
        self.window.clear_btn.clicked.connect(self.clear_link)
        if hasattr(self.window, "clear_btn_2"):
            self.window.clear_btn_2.clicked.connect(self.clear_name)

        self.window.find_btn.clicked.connect(self.choose_folder)
        self.window.execute_btn.clicked.connect(self.start_process)

        self.worker = None

    def set_icon(self):
        icon_candidates = ["ico.ico", "ico.png", "UI/ico_1.ico", "UI/icon.png", "UI/ico.ico"]
        for path in icon_candidates:
            abs_path = resource_path(path)
            if os.path.exists(abs_path):
                icon = QIcon(abs_path)
                self.window.setWindowIcon(icon)
                break

    def on_link_changed(self, text):
        raw_url = text.strip()
        _, _, suggested_name = parse_scribd_url(raw_url)
        if suggested_name and hasattr(self.window, "nameEdit"):
            self.window.nameEdit.setText(suggested_name)

    def clear_link(self):
        self.window.linkEdit.clear()

    def clear_name(self):
        if hasattr(self.window, "nameEdit"):
            self.window.nameEdit.clear()

    def choose_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.window, "Chọn thư mục lưu file PDF")
        if folder:
            self.window.folderpathEdit.setText(folder)

    def append_log(self, text):
        self.window.infoText.appendPlainText(text)

    def start_process(self):
        raw_url = self.window.linkEdit.text().strip()
        if not raw_url:
            self.append_log("Vui lòng nhập link Scribd!")
            return

        doc_id, embed_url, _ = parse_scribd_url(raw_url)
        if not embed_url:
            self.append_log("Đường dẫn Scribd không hợp lệ!")
            return

        save_folder = self.window.folderpathEdit.text().strip()
        if not save_folder or not os.path.exists(save_folder):
            self.append_log("Thư mục lưu trữ không tồn tại. Vui lòng chọn lại thư mục!")
            return

        custom_name = ""
        if hasattr(self.window, "nameEdit"):
            custom_name = self.window.nameEdit.text().strip()

        clean_name = sanitize_filename(custom_name)
        file_name = f"{clean_name}.pdf" if clean_name else f"Scribd_{doc_id}.pdf"
        save_filepath = os.path.join(save_folder, file_name)
        browser = self.window.browerBox.currentText()

        self.window.execute_btn.setEnabled(False)
        self.window.progressBar.setValue(0)
        self.window.infoText.clear()

        self.worker = ScribdWorker(
            link=embed_url, 
            browser_choice=browser, 
            save_filepath=save_filepath
        )
        self.worker.progress_changed.connect(self.window.progressBar.setValue)
        self.worker.log_message.connect(self.append_log)
        self.worker.finished.connect(lambda: self.window.execute_btn.setEnabled(True))
        self.worker.start()

    def show(self):
        self.window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Thiết lập icon cấp Application qua resource_path
    for path in ["ico.ico", "ico.png", "UI/ico_1.ico", "UI/icon.png", "UI/ico.ico"]:
        abs_path = resource_path(path)
        if os.path.exists(abs_path):
            app.setWindowIcon(QIcon(abs_path))
            break

    main_app = ScribdApp()
    main_app.show()
    sys.exit(app.exec())