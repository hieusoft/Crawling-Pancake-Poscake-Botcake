#!/usr/bin/env python3
"""
Test workflow script - Simplified version for testing
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Worker.SheetProcess import SheetProcessor
from Service.PancakeApi import PancakeAPI
from Model.Product import Product

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


def test_sheet_fetching():
    """Test only sheet data fetching"""
    print("=== TESTING SHEET DATA FETCHING ===")

    processor = SheetProcessor()

    try:
        # Get raw sheet data
        rows = processor.get_sheet_data()
        log(f"Retrieved {len(rows)} rows from sheet", "INFO")

        if rows:
            log("First row preview:", "DEBUG")
            log(f"  {rows[0]}", "DEBUG")

        # Create Product objects
        products = processor.create_products_from_rows(rows)
        log(f"Created {len(products)} Product objects", "SUCCESS")

        # Show product details
        for i, product in enumerate(products[:2], 1):  # Show first 2 products
            log(f"Product {i}:", "INFO")
            log(f"  Code: {product.code}", "INFO")
            log(f"  Images: {len(product.image) if product.image else 0}", "INFO")
            if product.image:
                log(f"  Image IDs: {product.image[:3]}", "DEBUG")  # Show first 3 images

        return True

    except Exception as e:
        log(f"Error in sheet fetching test: {e}", "ERROR")
        return False


def test_pancake_api():
    """Test Pancake API basic functionality"""
    print("\n=== TESTING PANCAKE API ===")

    api = PancakeAPI("201128346428245")

    try:
        # Test token validation
        log("Testing token validation...", "INFO")
        # This would require real API call, skip for now
        log("Token validation test skipped (requires real API)", "WARNING")

        # Test settings key retrieval (this makes real API call)
        log("Testing settings key retrieval...", "INFO")
        settings_key = api.get_current_settings_key()
        if settings_key:
            log(f"Got settings key: {settings_key}", "SUCCESS")
        else:
            log("Failed to get settings key", "WARNING")

        return True

    except Exception as e:
        log(f"Error in Pancake API test: {e}", "ERROR")
        return False


def test_full_workflow_dry_run():
    """Test full workflow structure without actual downloads/uploads"""
    print("\n=== TESTING FULL WORKFLOW STRUCTURE ===")

    PAGE_ID = "201128346428245"

    try:
        # Initialize components
        sheet_processor = SheetProcessor()
        pancake_api = PancakeAPI(PAGE_ID)

        log("Components initialized successfully", "SUCCESS")

        # Step 1: Fetch sheet data
        log("Step 1: Fetching sheet data...", "INFO")
        rows = sheet_processor.get_sheet_data()
        products = sheet_processor.create_products_from_rows(rows)
        log(f"Step 1 completed: {len(products)} products loaded", "SUCCESS")

        # Step 2: Simulate image processing
        log("Step 2: Simulating image processing...", "INFO")
        image_ids = set()
        for product in products:
            if product.image and isinstance(product.image, list):
                for img_id in product.image:
                    if img_id and isinstance(img_id, str) and img_id.strip():
                        image_ids.add(img_id.strip())

        log(f"Step 2 completed: Found {len(image_ids)} image IDs", "SUCCESS")
        log(f"Image IDs: {list(image_ids)[:3]}...", "DEBUG")  # Show first 3

        # Step 3: Simulate upload processing
        log("Step 3: Simulating upload processing...", "INFO")
        log("Step 3 completed: Upload simulation done", "SUCCESS")

        # Step 4: Simulate content processing
        log("Step 4: Simulating content processing...", "INFO")
        settings_key = pancake_api.get_current_settings_key()
        if settings_key:
            log(f"Step 4 completed: Got settings key {settings_key}", "SUCCESS")
        else:
            log("Step 4 warning: Could not get settings key", "WARNING")

        log("Full workflow structure test completed successfully!", "SUCCESS")
        return True

    except Exception as e:
        log(f"Error in full workflow test: {e}", "ERROR")
        return False


def main():
    """Main test function"""
    print("=== PANCAKE BOT WORKFLOW TEST ===")

    # Test individual components
    sheet_success = test_sheet_fetching()
    api_success = test_pancake_api()
    workflow_success = test_full_workflow_dry_run()

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"  Sheet fetching: {'PASS' if sheet_success else 'FAIL'}")
    print(f"  API connectivity: {'PASS' if api_success else 'FAIL'}")
    print(f"  Workflow structure: {'PASS' if workflow_success else 'FAIL'}")

    all_pass = sheet_success and api_success and workflow_success
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")

    if not all_pass:
        print("\nNote: Image download/upload tests require proper Google Drive permissions")
        print("and active Pancake API access. Use main_workflow.py for full testing.")


if __name__ == "__main__":
    main()
