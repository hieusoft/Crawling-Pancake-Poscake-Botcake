#!/usr/bin/env python3
"""
Cron Job for Automated Product Processing
Runs every 30 seconds to check for product changes and process new/changed products
"""

import sys
import os
import json
import time
from typing import Dict, Set, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Worker.SheetProcess import SheetProcessor
from Core.ProductProcessor import ProductProcessor
from Model.Product import Product

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


class ProductCronJob:
    """
    Cron job to monitor product changes and process automatically
    """

    def __init__(self, state_file: str = "product_state.json"):
        self.state_file = state_file
        self.sheet_processor = SheetProcessor()
        self.previous_products: Dict[str, Dict] = {}
        self.processed_codes: Set[str] = set()
        self.previous_codes: Dict[str, str] = {}  # Track previous code for each product hash

        # Load previous state
        self._load_state()

    def _load_state(self) -> None:
        """Load previous product state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.previous_products = data.get('products', {})
                    self.processed_codes = set(data.get('processed_codes', []))
                    self.previous_codes = data.get('previous_codes', {})
                log(f"Loaded state: {len(self.previous_products)} products, {len(self.processed_codes)} processed")
            else:
                log("No previous state file found, starting fresh")
        except Exception as e:
            log(f"Error loading state: {e}", "ERROR")

    def _save_state(self) -> None:
        """Save current product state to file"""
        try:
            data = {
                'products': self.previous_products,
                'processed_codes': list(self.processed_codes),
                'previous_codes': self.previous_codes,
                'last_updated': time.time()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log(f"Saved state: {len(self.previous_products)} products")
        except Exception as e:
            log(f"Error saving state: {e}", "ERROR")

    def _get_product_hash(self, product: Product) -> str:
        """Create a hash of product data to detect changes"""
        # Convert product to dict for hashing
        product_data = {
            'code': getattr(product, 'code', ''),
            'product_name': getattr(product, 'product_name', ''),
            'product_type': getattr(product, 'product_type', ''),
            'price': getattr(product, 'price', 0),
            'chat_lieu': getattr(product, 'chat_lieu', ''),
            'image_count': len(getattr(product, 'image', [])),
            'pancake_reply_price': bool(getattr(product, 'pancake_reply_price', None))
        }

        # Create a simple hash
        data_str = json.dumps(product_data, sort_keys=True, default=str)
        return str(hash(data_str))

    def _check_product_changes(self, current_products: List[Product]) -> tuple[List[Product], List[Product]]:
        """Check which products have changed or are new

        Returns:
            tuple: (products_to_process, products_need_new_combo)
        """
        changed_products = []
        combo_products = []  # Products that need new combo creation (code changed or new)

        current_product_map = {getattr(p, 'code', ''): p for p in current_products if getattr(p, 'code', '')}

        # Check for new or changed products
        for code, product in current_product_map.items():
            current_hash = self._get_product_hash(product)

            if code not in self.previous_products:
                # Check if this is actually a code change of an existing product
                # Look for products where the hash matches but code changed
                code_changed = False
                for prev_code, prev_hash in self.previous_products.items():
                    if prev_hash == current_hash and prev_code != code:
                        # This is a code change
                        log(f"PRODUCT CODE CHANGED from '{prev_code}' to '{code}' - will create new combo")
                        changed_products.append(product)
                        combo_products.append(product)
                        code_changed = True
                        break

                if not code_changed:
                    # Truly new product
                    log(f"NEW PRODUCT detected: {code}")
                    changed_products.append(product)
                    combo_products.append(product)  # New products need combo creation
            elif self.previous_products[code] != current_hash:
                # Existing product with content changes (but same code)
                log(f"PRODUCT CONTENT CHANGED (same code): {code}")
                changed_products.append(product)
                # Don't add to combo_products - only create combo when code changes

        # Update previous_products and previous_codes with current state
        self.previous_products = {code: self._get_product_hash(product) for code, product in current_product_map.items()}
        self.previous_codes = {code: code for code, product in current_product_map.items()}

        return changed_products, combo_products

    def _process_product(self, product: Product, create_combo: bool = True) -> bool:
        """Process a single product

        Args:
            product: Product to process
            create_combo: Whether to create combo products in step 5
        """
        product_code = getattr(product, 'code', 'Unknown')
        product_page_id = str(getattr(product, 'id_page', 'default_page_id'))

        # Skip if already processed
        if product_code in self.processed_codes:
            log(f"Skipping already processed product: {product_code}")
            return True

        try:
            log(f"Processing product: {product_code} (Page ID: {product_page_id})")

            # Create processor with page-specific token
            processor = ProductProcessor(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGlldSIsImV4cCI6MTc3NTkwMjAyNywiYXBwbGljYXRpb24iOjEsInVpZCI6ImFjNmU3MjQ0LWYyZTQtNGUxNy04YTk5LTgzNDA3NjhiOWZmMSIsInNlc3Npb25faWQiOiJkNWZlNDFjYS02YjU1LTQ4MzUtYTA2Ni0xZTA5MDdiMTVlM2QiLCJpYXQiOjE3NjgxMjYwMjcsImZiX2lkIjoiMjM4NDQwNzc5NTE3Njc4MCIsImxvZ2luX3Nlc3Npb24iOm51bGwsImZiX25hbWUiOiJoaWV1In0.K5l98Aeqa8mf8t6UdeuMotQRBQA6Fl7TmTh6z3S0jiw")

            # Process the product with combo flag
            if processor.process_product(product, create_combo=create_combo):
                self.processed_codes.add(product_code)
                log(f"SUCCESS: Processed product {product_code}")
                return True
            else:
                log(f"FAILED: Processing product {product_code}", "ERROR")
                return False

        except Exception as e:
            log(f"EXCEPTION processing {product_code}: {e}", "ERROR")
            return False

    def run_once(self) -> bool:
        """Run one cycle of the cron job"""
        try:
            log("=== CRON JOB START ===")

            # Fetch current products from sheet
            rows = self.sheet_processor.get_sheet_data()
            if not rows:
                log("No data from sheet", "WARNING")
                return False

            current_products = self.sheet_processor.create_products_from_rows(rows)
            log(f"Fetched {len(current_products)} products from sheet")

            # Check for changes
            changed_products, combo_products = self._check_product_changes(current_products)

            if not changed_products:
                log("No product changes detected")
                self._save_state()
                return True

            # Process changed products (only if not already processed)
            success_count = 0
            for product in changed_products:
                product_code = getattr(product, 'code', '')
                if product_code not in self.processed_codes:
                    # Pass combo creation flag to processor
                    should_create_combo = product_code in [getattr(p, 'code', '') for p in combo_products]
                    if self._process_product(product, create_combo=should_create_combo):
                        success_count += 1
                else:
                    log(f"Skipping already processed product: {product_code}")

            log(f"Processed {success_count}/{len(changed_products)} changed products")

            # Save state
            self._save_state()

            log("=== CRON JOB END ===")
            return success_count == len(changed_products)

        except Exception as e:
            log(f"Cron job failed: {e}", "ERROR")
            return False

    def run_forever_with_auto_reset(self, interval_seconds: int = 30) -> None:
        """Run cron job continuously with auto-reset processed codes"""
        log(f"Starting cron job with auto-reset every {interval_seconds}s")

        while True:
            try:
                # Reset processed codes mỗi lần chạy để xử lý lại tất cả
                self.processed_codes.clear()
                log(f"Auto-reset: Cleared {len(self.processed_codes)} processed codes")

                self.run_once()
            except KeyboardInterrupt:
                log("Cron job stopped by user")
                break
            except Exception as e:
                log(f"Cron job cycle failed: {e}", "ERROR")

            log(f"Sleeping for {interval_seconds} seconds...")
            time.sleep(interval_seconds)

    def run_forever(self, interval_seconds: int = 30) -> None:
        """Run cron job continuously every interval_seconds"""
        log(f"Starting cron job with {interval_seconds}s interval")

        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                log("Cron job stopped by user")
                break
            except Exception as e:
                log(f"Cron job cycle failed: {e}", "ERROR")

            log(f"Sleeping for {interval_seconds} seconds...")
            time.sleep(interval_seconds)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Product Cron Job")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=30, help="Interval in seconds (default: 30)")
    parser.add_argument("--state-file", default="product_state.json", help="State file path")
    parser.add_argument("--reset-processed", action="store_true", help="Reset processed codes (process all products)")

    args = parser.parse_args()

    cron_job = ProductCronJob(state_file=args.state_file)

    if args.reset_processed:
        cron_job.processed_codes.clear()
        log("Reset processed codes - will process all products")

    # Default behavior: run continuously with auto-reset
    if len(sys.argv) == 1:  # No arguments provided
        log("Running continuously with auto-reset every 30 seconds")
        cron_job.run_forever_with_auto_reset(interval_seconds=30)
    elif args.once:
        success = cron_job.run_once()
        sys.exit(0 if success else 1)
    else:
        cron_job.run_forever(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
