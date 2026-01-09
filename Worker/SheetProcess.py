import requests
from io import StringIO
import csv
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.Product import Product

class SheetProcessor:
    def __init__(self, spreadsheet_id="1Rway6WCREH6bj7PiEpS-HRuhMRKyYItaWJPzW0JIRmY"):
        self.spreadsheet_id = spreadsheet_id

    def get_sheet_data(self, gid="0"):
        """Fetch data from Google Sheets and return as list of rows"""
        sheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv&gid={gid}"
        res = requests.get(sheet_url)
        res.raise_for_status()

        f = StringIO(res.content.decode('utf-8'))
        reader = csv.reader(f)
        rows = list(reader)
        return rows

    def create_products_from_rows(self, rows, start_row=3, num_rows=2):
        """Create Product objects from sheet rows starting from start_row"""
        products = []

        # Ensure we have enough rows
        if len(rows) <= start_row:
            return products

        # Process specified number of rows
        for i in range(start_row, min(start_row + num_rows, len(rows))):
            row = rows[i]

            try:
                # Convert numeric values
                def split_color(value):
                    
                    if not value:
                        return None
                    
                    colors = [color.strip() for color in value.split('\n') if color.strip()]
                    return colors if colors else None
                def split_message(value):
                    
                    if not value:
                        return None

                    messages = [message.strip() for message in value.split('\n\n\n') if message.strip()]


                    messages_dicts = []                    
                    for msg in messages:
                        parts = msg.split('\n\n')
                        text = parts[0].strip() if parts else ""
                        images = parts[1].strip() if len(parts) > 1 else ""
                        messages_dicts.append({"text": text, "images": images})
                    return messages_dicts


                  
                def safe_float(value):
                    try:
                        return float(value) if value else None
                    except:
                        return None

                def safe_int(value):
                    try:
                        return int(float(value)) if value else None
                    except:
                        return None
                print( row[1])
                product = Product(
                    id_page=safe_int(row[0]) if len(row) > 0 else None,
                    code=row[1] if len(row) > 1 else None,
                    image=row[2] if len(row) > 2 else None,
                    color=split_color(row[3]) if len(row) > 3 else None,
                    price=safe_float(row[4]) if len(row) > 4 else None,
                    product_type=row[5] if len(row) > 5 else None,
                    product_name=row[6] if len(row) > 6 else None,
                    chat_lieu=row[7] if len(row) > 7 else None,
                    pancake_reply_price=split_message(row[9]) if len(row) > 9 else None,
                    message_b1=split_message(row[10]) if len(row) > 10 else None,
                    message_b2=split_message(row[11]) if len(row) > 11 else None,
                    message_b3=split_message(row[12]) if len(row) > 12 else None,
                    message_b4=split_message(row[13]) if len(row) > 13 else None,
                    message_cl=split_message(row[14]) if len(row) > 14 else None,
                    message_ld=split_message(row[15]) if len(row) > 15 else None,
                    pos_product_code=row[16] if len(row) > 15 else None,
                    pos_product_name=row[17] if len(row) > 16 else None,

                    attr_color=split_color(row[18]) if len(row) > 17 else None,
                    attr_size=split_color(row[19]) if len(row) > 18 else None,
                    mau=split_message(row[18]) if len(row) > 18 else None,
                    ma_anh=row[15] if len(row) > 15 else None,
                    gia_san_pham=safe_float(row[19]) if len(row) > 19 else None,
                    sale_price=safe_float(row[20]) if len(row) > 20 else None,
                    bao_gia_pancake=safe_float(row[21]) if len(row) > 21 else None,
                    botcake_price_instant=safe_float(row[22]) if len(row) > 22 else None,
                    combo_name=row[23] if len(row) > 23 else None,

                    comment_default=row[24] if len(row) > 24 else None,
                    comment_with_phone=row[25] if len(row) > 25 else None,
                    message_from_comment=row[26] if len(row) > 26 else None,
                    message_from_comment_with_phone=row[27] if len(row) > 27 else None,
                    send_message_type=row[28] if len(row) > 28 else None
                )
                
                products.append(product)

            except Exception as e:
                print(f"[WARNING] Error creating product from row {i}: {e}")
                continue

        return products


def main():
    """Test function for SheetProcessor"""
    print("=== Testing SheetProcessor ===")

    # Create processor instance
    processor = SheetProcessor()

    try:
        print("Loading data from Google Sheets...")
        rows = processor.get_sheet_data()

        print(f"[SUCCESS] Loaded {len(rows)} rows of data")

        # Create products from rows 3 and 4 (start_row=3, num_rows=2)
        print("\nCreating products from rows 3 and 4...")
        products = processor.create_products_from_rows(rows, start_row=3, num_rows=2)

        print(f"[SUCCESS] Created {len(products)} product objects")

        # Display product information
        for i, product in enumerate(products, 1):
            print(f"\n--- Product {i} ---")
            # Show color info
            # if hasattr(product, 'color') and product.color:
            #     print(f"[INFO] Color array: {len(product.color)} colors")

            # try:
            #     product.display()
            # except UnicodeEncodeError:
            #     print("[Unicode display issue - product created successfully]")

        print(f"\n=== Test completed! Created {len(products)} products ===")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n=== Test failed! ===")


if __name__ == "__main__":
    main()
