#!/usr/bin/env python3
"""
Image Processor - Handles image download and upload operations
"""

import concurrent.futures
from typing import List, Dict, Any, Optional

# Import services
from Service.DriverImages import GoogleDriveImageDownloader
from Service.PancakeApi import PancakeAPI

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class ImageProcessor:
    """
    Handles all image-related operations: download and upload
    """

    def __init__(self):
        self.image_downloader = GoogleDriveImageDownloader()
        self.downloaded_images = {}  # Cache downloaded images
        self.uploaded_images = {}    # Cache uploaded images

    def process_product_images(self, product, pancake_api: PancakeAPI) -> bool:
        """
        Process all images for a product: download then upload

        Args:
            product: Product object with image list
            pancake_api: PancakeAPI instance for this product

        Returns:
            bool: True if all operations successful
        """
        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')

        try:
            log(f"[Thread-{thread_id}] Processing images for product: {product_code}", "INFO")

            # Step 1: Download images
            if not self._download_images_for_product(product):
                log(f"[Thread-{thread_id}] Failed to download images for {product_code}", "ERROR")
                return False

            # Step 2: Upload images
            if not self._upload_images_for_product(product, pancake_api):
                log(f"[Thread-{thread_id}] Failed to upload images for {product_code}", "ERROR")
                return False

            log(f"[Thread-{thread_id}] Completed image processing for {product_code}", "SUCCESS")
            return True

        except Exception as e:
            log(f"[Thread-{thread_id}] Exception processing images for {product_code}: {e}", "ERROR")
            return False

    def _download_images_for_product(self, product) -> bool:
        """Download images for a specific product with parallel processing"""
        product_images = getattr(product, 'image', [])
        if not product_images:
            return True

        # Filter valid image IDs
        valid_image_ids = [img_id.strip() for img_id in product_images
                          if img_id and isinstance(img_id, str) and img_id.strip()]

        if not valid_image_ids:
            return True

        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')
        log(f"[Thread-{thread_id}] Downloading {len(valid_image_ids)} images for {product_code} with parallel threads", "INFO")

        # Use ThreadPoolExecutor để download song song
        downloaded_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(valid_image_ids)) as executor:
            # Submit tất cả download tasks
            future_to_image_id = {
                executor.submit(self.image_downloader.download_image, image_id): image_id
                for image_id in valid_image_ids
            }

            # Collect results
            for future in concurrent.futures.as_completed(future_to_image_id):
                image_id = future_to_image_id[future]
                try:
                    local_path = future.result()
                    if local_path:
                        self.downloaded_images[image_id] = local_path
                        downloaded_count += 1
                        log(f"[Thread-{thread_id}] Downloaded {image_id}", "SUCCESS")
                    else:
                        log(f"[Thread-{thread_id}] Failed {image_id}", "ERROR")
                except Exception as e:
                    log(f"[Thread-{thread_id}] Exception downloading {image_id}: {e}", "ERROR")

        success = downloaded_count == len(valid_image_ids)
        log(f"[Thread-{thread_id}] Downloaded {downloaded_count}/{len(valid_image_ids)} images for {product_code}", "SUCCESS" if success else "WARNING")
        return success

    def _upload_images_for_product(self, product, pancake_api: PancakeAPI) -> bool:
        """Upload images for a specific product"""
        product_images = getattr(product, 'image', [])
        if not product_images:
            return True

        uploaded_count = 0
        for image_id in product_images:
            if image_id in self.downloaded_images:
                local_path = self.downloaded_images[image_id]
                if __import__('os').path.exists(local_path):
                    photo_obj = pancake_api.upload_to_pancake(local_path)
                    if photo_obj:
                        self.uploaded_images[image_id] = photo_obj
                        uploaded_count += 1

        return uploaded_count == len([img for img in product_images if img and isinstance(img, str) and img.strip()])
