#!/usr/bin/env python3
"""
Settings Processor - Handles Pancake settings update operations
"""

from typing import List, Dict, Any, Optional
import json
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

        # Map shortcut patterns to product message field
        shortcut_to_field = {
            '1b': 'message_1b',
            '2b': 'message_2b',
            '3b': 'message_3b',
            '4b': 'message_4b',
            'cl': 'message_cl',
            'ld': 'message_ld'
        }

        for reply in current_replies:
            reply_shortcut = reply.get('shortcut', '')
            if reply_shortcut in shortcut_to_field:
                field_name = shortcut_to_field[reply_shortcut]
                product_messages = getattr(product, field_name, [])
                
                if product_messages and 'messages' in reply:
                    for i, reply_message in enumerate(reply['messages']):
                        if i < len(product_messages):
                            product_msg = product_messages[i]

                            if 'text' in product_msg:
                                reply_message['message'] = product_msg['text']

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
            updated_replies.append(reply)

        # Update first reply with pancake_reply_price
        try:
            if updated_replies and hasattr(product, 'pancake_reply_price') and product.pancake_reply_price:
                first_reply = updated_replies[0]
                updated_replies[0]['shortcut']=product.code
                if 'messages' in first_reply and first_reply['messages']:
                    product_messages = getattr(product, 'pancake_reply_price', [])
                    if isinstance(product_messages, list):

                        for i, reply_message in enumerate(first_reply['messages']):
                            if i < len(product_messages):
                                product_msg = product_messages[i]

                                if isinstance(product_msg, dict):
                                    if 'text' in product_msg:
                                        reply_message['message'] = product_msg['text']

                                    if 'images' in product_msg and product_msg['images']:
                                        updated_photos = []
                                        for img_id in product_msg['images']:
                                            # Try multiple matching strategies
                                            found = False
                                            if img_id in uploaded_images:
                                                photo_obj = uploaded_images[img_id]
                                                found = True
                                            elif str(img_id) in uploaded_images:
                                                photo_obj = uploaded_images[str(img_id)]
                                                found = True
                                            else:
                                                # Try removing .jpg extension
                                                img_id_no_ext = img_id.replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                                                if img_id_no_ext in uploaded_images:
                                                    photo_obj = uploaded_images[img_id_no_ext]
                                                    found = True
                                                else:
                                                    # Try matching by filename in photo_obj.name
                                                    for key, photo_data in uploaded_images.items():
                                                        photo_name = photo_data.get('name', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                                                        if photo_name == img_id_no_ext or photo_data.get('name') == img_id:
                                                            photo_obj = photo_data
                                                            found = True
                                                            break

                                            if found:
                                                # Sử dụng TOÀN BỘ data từ Pancake API response
                                                updated_photos.append(photo_obj.copy())
                                            else:
                                                # Try to get full data from photo_obj if available, otherwise create fallback
                                                photo_obj = uploaded_images.get(img_id)
                                                if photo_obj:
                                                    updated_photos.append(photo_obj.copy())
                                                else:
                                                    # Create a basic photo object for missing images
                                                    updated_photos.append({
                                                        'id': img_id,
                                                        'url': f"https://content.pancake.vn/2-2601/2026/1/8/{img_id}",
                                                        'preview_url': f"https://content.pancake.vn/2-2601/2026/1/8/{img_id}",
                                                        'name': img_id,
                                                        'image_data': {'height': 1000, 'width': 600}
                                                    })
                                        reply_message['photos'] = updated_photos
        except Exception as e:
            print(f"[ERROR] Failed to update first reply: {e}")

        return updated_replies
