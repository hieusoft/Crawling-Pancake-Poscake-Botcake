import requests
from io import StringIO
import csv
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.Product import Product


class SheetProcessor:
    EXPECTED_COLS = 29   # row[0] → row[28]

    def __init__(self, spreadsheet_id="1Rway6WCREH6bj7PiEpS-HRuhMRKyYItaWJPzW0JIRmY"):
        self.spreadsheet_id = spreadsheet_id

    # ============================
    # LOAD & CLEAN SHEET
    # ============================
    def get_sheet_data(self, gid="0"):
        """Load CSV, remove 3 header rows, remove empty rows"""
        sheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv&gid={gid}"
        res = requests.get(sheet_url)
        res.raise_for_status()

        f = StringIO(res.content.decode("utf-8", errors="replace"))
        reader = csv.reader(f)
        rows = list(reader)

        # Remove first 3 header rows
        if len(rows) > 3:
            rows = rows[3:]

        # Remove empty rows
        clean_rows = []
        for r in rows:
            if any(cell.strip() for cell in r):
                clean_rows.append(r)

        return clean_rows

    # ============================
    # FIX MERGED COLUMNS
    # ============================
    def normalize_row(self, row):
        """
        Google Sheet merge → CSV bị lệch cột
        Fix bằng cách ép row có đúng 29 cột
        """
        if len(row) < self.EXPECTED_COLS:
            row = row + [""] * (self.EXPECTED_COLS - len(row))
        elif len(row) > self.EXPECTED_COLS:
            row = row[:self.EXPECTED_COLS]
        return row

    # ============================
    # HELPERS
    # ============================
    def split_color(self, value):
        if not value:
            return None
        return [c.strip() for c in value.split("\n") if c.strip()]

    def split_message(self, value):
        if not value:
            return None

        messages = [m.strip() for m in value.split("\n\n\n") if m.strip()]
        result = []

        for msg in messages:
            parts = msg.split("\n\n")
            text = parts[0].strip() if parts else ""

            # Tách các image IDs theo dòng và thêm .jpg
            images = []
            if len(parts) > 1:
                image_ids = [img_id.strip() for img_id in parts[1].split("\n") if img_id.strip()]
                images = [img_id + ".jpg" for img_id in image_ids]

            result.append({"text": text, "images": images})

        return result
    def split_combo(self, *values):
        """Parse combo data from multiple cells, each with format:
        COMBO_NAME
        PRICE
        QUANTITY

        Multiple combos separated by \n\n\n
        """
        result = []

        for value in values:
            if not value:
                continue

            # Split by \n\n\n to get individual combos
            combos = [combo.strip() for combo in value.split('\n\n\n') if combo.strip()]

            for combo in combos:
                # Each combo has 3 lines: name, price, quantity
                lines = [line.strip() for line in combo.split('\n') if line.strip()]

                if len(lines) >= 3:
                    combo_name = lines[0]
                    price = self.safe_float(lines[1])
                    quantity = self.safe_int(lines[2])

                    result.append({
                        "combo_name": combo_name,
                        "price": price,
                        "quantity": quantity
                    })
                else:
                    print(f"[WARNING] Combo has insufficient data: {lines}")

        return result if result else None    
       
    def safe_float(self, value):
        try:
            return float(value) if value else None
        except:
            return None

    def safe_int(self, value):
        try:
            return int(float(value)) if value else None
        except:
            return None

    # ============================
    # CREATE PRODUCTS
    # ============================
    def create_products_from_rows(self, rows):
        products = []

        # enumerate from 4 → đúng với Google Sheet
        for sheet_row, raw_row in enumerate(rows, start=4):
            row = self.normalize_row(raw_row)

            try:
                product = Product(
                    id_page=self.safe_int(row[0]),
                    code=row[4],
                    image=self.split_color(row[5]),
                    color=self.split_color(row[6]),
                    price=self.safe_float(row[7]),
                    product_type=row[8],
                  
                    chat_lieu=row[9],

                    pancake_reply_price=self.split_message(row[12]),
                    message_1b=self.split_message(row[13]),
                    message_2b=self.split_message(row[14]),
                    message_3b=self.split_message(row[15]),
                    message_4b=self.split_message(row[16]),
                    message_cl=self.split_message(row[17]),
                    message_ld=self.split_message(row[18]),
                    pos_shop_id=row[2],
                    pos_product_code=row[19],
                    pos_product_name=row[20],
  
                    attr_color=self.split_color(row[21]),
                    attr_size=self.split_color(row[22]),
                    pos_product_price=self.safe_float(row[23]),
                    pos_product_combo=self.split_combo(row[24], row[25], row[26]),
                    mau=self.split_message(row[18]),
                    ma_anh=row[15],

                    gia_san_pham=self.safe_float(row[19]),
                    sale_price=self.safe_float(row[20]),
                    bao_gia_pancake=self.safe_float(row[21]),
                    botcake_price_instant=self.safe_float(row[22]),

                    comment_default=row[24],
                    comment_with_phone=row[25],
                    message_from_comment=row[26],
                    message_from_comment_with_phone=row[27],
                    send_message_type=row[28]
                )

                products.append(product)

            except Exception as e:
                print(f"[ERROR SHEET ROW {sheet_row}] {str(e)}")

        return products



def main():
    print("=== GOOGLE SHEET IMPORT ===")

    processor = SheetProcessor()

    try:
        rows = processor.get_sheet_data()
        print(f"Loaded {len(rows)} product rows")

        products = processor.create_products_from_rows(rows)
        print(f"Created {len(products)} Product objects")

        for i, p in enumerate(products, 1):
            print(f"\n--- Product {i} ---")
            print(f"Code: {getattr(p, 'code', 'N/A')}")
            print(f"Name: {getattr(p, 'product_name', 'N/A')}")
            print(f"Shop ID: {getattr(p, 'pos_shop_id', 'N/A')}")
            try:
                p.display()
            except:
                print("[OK]")

    except Exception as e:
        print("[ERROR]", e)


if __name__ == "__main__":
    main()
