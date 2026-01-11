#!/usr/bin/env python3
"""
Main workflow script for Pancake Bot
"""

import sys
import os
import concurrent.futures
from typing import List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Worker.SheetProcess import SheetProcessor
from Core.ProductProcessor import ProductProcessor
from Model.Product import Product

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class MainWorkflow:
    """
    Main workflow orchestrator for Pancake Bot
    """

    def __init__(self, page_id: str, access_token: str = None):
        """Initialize workflow"""
        self.page_id = page_id
        self.access_token = access_token or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGlldSIsImV4cCI6MTc3NDc1NzA1NywiYXBwbGljYXRpb24iOjEsInVpZCI6ImFjNmU3MjQ0LWYyZTQtNGUxNy04YTk5LTgzNDA3NjhiOWZmMSIsInNlc3Npb25faWQiOiJmZDU3NzIzMy0yYzJjLTRiMzAtODBjOS03ODQ0NGRmNWRmZDUiLCJpYXQiOjE3NjY5ODEwNTcsImZiX2lkIjoiMjM4NDQwNzc5NTE3Njc4MCIsImxvZ2luX3Nlc3Npb24iOm51bGwsImZiX25hbWUiOiJoaWV1In0.sE7-XOHDgrPSGf_oisgH8Ezr90-1Rzyhpb_3btFdqKs"
        self.sheet_processor = SheetProcessor()
        self.product_processor = ProductProcessor(access_token=self.access_token)
        self.products: List[Product] = []

    def run_full_workflow(self) -> bool:
        """Run complete workflow with parallel product processing"""
        try:
            if not self._fetch_sheet_data():
                log("Failed to fetch sheet data", "ERROR")
                return False

            log(f"Loaded {len(self.products)} products, starting parallel processing", "INFO")
            success_count = self._process_products_parallel()
            success = success_count == len(self.products)
            log(f"Processed {success_count}/{len(self.products)} products", "SUCCESS" if success else "WARNING")
            return success

        except Exception as e:
            log(f"Workflow failed: {e}", "ERROR")
            return False

    def _fetch_sheet_data(self) -> bool:
        """Fetch and process sheet data"""
        try:
            rows = self.sheet_processor.get_sheet_data()
            if not rows:
                return False
            self.products = self.sheet_processor.create_products_from_rows(rows)
            return bool(self.products)
        except Exception as e:
            log(f"Error fetching sheet data: {e}", "ERROR")
            return False

    def _process_products_parallel(self) -> int:
        """Process all products in parallel threads"""
        success_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.products)) as executor:
            future_to_product = {
                executor.submit(self.product_processor.process_product, product): product
                for product in self.products
            }
            for future in concurrent.futures.as_completed(future_to_product):
                product = future_to_product[future]
                try:
                    if future.result():
                        success_count += 1
                        log(f"Product {getattr(product, 'code', 'Unknown')} completed", "SUCCESS")
                except Exception as e:
                    log(f"Product processing error: {e}", "ERROR")
        return success_count


def fetch_products_and_get_page_id(access_token: str = None):
    """Fetch products from sheet and return page_id from product data"""
    temp_workflow = MainWorkflow("temp_page_id", access_token)
    if temp_workflow._fetch_sheet_data() and temp_workflow.products:
        page_id = temp_workflow.products[0].id_page
        return temp_workflow.products, str(page_id) if page_id else None
    return [], None


def main():
    """Main function"""
    print("=== PANCAKE BOT WORKFLOW ===")

    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGlldSIsImV4cCI6MTc3NDc1NzA1NywiYXBwbGljYXRpb24iOjEsInVpZCI6ImFjNmU3MjQ0LWYyZTQtNGUxNy04YTk5LTgzNDA3NjhiOWZmMSIsInNlc3Npb25faWQiOiJmZDU3NzIzMy0yYzJjLTRiMzAtODBjOS03ODQ0NGRmNWRmZDUiLCJpYXQiOjE3NjY5ODEwNTcsImZiX2lkIjoiMjM4NDQwNzc5NTE3Njc4MCIsImxvZ2luX3Nlc3Npb24iOm51bGwsImZiX25hbWUiOiJoaWV1In0.sE7-XOHDgrPSGf_oisgH8Ezr90-1Rzyhpb_3btFdqKs"
    products, page_id = fetch_products_and_get_page_id(access_token)
    if not products:
        log("No products available", "ERROR")
        return

    page_id = page_id or "201128346428245"  # Default fallback
    workflow = MainWorkflow(page_id, access_token)
    workflow.products = products

    success = workflow.run_full_workflow()
    status = "SUCCESS" if success else "FAILED"
    print(f"\n[{status}] WORKFLOW COMPLETED!")
    print(f"  Products loaded: {len(products)}")


if __name__ == "__main__":
    main()
