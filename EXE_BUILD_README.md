# Building Standalone EXE

Hướng dẫn đóng gói `cron_job.py` thành file exe chạy độc lập.

## 📋 Yêu cầu

- Python 3.8+
- PyInstaller
- Các dependencies trong `requirements.txt`

## 🚀 Quick Build

```bash
# Cài đặt PyInstaller
pip install pyinstaller

# Cài đặt dependencies
pip install -r requirements.txt

# Build exe
python build_exe.py
```

## 📂 Cấu trúc sau khi build

```
dist/
├── cron_job.exe          # File exe chính
├── product_state.json    # File state (tự động tạo)
├── quick_replies.json    # File settings (tự động tạo)
└── images/               # Thư mục chứa ảnh download
```

## 🎯 Cách sử dụng exe

1. **Copy toàn bộ thư mục `dist`** đến máy đích
2. **Chạy exe:**
   ```cmd
   # Double-click cron_job.exe
   # hoặc
   cron_job.exe
   ```

3. **Exe sẽ:**
   - Chạy liên tục mỗi 30 giây
   - Tự động reset và xử lý tất cả products
   - Lưu file JSON trong cùng thư mục
   - Download ảnh vào thư mục `images/`

## 🔧 Tùy chỉnh Build

### Thay đổi icon (optional)

```python
# Trong build_exe.py, thêm icon parameter:
exe = EXE(
    # ...
    icon='icon.ico',  # Thêm file icon
)
```

### Build one-file exe

```python
# Trong build_exe.py, sửa thành:
exe = EXE(
    pyz,
    a.scripts,
    [],  # Remove a.binaries, a.zipfiles, a.datas
    name='cron_job',
    debug=False,
    # ...
    console=True,
    onefile=True,  # Tạo 1 file exe duy nhất
)
```

### Build cho Linux/Mac

```bash
# Trên Linux/Mac:
pyinstaller --onefile cron_job.py

# Copy các file JSON cần thiết
cp product_state.json dist/
cp quick_replies.json dist/
```

## 🐛 Troubleshooting

### Exe không chạy

1. **Check Python version:** PyInstaller yêu cầu Python tương thích
2. **Missing dependencies:** Đảm bảo cài đủ packages trong requirements.txt
3. **Antivirus blocking:** Một số antivirus chặn exe từ PyInstaller

### File JSON không được tạo

- Exe sẽ tự động tạo file JSON nếu chưa có
- Đảm bảo thư mục `dist` có quyền write

### Ảnh không download được

- Check kết nối internet
- Verify Google Drive links
- Check thư mục `images/` có quyền write

## 📊 Kích thước exe

- **Typical size:** 50-100MB (tùy dependencies)
- **One-file exe:** ~70MB
- **Folder exe:** ~60MB + dependencies

## 🔄 Update exe

1. Build exe mới từ source code
2. Copy file exe và các file JSON từ exe cũ
3. Thay thế exe cũ

## 📝 Notes

- **Đường dẫn:** Exe tự động detect thư mục chứa nó để lưu file
- **Dependencies:** Tất cả dependencies được đóng gói
- **Compatibility:** Exe chạy trên Windows 7+ (32/64-bit)
- **Performance:** Exe có performance tương đương script Python


