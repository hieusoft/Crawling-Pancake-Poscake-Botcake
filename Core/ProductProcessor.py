#!/usr/bin/env python3
"""
Product Processor - Handles individual product workflow processing
"""

from typing import List, Dict, Any, Optional

# Import services and processors
from Service.PancakeApi import PancakeAPI
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
        Process a complete product workflow: download → upload → update

        Args:
            product: Product object to process

        Returns:
            bool: True if successful
        """
        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')
        product_page_id = str(getattr(product, 'id_page', 'default_page_id'))

        try:
            log(f"[Thread-{thread_id}] Processing product: {product_code} (Page ID: {product_page_id})", "INFO")

            # Tạo PancakeAPI instance riêng cho page_id của product này
            pancake_api = PancakeAPI(page_id=product_page_id, access_token=self.access_token)

            # Step 1: Process images (download & upload)
            if not self.image_processor.process_product_images(product, pancake_api):
                log(f"[Thread-{thread_id}] Failed to process images for {product_code}", "ERROR")
                return False

            # Step 2: Update settings
            if not self.settings_processor.update_product_settings(
                product,
                pancake_api,
                self.image_processor.uploaded_images
            ):
                log(f"[Thread-{thread_id}] Failed to update settings for {product_code}", "ERROR")
                return False

            log(f"[Thread-{thread_id}] Completed product: {product_code}", "SUCCESS")
            return True

        except Exception as e:
            log(f"[Thread-{thread_id}] Exception processing {product_code}: {e}", "ERROR")
            return False
