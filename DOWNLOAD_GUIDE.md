# 🖼️ Pancake Bot - Google Drive Download Guide

## 🚨 Vấn đề hiện tại

Bot không thể download ảnh từ Google Drive vì **thiếu quyền truy cập công khai**.

**Lỗi:** `Cannot retrieve the public link of the file. You may need to change the permission to 'Anyone with the link'`

## 🛠️ Giải pháp

### Phương án 1: Fix Google Drive Permissions (Khuyên dùng)

1. **Mở Google Drive folder:**
   ```
   https://drive.google.com/drive/u/0/folders/1I3RvB7t6rAktkhTVw8oKsKORJuKkoUr0
   ```

2. **Chọn tất cả ảnh** (3 files JPG)

3. **Click "Share"** (chia sẻ)

4. **Thay đổi permissions:**
   - Click "Restricted" → "Anyone with the link"
   - ✅ Chọn "Viewer" permission
   - Click "Copy link" và lưu lại

5. **Chờ 5-10 phút** để permissions cập nhật

6. **Chạy lại bot:**
   ```bash
   python main_workflow.py
   ```

### Phương án 2: Download Manual và Upload

1. **Download manual từng file:**
   - Mở từng file trong Google Drive
   - Click "Download" để tải về local

2. **Đặt files vào folder `DDownloads/`**

3. **Chạy script manual upload:**
   ```bash
   python manual_upload.py  # (cần tạo script này)
   ```

### Phương án 3: Sử dụng Direct URLs

Nếu bạn có direct share URLs, update code:

```python
# Trong main_workflow.py, thay đổi step download:

# Thay vì dùng file IDs, dùng direct URLs:
direct_urls = [
    "https://drive.google.com/file/d/FILE_ID_1/view?usp=sharing",
    "https://drive.google.com/file/d/FILE_ID_2/view?usp=sharing",
    "https://drive.google.com/file/d/FILE_ID_3/view?usp=sharing"
]

for url in direct_urls:
    result = downloader.download_from_direct_url(url)
    if result:
        # Process uploaded image
        pass
```

## 📁 Files cần xử lý

Từ Google Sheets data, bot tìm thấy **3 image IDs:**

1. `z7397359279360_bdb8ca99f53e7707d5b5fd086f9a24f1.jpg`
2. `z7397359835229_42ec8892f74c232d254e6850a3f9bffc.jpg`
3. `z7397360974735_fe73f954867b7f95fca687f3c0129c2c.jpg`

## 🧪 Test Download

Chạy script test download:

```bash
python download_images_manual.py
```

## 📊 Workflow Status

```
Products loaded: 1 ✅
Images downloaded: 0 ❌ (do permissions)
Images uploaded: 0 ❌
Settings updated: No ❌
```

**Next:** Fix permissions → Re-run workflow → Success!

## 🔗 Links hữu ích

- [Google Drive Permission Guide](https://support.google.com/drive/answer/2494822)
- [Gdown FAQ](https://github.com/wkentaro/gdown?tab=readme-ov-file#faq)
- [Pancake API Docs](https://pancake.vn/developers)

---

**💡 Tip:** Phương án 1 (fix permissions) là đơn giản nhất và sẽ làm bot hoạt động tự động hoàn toàn!
