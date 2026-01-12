#!/usr/bin/env python3
"""
Product Processor - Handles individual product workflow processing
Workflow: Images → Settings → POS Creation → Verification
"""

from typing import List, Dict, Any, Optional

# Import services and processors
from Service.PancakeApi import PancakeAPI
from Service.PoscakeApi import PosAPI
from Core.ImageProcessor import ImageProcessor
from Core.SettingsProcessor import SettingsProcessor

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class ProductProcessor:
    """
    Handles complete workflow processing for individual products
    """

    def __init__(self, access_token: str = None):
        self.access_token = access_token
        self.image_processor = ImageProcessor()
        self.settings_processor = SettingsProcessor()

    def process_product(self, product) -> bool:
        """
        Process a complete product workflow: download, upload, update, pos, verify

        Args:
            product: Product object to process

        Returns:
            bool: True if successful
        """
        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')
        product_page_id = str(getattr(product, 'id_page', 'default_page_id'))

        try:
            log(f"[Thread-{thread_id}] Processing product: {product_code} (Page ID: {product_page_id}) - Steps: Images, Settings, POS, Verify", "INFO")

            # Tạo PancakeAPI instance riêng cho page_id của product này
            pancake_api = PancakeAPI(page_id=product_page_id, access_token=self.access_token)

            # # Step 1: Process images (download & upload)
            # if not self.image_processor.process_product_images(product, pancake_api):
            #     log(f"[Thread-{thread_id}] Failed to process images for {product_code}", "ERROR")
            #     return False

            # # Step 2: Update settings (optional - continue even if fails)
            # if not self.settings_processor.update_product_settings(
            #     product,
            #     pancake_api,
            #     self.image_processor.uploaded_images
            # ):
            #     log(f"[Thread-{thread_id}] Settings update failed for {product_code}, but continuing...", "WARNING")

            # Step 3: Create product on POS Pancake
            # if not self.create_pos_product(product):
            #     log(f"[Thread-{thread_id}] Failed to create POS product for {product_code}", "ERROR")
            #     return False

            # Step 4: Verify POS product creation by searching
            if not self.verify_pos_product(product):
                log(f"[Thread-{thread_id}] POS product verification failed for {product_code}", "WARNING")
                # Don't return False here, as POS creation might have succeeded but search failed

            log(f"[Thread-{thread_id}] Completed product: {product_code}", "SUCCESS")
            return True

        except Exception as e:
            log(f"[Thread-{thread_id}] Exception processing {product_code}: {e}", "ERROR")
            return False

    def create_pos_product(self, product) -> bool:
        """
        Create product on POS Pancake system

        Args:
            product: Product object to create

        Returns:
            bool: True if successful
        """
        try:
            # Initialize PosAPI
            pos_api = PosAPI()

            # Create product data from Product object with uploaded images
            product_data = pos_api.create_product_data(product, self.image_processor.uploaded_images)

            
            result = pos_api.send_product(product_data)
            if result.get("success"):
                log(f"Successfully created POS product: {getattr(product, 'code', 'Unknown')}", "SUCCESS")
                return True
            else:
                log(f"Failed to create POS product: HTTP {result.get('status_code')}", "ERROR")
                # Avoid logging response_text to prevent Unicode encoding issues
                log("Check response details above for error info", "ERROR")
                return False

        except Exception as e:
            log(f"Exception creating POS product: {e}", "ERROR")
            return False

    def verify_pos_product(self, product) -> bool:
        """
        Verify POS product creation by searching for the product

        Args:
            product: Product object to verify

        Returns:
            bool: True if product found, False otherwise
        """
        try:
            pos_api = PosAPI()

            # Get product code to search for - try pos_product_code first, then code
            product_code = getattr(product, 'pos_product_code', '') or getattr(product, 'code', '')

            log(f"Verifying POS product with code: '{product_code}'", "INFO")

            if not product_code:
                log("No product code available for verification", "WARNING")
                return False

            # Search for the product
            search_result = pos_api.search_product_by_code(product_code)

            if search_result and search_result.get("products_found", 0) > 0:
                first_product = search_result.get("first_product", {})
                log(f"✓ POS product verified: {first_product.get('name', 'Unknown')} (ID: {first_product.get('id', 'N/A')})", "SUCCESS")
                log(f"   Total products in shop: {search_result.get('total_entries', 0)}", "INFO")
                # Store the products data for potential future use
                self.last_search_results = search_result.get("products", [])
                return True
            else:
                total_in_shop = search_result.get("total_entries", 0) if search_result else 0
                log(f"✗ POS product not found: {product_code} (total in shop: {total_in_shop})", "WARNING")
                # Let's also try with the raw 'code' attribute in case pos_product_code is different
                raw_code = getattr(product, 'code', '')
                if raw_code and raw_code != product_code:
                    log(f"Trying search with raw code: '{raw_code}'", "INFO")
                    search_result2 = pos_api.search_product_by_code(raw_code)
                    if search_result2 and search_result2.get("products_found", 0) > 0:
                        first_product = search_result2.get("first_product", {})
                        log(f"✓ POS product found with raw code: {first_product.get('name', 'Unknown')}", "SUCCESS")
                        self.last_search_results = search_result2.get("products", [])
                        return True

                return False

        except Exception as e:
            log(f"Exception verifying POS product: {e}", "ERROR")
            return False

