#!/usr/bin/env python3
"""
Test script for combo creation logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cron_job import ProductCronJob
from Model.Product import Product

def test_combo_logic():
    """Test the combo creation logic"""

    # Create a mock cron job instance
    cron_job = ProductCronJob()

    # Mock product 1: New product
    product1 = Product(
        id_page=1,
        code="TEST001",
        image=[],
        color=[],
        price=100000,
        product_type="Test",
        chat_lieu="Test",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code="TEST001",
        pos_product_name="Test Product 1",
        pos_product_price=100000,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[],
        mau="",
        ma_anh=""
    )

    # Mock product 2: Existing product with code change
    product2 = Product(
        id_page=1,
        code="TEST002",
        image=[],
        color=[],
        price=200000,
        product_type="Test",
        chat_lieu="Test",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code="TEST002",
        pos_product_name="Test Product 2",
        pos_product_price=200000,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[],
        mau="",
        ma_anh=""
    )

    # Mock product 3: Existing product with content change only
    product3 = Product(
        id_page=1,
        code="TEST003",
        image=[],
        color=[],
        price=150000,  # Will be changed later
        product_type="Test",
        chat_lieu="Test",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code="TEST003",
        pos_product_name="Test Product 3",
        pos_product_price=150000,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[],
        mau="",
        ma_anh=""
    )

    print("=== Testing Combo Logic ===")

    # First run - all products are new
    print("\n1. First run - all products new:")
    changed, combos = cron_job._check_product_changes([product1, product2, product3])
    print(f"Changed products: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Combo products: {[getattr(p, 'code', '') for p in combos]}")

    # Second run - no changes
    print("\n2. Second run - no changes:")
    changed, combos = cron_job._check_product_changes([product1, product2, product3])
    print(f"Changed products: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Combo products: {[getattr(p, 'code', '') for p in combos]}")

    # Third run - product3 content changed (price)
    print("\n3. Third run - product3 price changed:")
    # Create new product3 with changed price
    product3_changed = Product(
        id_page=1,
        code="TEST003",
        image=[],
        color=[],
        price=180000,  # Changed price
        product_type="Test",
        chat_lieu="Test",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code="TEST003",
        pos_product_name="Test Product 3",
        pos_product_price=180000,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[],
        mau="",
        ma_anh=""
    )
    changed, combos = cron_job._check_product_changes([product1, product2, product3_changed])
    print(f"Changed products: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Combo products: {[getattr(p, 'code', '') for p in combos]}")

    # Fourth run - product2 code changed (realistic scenario)
    print("\n4. Fourth run - product2 code changed:")
    # Simulate a real code change: same content but different code
    product2_code_changed = Product(
        id_page=1,
        code="TEST002_NEW",  # Changed code
        image=[],  # Same content as original
        color=[],
        price=200000,
        product_type="Test",
        chat_lieu="Test",
        pancake_reply_price=[],
        message_1b=[],
        message_2b=[],
        message_3b=[],
        message_4b=[],
        message_cl=[],
        message_ld=[],
        pos_shop_id=123,
        pos_product_code="TEST002_NEW",
        pos_product_name="Test Product 2",
        pos_product_price=200000,
        attr_color=[],
        attr_size=[],
        pos_product_combo=[],
        mau="",
        ma_anh=""
    )
    changed, combos = cron_job._check_product_changes([product1, product2_code_changed, product3_changed])
    print(f"Changed products: {[getattr(p, 'code', '') for p in changed]}")
    print(f"Combo products: {[getattr(p, 'code', '') for p in combos]}")

if __name__ == "__main__":
    test_combo_logic()
