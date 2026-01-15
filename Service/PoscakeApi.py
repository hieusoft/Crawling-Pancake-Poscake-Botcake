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
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiTmd1eWVuIE5hbSIsImV4cCI6MTc3NjE3ODA2MywiYXBwbGljYXRpb24iOjEsInVpZCI6IjAyNTQ5OWE4LTg4MDgtNDY3Yy1iYjgwLTMyZTcxN2RiZjM0YSIsInNlc3Npb25faWQiOiI0YmQ3ZThmMC1iMmIwLTQ2MjUtODA0Ni1iYWI2ZDZkZDEwOTEiLCJpYXQiOjE3Njg0MDIwNjMsImZiX2lkIjoiMzkzMDY2MTY1NTQzNjc1IiwibG9naW5fc2Vzc2lvbiI6bnVsbCwiZmJfbmFtZSI6Ik5ndXllbiBOYW0ifQ.NdbiqANtdk4AwfibWuuy0ciJw0Tqo8E3wO7xQJMzVh0"
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
                    "color_index": c_idx,  # Add color index
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
            # Only assign image that matches the color index
            color_index = v.get("color_index", 0)
            if color_index < len(image_ids):
                image_id = image_ids[color_index]
                # Get photo object from uploaded_images dict
                photo_obj = uploaded_images.get(image_id)
                if photo_obj and isinstance(photo_obj, dict):
                    # Get content_url from photo object
                    image_url = photo_obj.get("content_url") or photo_obj.get("url", "")
                else:
                    # Fallback: use image_id as direct URL or empty string
                    image_url = image_id if isinstance(image_id, str) and image_id.startswith('http') else ""

                # Assign image at index 0 (single image per variation based on color)
                data[f"product[variations][{i}][images][0]"] = image_url
                

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
            print(response.url)
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

    def create_combo_product(self, combo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a combo product on POS

        Args:
            combo_data: Dictionary containing combo product data

        Returns:
            Dict with creation result
        """
        url = f"{self.base_url}/combo_products"
        params = {"access_token": self.access_token}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Origin": "https://pos.pancake.vn",
            "Referer": f"https://pos.pancake.vn/shop/{self.shop_id}/product/combo"
        }

        try:
            log(f"Creating combo product: {combo_data.get('combo_product', {}).get('name', 'Unknown')}", "INFO")

            response = requests.post(
                url,
                params=params,
                json=combo_data,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    log(f"Combo product created successfully: {result.get('name', 'Unknown')}", "SUCCESS")
                    return {
                        "success": True,
                        "data": result,
                        "status_code": response.status_code
                    }
                except json.JSONDecodeError:
                    log("Combo product created (response not JSON)", "SUCCESS")
                    return {
                        "success": True,
                        "data": {"message": "Combo created successfully"},
                        "status_code": response.status_code
                    }
            else:
                print(response.text)
                log(f"Failed to create combo product: HTTP {response.status_code}", "ERROR")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }

        except requests.exceptions.RequestException as e:
            log(f"Network error creating combo product: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            log(f"Unexpected error creating combo product: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
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

    def test_create_combo_product(self) -> None:
        """Test method to create a combo product"""
        log("Testing PosAPI combo product creation", "INFO")

        # First, search for a product to get its ID
        product_code = "ED56"  # Change this to the product code you want to use in combo
        log(f"Searching for product with code: {product_code}", "INFO")

        search_result = self.search_product_by_code(product_code)

        if not search_result.get("products_found", 0) > 0:
            log(f"No product found with code {product_code}, cannot create combo", "ERROR")
            return

        # Get the first product's ID from search results
        product_id = search_result.get("first_product", {}).get("id")
        if not product_id:
            log("Could not get product ID from search results", "ERROR")
            return

        log(f"Found product ID: {product_id}", "SUCCESS")

        # Create combo data using the found product ID
        combo_data = {
            "combo_product": {
                "name": "COMBO 2 ÁO ED56",
                "value_combo": 699000,
                "is_value_combo": True,
                "variations": [
                    {
                        "count": 2,
                        "product_id": product_id,  # Use the found product ID
                        "variation_id": None
                    }
                ]
            }
        }

        # Create combo product
        result = self.create_combo_product(combo_data)
        if result.get("success"):
            print("Combo product created successfully!")
            print(f"Response: {result.get('data')}")
        else:
            print(f"Failed to create combo product: {result.get('error')}")
def main():
    """Main function for testing"""
    api = PosAPI()

    print("=== Testing Product Search ===")
    api.test_search_product("ED56")

    print("\n=== Testing Combo Product Creation ===")
    api.test_create_combo_product()


if __name__ == "__main__":
    main()
