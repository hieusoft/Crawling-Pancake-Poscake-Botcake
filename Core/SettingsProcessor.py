#!/usr/bin/env python3
"""
Settings Processor - Handles Pancake settings update operations
"""

from typing import List, Dict, Any, Optional

# Import services
from Service.PancakeApi import PancakeAPI

# Simple logger
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class SettingsProcessor:
    """
    Handles Pancake settings update operations
    """

    def __init__(self):
        pass

    def update_product_settings(self, product, pancake_api: PancakeAPI, uploaded_images: Dict[str, Any]) -> bool:
        """
        Update Pancake settings for a specific product

        Args:
            product: Product object to update settings for
            pancake_api: PancakeAPI instance for this product
            uploaded_images: Dict of uploaded image objects

        Returns:
            bool: True if update successful
        """
        thread_id = __import__('threading').current_thread().ident
        product_code = getattr(product, 'code', 'Unknown')

        try:
            log(f"[Thread-{thread_id}] Updating settings for product: {product_code}", "INFO")

            # Get current settings (both key and replies in one call)
            settings_data = pancake_api.get_current_settings()
            if not settings_data:
                log(f"[Thread-{thread_id}] Failed to get current settings for {product_code}", "ERROR")
                return False
           
            settings_key = settings_data.get("current_settings_key")
            current_replies = settings_data.get("quick_replies", [])

            if not settings_key:
                log(f"[Thread-{thread_id}] No settings key found for {product_code}", "ERROR")
                return False

            # Create updated replies for this product only
            updated_replies = self._create_replies_for_product(current_replies, product, uploaded_images)

            # Update settings
            success = pancake_api.update_settings(updated_replies, settings_key)
            if success:
                log(f"[Thread-{thread_id}] Settings updated successfully for {product_code}", "SUCCESS")
            else:
                log(f"[Thread-{thread_id}] Failed to update settings for {product_code}", "ERROR")

            return success

        except Exception as e:
            log(f"[Thread-{thread_id}] Exception updating settings for {product_code}: {e}", "ERROR")
            return False
    
    def _create_replies_for_product(self, current_replies, product, uploaded_images: Dict[str, Any]):
        """Create updated replies for a specific product"""
        updated_replies = []

        # Map shortcut patterns to product message fields
        product_code = getattr(product, 'code', '').upper()
        shortcut_to_field = {
            product_code: product_code,  # Key = Value for product code
            '1b': 'message_1b',
            '2b': 'message_2b',
            '3b': 'message_3b',
            '4b': 'message_4b',
            'cl': 'message_cl',
            'ld': 'message_ld'
        }
        print(shortcut_to_field)
        for reply in current_replies:
            reply_shortcut = reply.get('shortcut', '').lower()
            
            # Update messages based on shortcut
            if reply_shortcut in shortcut_to_field:
                field_name = shortcut_to_field[reply_shortcut]
                product_messages = getattr(product, field_name, [])
                
                if product_messages and 'messages' in reply:
                    # Update each message in the reply
                    for i, reply_message in enumerate(reply['messages']):
                        if i < len(product_messages):
                            product_msg = product_messages[i]

                            # Update message text
                            if 'text' in product_msg:
                                reply_message['message'] = product_msg['text']

                            # Update message images
                            if 'images' in product_msg and product_msg['images']:
                                updated_photos = []
                                for img_id in product_msg['images']:
                                    if img_id in uploaded_images:
                                        photo_obj = uploaded_images[img_id]
                                        updated_photos.append({
                                            'id': photo_obj.get('id', ''),
                                            'url': photo_obj.get('url', ''),
                                            'preview_url': photo_obj.get('preview_url', ''),
                                            'name': photo_obj.get('name', ''),
                                            'image_data': photo_obj.get('image_data', {})
                                        })
                                reply_message['photos'] = updated_photos

            # Also update main product images if shortcut matches product code
            reply_code = reply.get('code', '')
            if reply_code == getattr(product, 'code', ''):
                if 'messages' in reply and reply['messages']:
                    first_message = reply['messages'][0]
                    if 'photos' in first_message and hasattr(product, 'image') and product.image:
                        updated_images = []
                        for img_id in product.image:
                            if img_id in uploaded_images:
                                photo_obj = uploaded_images[img_id]
                                updated_images.append({
                                    'id': photo_obj.get('id', ''),
                                    'url': photo_obj.get('url', ''),
                                    'preview_url': photo_obj.get('preview_url', ''),
                                    'name': photo_obj.get('name', ''),
                                    'image_data': photo_obj.get('image_data', {})
                                })
                        first_message['photos'] = updated_images

            updated_replies.append(reply)

        return updated_replies
