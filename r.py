import gdown

# ----- CÀI ĐẶT LINK GOOGLE DRIVE -----
# Link chia sẻ (nguồn của bạn):
drive_link = "https://drive.google.com/file/d/1VR558T2QptoXlrsghuIRzNwn3-NRUsnR/view?usp=drive_link"

# Tách file ID từ link
file_id = drive_link.split("/d/")[1].split("/")[0]
# Tạo URL tải trực tiếp
download_url = f"https://drive.google.com/uc?id={file_id}"

# Tên file khi tải về (có thể đổi tên .jpg/.png theo đúng định dạng ảnh)
output = "downloaded_image.jpg"

print("📥 Đang tải ảnh từ Google Drive…")
gdown.download(download_url, output, quiet=False)

print(f"✅ Tải xong! File đã lưu: {output}")
