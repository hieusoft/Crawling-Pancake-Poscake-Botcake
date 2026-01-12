# Product Cron Job - Automated Product Processing

Cron job tự động theo dõi thay đổi sản phẩm và xử lý sản phẩm mới hoặc đã thay đổi.

## Tính năng

- 🔄 **Tự động phát hiện thay đổi**: Theo dõi thay đổi trong Google Sheets
- 🆕 **Xử lý sản phẩm mới**: Tự động xử lý sản phẩm mới được thêm vào
- 🔄 **Xử lý sản phẩm thay đổi**: Phát hiện và xử lý sản phẩm có thay đổi
- ⏰ **Chạy định kỳ**: Cron job chạy mỗi 30 giây (có thể tùy chỉnh)
- 💾 **Lưu trạng thái**: Lưu trạng thái để tránh xử lý trùng lặp
- 📊 **Logging chi tiết**: Ghi log đầy đủ cho việc theo dõi

## Cách sử dụng

### 🚀 **Chạy liên tục (khuyến nghị - auto reset):**

```bash
python cron_job.py
# → Chạy liên tục mỗi 30s, tự động reset và xử lý tất cả products
```

### 📋 **Các tùy chọn:**

```bash
# Chạy 1 lần duy nhất (test)
python cron_job.py --once

# Chạy định kỳ mỗi 30 giây (không auto-reset)
python cron_job.py --interval 30

# Chạy định kỳ mỗi 60 giây
python cron_job.py --interval 60

# Reset và xử lý lại tất cả (1 lần)
python cron_job.py --reset-processed --once

# File state tùy chỉnh
python cron_job.py --state-file my_state.json
```

### 🪟 **Chạy trên Windows:**

```cmd
# Chạy liên tục trong background:
start /B python cron_job.py

# Hoặc dùng batch file:
start_cron.bat
```

### 🔄 **Logic Auto-Reset:**
- **Default mode**: Chạy liên tục + auto reset processed codes mỗi 30s
- **Mỗi cycle**: Reset processed codes → xử lý lại tất cả products
- **Smart detection**: Vẫn phát hiện products mới/thay đổi

### 6. Chạy trên Windows (background)

```cmd
start_cron.bat
```

## Cấu trúc file

```
product_state.json    # File lưu trạng thái (tự động tạo)
cron_job.py          # Script cron job chính
start_cron.bat       # Script chạy trên Windows
```

## Logic hoạt động

1. **Đọc dữ liệu** từ Google Sheets
2. **So sánh hash** của từng sản phẩm với lần chạy trước
3. **Phát hiện thay đổi**:
   - Sản phẩm mới (chưa có trong state)
   - Sản phẩm thay đổi (hash khác)
4. **Xử lý song song** các sản phẩm cần thiết
5. **Lưu trạng thái** để lần sau tham khảo

## Hash calculation

Hash được tính dựa trên các trường chính của sản phẩm:
- code, product_name, product_type
- price, chat_lieu
- image_count, pancake_reply_price

## State file format

```json
{
  "products": {
    "ED56": "-4239829028556129683",
    "PD31": "2629063251477372006"
  },
  "processed_codes": ["ED56", "PD31"],
  "last_updated": 1768129497.358287
}
```

## Troubleshooting

### Sản phẩm không được xử lý

1. Kiểm tra hash có thay đổi không: `python cron_job.py --once`
2. Reset processed codes: `python cron_job.py --reset-processed --once`

### Lỗi kết nối Google Sheets

- Kiểm tra quyền truy cập Google Sheets
- Xác nhận spreadsheet ID đúng

### Lỗi upload ảnh

- Kiểm tra kết nối internet
- Xác nhận Pancake API token hợp lệ

## Cấu hình nâng cao

### Thay đổi interval

```python
cron_job.run_forever(interval_seconds=60)  # 60 giây
```

### Thay đổi hash fields

Sửa method `_get_product_hash()` để include/exclude fields theo nhu cầu.

### Custom logging

Sửa function `log()` để output tới file hoặc external service.
