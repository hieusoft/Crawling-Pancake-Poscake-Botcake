import requests
import json
import urllib.request
import mimetypes
import sys
import os
from typing import Optional, Dict, List, Any

# Simple logger function
def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

class BotcakeAPI:
    """Pancake.vn API client for managing page settings and content"""

    def __init__(self, page_id: str, access_token: Optional[str] = None):
        """
        Initialize Pancake API client

        Args:
            page_id: Facebook page ID
            access_token: Pancake access token (optional, uses default if not provided)
        """
        self.page_id = page_id
        self.access_token = access_token or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImthYXJuZWNpbGxlYkBob3RtYWlsLmNvbSIsImV4cCI6MTc3NjE4MjE0MywiZmJfaWQiOiI0MDcyMDc2NTA3OTYxOTMiLCJmYl9uYW1lIjoiTmd1eWVuIE5hbSIsImlhdCI6MTc2ODQwNjE0MywiaWQiOiIwYTE3OGU1Yy00YjgwLTQ3YWMtYjU5My1hZDRlM2U0NzRlNWYiLCJwYW5jYWtlX2lkIjoiM2Q0YjRhZjgtNGU4YS00M2E2LTk3ZmEtYWIwZTM1OWJmYzMwIn0.FsMM0XjrYj27X4KuCN_W8wlgzwbvFJT9RA-u3SsbpXo"

       
        self.base_url = f"https://botcake.io/api/v1/pages/{self.page_id}/settings"
        self.pages_url = "https://botcake.io/api/v1/pages"
        self.contents_url = f"https://botcake.io/api/v1/pages/{self.page_id}/contents"
        self.assistants_url = f"https://botcake.io/api/v1/pages/{self.page_id}/assistants"
        self.get_warehouses_url = f"https://botcake.io/api/v1/pages/{self.page_id}/prducts/get_warehouses"
        self.get_products_url = f"https://botcake.io/api/v1/pages/{self.page_id}/products/get_products"
        # Local directories
        self.images_dir = "images"
        os.makedirs(self.images_dir, exist_ok=True)

        # HTTP headers and params
        self.headers = {
            "Accept": "application/json",
            "Origin": "https://pancake.vn",
            "Referer": f"https://pancake.vn/{self.page_id}/setting/reply",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        self.params = {"access_token": self.access_token}

        log(f"PancakeAPI initialized for page: {page_id}", "INFO")
        
    def get_warehouse(self) -> Optional[Dict[str, Any]]:
        """
        Lấy current settings từ Pancake (quick replies và current_settings_key)

        Returns:
            Dict: Chứa 'quick_replies' và 'current_settings_key' hoặc None nếu có lỗi
        """
        log("Fetching current settings from Pancake", "INFO")

        url = f"{self.get_warehouses_url}?access_token={self.access_token}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code != 200:
                return None

            data = response.json()
            categories = data.get("settings", {})
            warehouses = categories.get("quick_replies", [])
           
            print(data)

            return {
                "pos_warehouse_id": warehouses.pos_warehouse_id,
                "current_settings_key": data
            }

        except requests.exceptions.RequestException as e:
            log(f"Network error while fetching settings: {e}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            log(f"Invalid JSON response: {e}", "ERROR")
            return None
        except Exception as e:
            log(f"Unexpected error in get_current_settings: {e}", "ERROR")
            return None
    def search_product_by_code(self, product_code: str) -> Dict[str, Any]:
       