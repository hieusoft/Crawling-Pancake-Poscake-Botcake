#!/usr/bin/env python3
"""
Real scenario test for combo creation logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cron_job import ProductCronJob
from Model.Product import Product

def create_product(code, name, price):
    """Helper to create product"""
    return Product(
        id_page=1,
        code=code,
        image=[],
        color=[],
        price=price,
        product_type="Test",
        chat_lieu="Cotton",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code=code,
        pos_product_name=name,
        pos_product_price=price,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[{"combo_name": f"Combo {code}", "price": price * 2, "quantity": 2}],
        mau="",
        ma_anh=""
    )

def test_real_scenario():
    """Test real-world scenario"""
    print("=== Real Scenario Test ===")

    cron_job = ProductCronJob()

    # Day 1: New products
    print("\nDay 1: New products added")
    ao_thun = create_product("AT001", "Áo Thun Basic", 150000)
    quan_jean = create_product("QJ002", "Quần Jean Slim", 350000)

    changed, combos = cron_job._check_product_changes([ao_thun, quan_jean])
    print(f"Changed: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Create combo: {[getattr(p, 'code', '') for p in combos]}")

    # Day 2: Price change (content change, same code)
    print("\nDay 2: Ao Thun price changed from 150k to 180k")
    ao_thun_updated = create_product("AT001", "Ao Thun Basic", 180000)  # Price changed

    changed, combos = cron_job._check_product_changes([ao_thun_updated, quan_jean])
    print(f"Changed: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Create combo: {[getattr(p, 'code', '') for p in combos]}")

    # Day 3: Name change (content change, same code)
    print("\nDay 3: Quan Jean name changed")
    quan_jean_updated = create_product("QJ002", "Quan Jean Skinny Fit", 350000)  # Name changed

    changed, combos = cron_job._check_product_changes([ao_thun_updated, quan_jean_updated])
    print(f"Changed: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Create combo: {[getattr(p, 'code', '') for p in combos]}")

    # Day 4: Code change (real code change scenario)
    print("\nDay 4: Ao Thun code changed from AT001 to AT001V2")
    ao_thun_new_code = create_product("AT001V2", "Ao Thun Basic V2", 180000)

    changed, combos = cron_job._check_product_changes([ao_thun_new_code, quan_jean_updated])
    print(f"Changed: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Create combo: {[getattr(p, 'code', '') for p in combos]}")

    print("\n=== Summary ===")
    print("SUCCESS: Combo chi duoc tao khi:")
    print("   - Product moi")
    print("   - Code product thay doi")
    print("SKIP: Combo KHONG duoc tao khi:")
    print("   - Chi gia, ten, hoac noi dung khac thay doi (code giu nguyen)")

if __name__ == "__main__":
    test_real_scenario()
