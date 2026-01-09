class Product:
    def __init__(
        self,
        
        id_page: int,
        code:str,
        image:str,
        color:list[str],
        price:float,
        product_type: str,
        product_name: str,
        chat_lieu: str,
        pancake_reply_price:str,

        message_b1:list[dict["text": str, "images": str]],
        message_b2:list[dict["text": str, "images": str]],
        message_b3:list[dict["text": str, "images": str]],
        message_b4:list[dict["text": str, "images": str]],
        message_cl:list[dict["text": str, "images": str]],
        message_ld:list[dict["text": str, "images": str]],


        pos_product_code: str ,
        pos_product_name: str,
        
        attr_color: list[str],
        attr_size: list[str],
        mau: str ,
       
        ma_anh: str,
        # Giá
        gia_san_pham: float = None,
        sale_price: float = None,
        bao_gia_pancake: float = None,
        botcake_price_instant: float = None,

        # Combo
        combo_name: str = None,

        

        comment_default: str = None,
        comment_with_phone: str = None,
        message_from_comment: str = None,
        message_from_comment_with_phone: str = None,
        send_message_type: str = None
    ):
        self.id_page = id_page
        self.code = code
        self.image = image
        self.color = color
        self.price = price
        self.product_type = product_type
        self.product_name = product_name
        self.chat_lieu = chat_lieu
        self.pancake_reply_price = pancake_reply_price  
        self.message_b1 = message_b1
        self.message_b2 = message_b2
        self.message_b3 = message_b3
        self.message_b4 = message_b4
        self.message_cl = message_cl
        self.message_ld = message_ld
        self.pos_product_code = pos_product_code
        self.pos_product_name = pos_product_name

        self.ma_anh = ma_anh

        self.attr_color = attr_color
        self.attr_size = attr_size
        self.mau = mau
 

        self.gia_san_pham = gia_san_pham
        self.sale_price = sale_price
        self.bao_gia_pancake = bao_gia_pancake
        self.botcake_price_instant = botcake_price_instant

        self.combo_name = combo_name

        
        self.comment_default = comment_default
        self.comment_with_phone = comment_with_phone
        self.message_from_comment = message_from_comment
        self.message_from_comment_with_phone = message_from_comment_with_phone
        self.send_message_type = send_message_type

    def display(self):
        print(f"""
=== PRODUCT ===
Page ID: {self.id_page}
Code: {self.code}
Image: {self.image}
Color: {self.color}
Price: {self.price}
Loại Sản phẩm: {self.product_type}
Chất liệu: {self.chat_lieu}


===Pancake ===

Báo giá pancake: {self.pancake_reply_price}
TIn nhắn:
1b: {(self.message_b1)} | 2b: {self.message_b2} | 3b: {self.message_b3} | 4b: {self.message_b4}
CL: {self.message_cl} | LD: {self.message_ld}
===POS===
pos_product_code: {self.pos_product_code}
pos_product_name: {self.pos_product_name}
Thuộc tính:
- Màu: {self.attr_color}
- Size: {self.attr_size}
- Chất liệu: {self.chat_lieu}

Giá:
- Giá gốc: {self.gia_san_pham}
- Giá bán: {self.sale_price}
- Báo giá Pancake: {self.bao_gia_pancake}
- Báo giá Botcake (ngay): {self.botcake_price_instant}

Combo: {self.combo_name}



Nội dung tương tác:
- Bình luận mặc định: {self.comment_default}
- Bình luận có SĐT: {self.comment_with_phone}
- Tin nhắn từ BL: {self.message_from_comment}
- Tin nhắn BL có SĐT: {self.message_from_comment_with_phone}
- Kiểu gửi tin: {self.send_message_type}
""")
