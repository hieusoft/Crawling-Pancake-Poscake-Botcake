#!/usr/bin/env python3
"""
Product Processor - Handles individual product workflow processing
Workflow: Images → Settings → POS Creation → Verification → Combo Creation
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
        self.last_search_results = {}  # Store last search results to reuse in combo creation

    def process_product(self, product) -> bool:
        """
        Process a complete product workflow: images, settings, pos creation, verify, combo creation

        Args:
            product: Product object to process

        Returns:
            bool: True if successful
        """
        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')
        product_page_id = str(getattr(product, 'id_page', 'default_page_id'))

        try:
            log(f"[Thread-{thread_id}] Processing product: {product_code} (Page ID: {product_page_id}) - Steps: Images, Settings, POS, Verify, Combo", "INFO")

            # Tạo PancakeAPI instance riêng cho page_id của product này
            pancake_api = PancakeAPI(page_id=product_page_id, access_token=self.access_token)

            # Step 1: Process images (download & upload)
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

            # # Step 3: Create product on POS Pancake
            # if not self.create_pos_product(product):
            #     log(f"[Thread-{thread_id}] Failed to create POS product for {product_code}", "ERROR")
            #     return False

            # Step 4: Verify POS product creation by searching
            if not self.verify_pos_product(product):
                log(f"[Thread-{thread_id}] POS product verification failed for {product_code}", "WARNING")
                # Don't return False here, as POS creation might have succeeded but search failed

            # Step 5: Create combo products (optional - don't fail if combo creation fails)
            # Use the search result from step 4 to avoid re-searching
            if not self.create_combo_product(product):
                log(f"[Thread-{thread_id}] Combo product creation failed for {product_code}, but continuing...", "WARNING")
            
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
                log(f"POS product verified: {first_product.get('name', 'Unknown')} (ID: {first_product.get('id', 'N/A')})", "SUCCESS")
                log(f"   Total products in shop: {search_result.get('total_entries', 0)}", "INFO")
                # Store the product info for reuse in combo creation
                self.last_search_results = first_product
                
                return True
            else:
                total_in_shop = search_result.get("total_entries", 0) if search_result else 0
                log(f"POS product not found: {product_code} (total in shop: {total_in_shop})", "WARNING")
                # Let's also try with the raw 'code' attribute in case pos_product_code is different
                raw_code = getattr(product, 'code', '')
                if raw_code and raw_code != product_code:
                    log(f"Trying search with raw code: '{raw_code}'", "INFO")
                    search_result2 = pos_api.search_product_by_code(raw_code)
                    if search_result2 and search_result2.get("products_found", 0) > 0:
                        first_product = search_result2.get("first_product", {})
                        log(f"POS product found with raw code: {first_product.get('name', 'Unknown')}", "SUCCESS")
                        # Store the product info for reuse in combo creation
                        self.last_search_results = search_result2.get("first_product", {})
                        return True

                return False

        except Exception as e:
            log(f"Exception verifying POS product: {e}", "ERROR")
            return False

    def create_combo_product(self, product, search_result=None) -> bool:
        """
        Create combo products on POS Pancake system based on product.pos_product_combo

        Args:
            product: Product object to create combos from (must have pos_product_combo attribute)
            search_result: Search result from POS API (optional, will search if None)

        Returns:
            bool: True if all combos created successfully, False if any failed
        """
        try:
            # Get combo list from product
            combo_list = getattr(product, 'pos_product_combo', None)
            if not combo_list or not isinstance(combo_list, list) or len(combo_list) == 0:
                log("No pos_product_combo found or empty, skipping combo creation", "WARNING")
                return True  # Not an error, just no combos to create
            # Use provided search_result or fall back to stored one
            if search_result is None:
                # Try to get from stored results
                stored_product = getattr(self, 'last_search_results', None)
                if stored_product and isinstance(stored_product, dict):
                    # Convert stored product info back to search result format
                    search_result = {
                        "success": True,
                        "products_found": 1,
                        "first_product": stored_product,
                        "products": [stored_product]
                    }
                else:
                    search_result = None

            if search_result is None or search_result.get("products_found", 0) == 0:
                # Initialize PosAPI and search manually
                pos_api = PosAPI()
                product_code = getattr(product, 'pos_product_code', '') or getattr(product, 'code', '')

                if not product_code:
                    log("No product code available for combo creation", "ERROR")
                    return False

                log(f"Searching for product '{product_code}' to create combo", "INFO")
                search_result = pos_api.search_product_by_code(product_code)

                if not search_result or search_result.get("products_found", 0) == 0:
                    log(f"Product '{product_code}' not found, cannot create combo", "ERROR")
                    return False
            else:
                # Initialize PosAPI for combo creation
                pos_api = PosAPI()

            # Get product ID from search results
            product_id = search_result.get("first_product", {}).get("id")
            if not product_id:
                log("Could not get product ID from search results", "ERROR")
                return False

            # Track success/failure
            all_success = True
            created_combos = 0

            # Create each combo in the list
            for i, combo_config in enumerate(combo_list):
                try:
                    combo_name = combo_config.get("combo_name", f"Combo {i+1}")
                    combo_value = combo_config.get("price", 0)
                    count = combo_config.get("quantity", 1)

                    # Validate required fields
                    if not combo_name or combo_value <= 0 or count <= 0:
                        log(f"Invalid combo config at index {i}: name={combo_name}, price={combo_value}, quantity={count}", "WARNING")
                        all_success = False
                        continue

                    # Create combo data
                    combo_data = {
                        "combo_product": {
                            "discount_amount": 0,
                            "discount_by_percent": 0,
                            "max_discount_by_percent": 0,
                            "is_use_percent": False,
                            "is_free_shipping": False,
                            "name": combo_name,
                            "value_combo": int(combo_value),
                            "is_value_combo": True,
                            "bonus_products": [],
                            "is_variation": False,
                            "cal_value_variation": 0,
                            "variations": [
                                {
                                    "product": self.last_search_results,  # Use stored product info
                                    "count": count,
                                    "product_id": product_id,
                                    "variation_id": None,
                                    "variation": "",
                                }
                            ]
                        }
                    }

                    log(f"Creating combo {i+1}/{len(combo_list)}: {combo_name} (quantity: {count}, value: {combo_value})", "INFO")

                    # Create the combo product
                    result = pos_api.create_combo_product(combo_data)

                    if result.get("success"):
                        combo_id = result.get("data", {}).get("id")
                        log(f"Successfully created combo product (ID: {combo_id})", "SUCCESS")
                        created_combos += 1
                    else:
                        log(f"Failed to create combo product - {result.get('error', 'Unknown error')}", "ERROR")
                        all_success = False

                except Exception as combo_error:
                    log(f"Exception creating combo {i+1}: {combo_error}", "ERROR")
                    all_success = False
                    continue

            log(f"Combo creation completed: {created_combos}/{len(combo_list)} combos created successfully", "INFO")
            return all_success

        except Exception as e:
            log(f"Exception creating combo product: {e}", "ERROR")
            return False
