import requests
import json
import sys
import os
import unicodedata
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.Product import Product

# Simple logger function
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class PosAPI:
    """POS Pancake.vn API client for managing products"""

    def __init__(self, access_token: Optional[str] = None, shop_id: Optional[str] = None):
        """
        Initialize POS API client

        Args:
            access_token: POS access token
            shop_id: Shop ID
        """
        self.access_token = access_token or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGlldSIsImV4cCI6MTc3NTkwMjAyNywiYXBwbGljYXRpb24iOjEsInVpZCI6ImFjNmU3MjQ0LWYyZTQtNGUxNy04YTk5LTgzNDA3NjhiOWZmMSIsInNlc3Npb25faWQiOiJkNWZlNDFjYS02YjU1LTQ4MzUtYTA2Ni0xZTA5MDdiMTVlM2QiLCJpYXQiOjE3NjgxMjYwMjcsImZiX2lkIjoiMjM4NDQwNzc5NTE3Njc4MCIsImxvZ2luX3Nlc3Npb24iOm51bGwsImZiX25hbWUiOiJoaWV1In0.K5l98Aeqa8mf8t6UdeuMotQRBQA6Fl7TmTh6z3S0jiw"
        self.shop_id = shop_id or "3027495"
        self.base_url = f"https://pos.pancake.vn/api/v1/shops/{self.shop_id}"

        # Default headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        log(f"PosAPI initialized for shop: {self.shop_id}", "INFO")

    def remove_vietnamese_accents(self, text: str) -> str:
        """
        Remove Vietnamese accents from text using Unicode normalization

        Args:
            text: Text with Vietnamese accents

        Returns:
            Text without accents, uppercase, spaces preserved
        """
        # First handle special Vietnamese characters
        special_map = {
            'Đ': 'D', 'đ': 'd',
        }

        # Replace special characters first
        for special, replacement in special_map.items():
            text = text.replace(special, replacement)

        # Normalize to decomposed form (NFD) to separate base characters and accents
        normalized = unicodedata.normalize('NFD', text)

        # Remove combining characters (accents) but keep spaces
        without_accents = ''.join(
            char for char in normalized
            if unicodedata.category(char) != 'Mn'  # Nonspacing marks (accents)
        )

        # Convert to uppercase but keep spaces
        return without_accents.upper()

    def generate_variants(self, product: Product) -> List[Dict[str, Any]]:
        """
        Generate product variants from Product object

        Args:
            product: Product object containing variant data

        Returns:
            List of variant dictionaries
        """
        # Get data from Product object
        base_sku = getattr(product, 'code', 'DEFAULT')  # Use product code as base SKU
        colors = getattr(product, 'color', [])  # Product color array
        sizes = getattr(product, 'attr_size', [])  # Product size array
        price = int(getattr(product, 'pos_product_price', 0))  # Product price as int

        # Convert colors from array to dict format
        color_dicts = []
        if colors:
            for i, color in enumerate(colors):
                color_dicts.append({
                    "name": color,
                    "key": color  # Use actual color name as key
                })

        # Convert sizes from array to list
        size_list = sizes if sizes else []

        variants = []
        idx = 0
        for c_idx, c in enumerate(color_dicts):
            for s_idx, s in enumerate(size_list):
                sku = f"{base_sku}-{c['key']}-{s}"
                variants.append({
                    "index": idx,
                    "sku": sku,
                    "price": price,
                    "color_name": c["name"],
                    "color_key": c["key"],
                    "size": s
                })
                idx += 1
        return variants


    def create_product_data(self, product: Product, images: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create product data payload for POS API from Product object

        Args:
            product: Product object containing all product data

        Returns:
            Dict containing product data payload
        """
        # Get data from Product object
        base_sku = getattr(product, 'pos_product_code', 'DEFAULT')
        product_name = getattr(product, 'pos_product_name', 'Default Product')
        price = int(getattr(product, 'pos_product_price', 0))

        # Handle images: uploaded_images dict and image_ids list
        # images parameter should be uploaded_images dict from ImageProcessor
        # product.image contains list of image IDs
        uploaded_images = images if images and isinstance(images, dict) else {}
        image_ids = getattr(product, 'image', [])

        # Clean base SKU (remove accents and spaces)
        clean_base_sku = self.remove_vietnamese_accents(base_sku)
        
        variants = self.generate_variants(product)

        data = {
            # Sync rules
            "product[syncVariations][last_imported_price]": "true",
            "product[syncVariations][retail_price]": "true",
            "product[syncVariations][wholesale_price2]": "true",
            "product[syncVariations][weight]": "true",
            "product[syncVariations][total_quantity]": "false",
            "product[syncVariations][images]": "false",

            # Product info
            "product[name]": product_name,
            "product[custom_id]": base_sku,
            "product[type]": "product",
            "product[shop_id]": self.shop_id,
            "product[weight]": "1",
        }

        # ===== Attributes =====
        # Color - get from Product.color
        colors = getattr(product, 'color', [])
       
        data["product[product_attributes][0][name]"] = "màu"
        for i, color_name in enumerate(colors):
            data[f"product[product_attributes][0][values][{i}]"] = color_name
            data[f"product[product_attributes][0][keyword][{i}][keyValue]"] = color_name
            data[f"product[product_attributes][0][keyword][{i}][value]"] = color_name
        data["product[product_attributes][0][index]"] = "0"

        # Size - get from Product.attr_size
        sizes = getattr(product, 'attr_size', [])
        data["product[product_attributes][1][name]"] = "size"
        for i, size_name in enumerate(sizes):
            data[f"product[product_attributes][1][values][{i}]"] = size_name
            data[f"product[product_attributes][1][keyword][{i}][keyValue]"] = size_name
            data[f"product[product_attributes][1][keyword][{i}][value]"] = size_name
        data["product[product_attributes][1][index]"] = "1"

        # ===== Variations =====
        for v in variants:
            i = v["index"]

            # Create SKU without accents and spaces (e.g., "áo ed56" -> "AOED56")
            clean_sku = self.remove_vietnamese_accents(v["sku"]).replace(' ', '') 
            data[f"product[variations][{i}][custom_id]"] = clean_sku
            data[f"product[variations][{i}][retail_price]"] = str(v["price"])
            data[f"product[variations][{i}][last_imported_price]"] = "0"
            data[f"product[variations][{i}][weight]"] = "0"
            data[f"product[variations][{i}][total_quantity]"] = "0"
            data[f"product[variations][{i}][not_create_transaction]"] = "false"

            # === IMAGES ===
            for img_index, image_id in enumerate(image_ids):
                # Get photo object from uploaded_images dict
                photo_obj = uploaded_images.get(image_id)
                if photo_obj and isinstance(photo_obj, dict):
                    # Get content_url from photo object
                    image_url = photo_obj.get("content_url") or photo_obj.get("url", "")
                else:
                    # Fallback: use image_id as direct URL or empty string
                    image_url = image_id if isinstance(image_id, str) and image_id.startswith('http') else ""

                data[f"product[variations][{i}][images][{img_index}]"] = image_url
                

            # === Color ===
            data[f"product[variations][{i}][fields][0][name]"] = "màu"
            data[f"product[variations][{i}][fields][0][value]"] = v["color_name"]
            data[f"product[variations][{i}][fields][0][keyValue]"] = v["color_name"]
            # === Size ===
            data[f"product[variations][{i}][fields][1][name]"] = "size"
            data[f"product[variations][{i}][fields][1][value]"] = v["size"]
            data[f"product[variations][{i}][fields][1][keyValue]"] = v["size"]

        return data

    def send_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send product data to POS API

        Args:
            product_data: Product data payload

        Returns:
            Dict containing response status and data
        """
        url = f"{self.base_url}/products"

        try:
            response = requests.post(
                url,
                params={"access_token": self.access_token},
                data=product_data,
                timeout=30
            )

            result = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response_text": response.text
            }

            if response.status_code in [200, 201]:
                log("Product sent successfully!", "SUCCESS")
            else:
                log(f"Failed to send product: HTTP {response.status_code}", "ERROR")

            return result

        except requests.exceptions.RequestException as e:
            log(f"Network error sending product: {e}", "ERROR")
            return {
                "status_code": 0,
                "success": False,
                "response_text": str(e),
                "error": str(e)
            }
        except Exception as e:
            log(f"Unexpected error sending product: {e}", "ERROR")
            return {
                "status_code": 0,
                "success": False,
                "response_text": str(e),
                "error": str(e)
            }

    def search_product_by_code(self, product_code: str) -> Dict[str, Any]:
       
        url = f"{self.base_url}/products"

        params = {
            "access_token": self.access_token,
            "include_combo_info": "true",
            "search": product_code
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # API returns 'data' array instead of 'products'
                products = data.get("data", [])
                total_entries = data.get("total_entries", 0)

                log(f"Search response: found {len(products)} products, total_entries: {total_entries} for code '{product_code}'", "INFO")

                # Always return the full response data with products array
                result = {
                    "success": True,
                    "total_entries": total_entries,
                    "products_found": len(products),
                    "products": products,
                    "searched_code": product_code
                }

                if products and len(products) > 0:
                    product_info = products[0]
                    log(f"Found product: {product_info.get('name', 'Unknown')} (ID: {product_info.get('id', 'N/A')})", "SUCCESS")
                    result["first_product"] = product_info
                else:
                    log(f"No product found with code: {product_code} (total in shop: {total_entries})", "WARNING")

                return result
            else:
                log(f"Search failed: HTTP {response.status_code}", "ERROR")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "total_entries": 0,
                    "products_found": 0,
                    "products": [],
                    "searched_code": product_code
                }

        except requests.exceptions.RequestException as e:
            log(f"Network error searching product: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "total_entries": 0,
                "products_found": 0,
                "products": [],
                "searched_code": product_code
            }
        except json.JSONDecodeError as e:
            log(f"Invalid JSON response: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Invalid JSON: {str(e)}",
                "total_entries": 0,
                "products_found": 0,
                "products": [],
                "searched_code": product_code
            }
        except Exception as e:
            log(f"Unexpected error searching product: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "total_entries": 0,
                "products_found": 0,
                "products": [],
                "searched_code": product_code
            }


    def test_search_product(self, product_code: str = "ED56") -> None:
        """Test method to search product by code"""
        log(f"Testing PosAPI product search for code: {product_code}", "INFO")

        # Search for product
        search_result = self.search_product_by_code(product_code)

        if search_result and search_result.get("products_found", 0) > 0:
            first_product = search_result.get("first_product", {})
            print(f"Found product: {first_product.get('name', 'Unknown')}")
            print(f"Product ID: {first_product.get('id', 'N/A')}")
            print(f"Custom ID: {first_product.get('custom_id', 'N/A')}")
            print(f"Retail Price: {first_product.get('retail_price', 'N/A')}")
            print(f"Total products in shop: {search_result.get('total_entries', 0)}")
            print(f"Products data saved: {len(search_result.get('products', []))} items")
        else:
            total_in_shop = search_result.get("total_entries", 0) if search_result else 0
            print(f"No product found with code: {product_code} (total in shop: {total_in_shop})")
def main():
    """Main function for testing"""
    api = PosAPI()

    # Test product search
    api.test_search_product("ED56")


if __name__ == "__main__":
    main()
