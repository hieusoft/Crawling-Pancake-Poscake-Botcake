# POS API - Product Management

Class `PosAPI` để quản lý sản phẩm trên POS Pancake.vn

## Cách sử dụng

```python
from Service.PoscakeApi import PosAPI
from Model.Product import Product

# Khởi tạo API
api = PosAPI()

# === TÌM SẢN PHẨM ===
product_info = api.search_product_by_code("ED56")
if product_info:
    print("Found:", product_info.get("name"))
else:
    print("Product not found")

# === TẠO SẢN PHẨM MỚI ===
product = Product(
    id_page=123,
    code="PROD001",
    image=["img1.jpg", "img2.jpg"],
    color=["RED", "BLUE"],
    price=100000,
    product_type="T-Shirt",
    attr_size=["S", "M", "L"],
    # ... other fields
)

# Tạo product data từ Product object
product_data = api.create_product_data(product)

# Gửi lên POS
result = api.send_product(product_data)
print("Status:", result["status_code"])
print("Success:", result["success"])

# === TẠO COMBO PRODUCT ===
combo_data = {
    "name": "Combo Áo Thun + Quần Jean",
    "description": "Combo tiết kiệm với áo thun và quần jean",
    "price": 250000,
    "items": [
        {
            "product_id": "product-id-1",
            "quantity": 1
        },
        {
            "product_id": "product-id-2",
            "quantity": 1
        }
    ]
}

combo_result = api.create_combo_product(combo_data)
print("Combo created:", combo_result.get("success"))
```

## Cấu hình

```python
api = PosAPI(
    access_token="your_token",  # Optional
    shop_id="your_shop_id"      # Optional
)
```

## Methods

### `search_product_by_code(product_code: str)`
Tìm sản phẩm theo code trên POS
- **Parameters:** `product_code` - Mã sản phẩm cần tìm
- **Returns:** Dict chứa full search results
- **API Endpoint:** `GET /api/v1/shops/{shop_id}/products?search={code}`
- **Response Structure:**
  ```python
  {
    "success": bool,
    "total_entries": int,      # Tổng products trong shop
    "products_found": int,    # Số products tìm được với code
    "products": [...],        # Array của tất cả products tìm được
    "first_product": {...},   # Product đầu tiên (nếu có)
    "searched_code": str,     # Code đã search
    "error": str              # Error message (nếu có)
  }
  ```

### `generate_variants(product: Product)`
Tạo các biến thể sản phẩm từ Product object
- Lấy `code` làm base SKU
- Lấy `color` array cho màu sắc
- Lấy `attr_size` array cho kích thước
- Lấy `price` cho giá

### `create_product_data(product: Product, images: Optional[List[str]] = None)`
Tạo payload data cho API request từ Product object
- Lấy thông tin từ Product fields
- **Images:** Sử dụng uploaded_images dict từ Pancake API, extract content_url cho từng image ID
- Tạo attributes từ color và attr_size (tự động chuyển sang không dấu)
- Tạo variations từ generate_variants()
- **SKU generation:** Remove accents và spaces (VD: "áo ed56" → "AOED56-CAMNHAT-S")
- **Base SKU:** Remove accents và spaces từ product code
- **Price conversion:** Tự động convert price sang int trước khi gửi API
- **Color keys:** Sử dụng tên màu thực thay vì generic keys (VD: "HONG" trong SKU thay vì "COLOR1")

### `send_product(product_data: Dict)`
Gửi product lên POS API
- Returns: `{"status_code": int, "success": bool, "response_text": str}`

### `create_combo_product(combo_data: Dict[str, Any])`
Tạo combo product trên POS
- **Parameters:** `combo_data` - Dictionary chứa thông tin combo product
- **Returns:** Dict với kết quả tạo combo
- **API Endpoint:** `POST /api/v1/shops/{shop_id}/combo_products`
- **Response Structure:**
  ```python
  {
    "success": bool,
    "data": {...},           # Combo product data từ API
    "status_code": int,     # HTTP status code
    "error": str            # Error message (nếu có)
  }
  ```
- **Combo Data Structure:**
  ```python
  {
    "name": "Tên combo",
    "description": "Mô tả combo",
    "price": 150000,        # Giá combo (VND)
    "items": [
      {
        "product_id": "product-id-1",
        "quantity": 1
      },
      {
        "product_id": "product-id-2",
        "quantity": 2
      }
    ]
  }
  ```

### `test_create_combo_product()`
Test tạo combo product

### `test_search_product(product_code: str)`
Test tìm sản phẩm theo code

## Cấu trúc Product Data

- **Sync Rules**: Cấu hình đồng bộ
- **Product Info**: Thông tin cơ bản
- **Attributes**: Màu sắc và kích thước
- **Variations**: Các biến thể với SKU, giá, hình ảnh

## Test

```bash
# Test từ PosAPI trực tiếp (chỉ search)
python Service/PoscakeApi.py
```

Output sẽ show kết quả search sản phẩm.
