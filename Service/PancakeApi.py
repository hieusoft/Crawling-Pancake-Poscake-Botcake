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

class PancakeAPI:
    """Pancake.vn API client for managing page settings and content"""

    def __init__(self, page_id: str, access_token: Optional[str] = None):
        """
        Initialize Pancake API client

        Args:
            page_id: Facebook page ID
            access_token: Pancake access token (optional, uses default if not provided)
        """
        self.page_id = page_id
        self.access_token = access_token or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGlldSIsImV4cCI6MTc3NDc1NzA1NywiYXBwbGljYXRpb24iOjEsInVpZCI6ImFjNmU3MjQ0LWYyZTQtNGUxNy04YTk5LTgzNDA3NjhiOWZmMSIsInNlc3Npb25faWQiOiJmZDU3NzIzMy0yYzJjLTRiMzAtODBjOS03ODQ0NGRmNWRmZDUiLCJpYXQiOjE3NjY5ODEwNTcsImZiX2lkIjoiMjM4NDQwNzc5NTE3Njc4MCIsImxvZ2luX3Nlc3Npb24iOm51bGwsImZiX25hbWUiOiJoaWV1In0.sE7-XOHDgrPSGf_oisgH8Ezr90-1Rzyhpb_3btFdqKs"

        # API URLs
        self.base_url = f"https://pancake.vn/api/v1/pages/{self.page_id}/settings"
        self.pages_url = "https://pancake.vn/api/v1/pages"
        self.contents_url = f"https://pancake.vn/api/v1/pages/{self.page_id}/contents"

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
        
    def get_current_settings(self) -> Optional[Dict[str, Any]]:
        """
        Lấy current settings từ Pancake (quick replies và current_settings_key)

        Returns:
            Dict: Chứa 'quick_replies' và 'current_settings_key' hoặc None nếu có lỗi
        """
        log("Fetching current settings from Pancake", "INFO")

        url = f"{self.base_url}?access_token={self.access_token}&separate_pos=true"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code != 200:
                return None

            data = response.json()
            settings = data.get("settings", {})
            quick_replies = settings.get("quick_replies", [])
            current_settings_key = settings.get("current_settings_key")

            return {
                "quick_replies": quick_replies,
                "current_settings_key": current_settings_key
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
    def update_settings(self, quick_replies: List[Dict[str, Any]], current_settings_key: str) -> bool:
        """
        Cập nhật settings lên Pancake

        Args:
            quick_replies: Danh sách quick replies mới
            current_settings_key: Settings key hiện tại

        Returns:
            bool: True nếu update thành công, False nếu thất bại
        """
        log("Sending POST request to update settings", "INFO")

        if not current_settings_key:
            log("current_settings_key is required", "ERROR")
            return False

        url = f"https://pancake.vn/api/v1/pages/{self.page_id}/settings"

        payload = {
            "quick_replies": quick_replies
        }

        files = {
            "changes": (None, json.dumps(payload, ensure_ascii=False)),
            "current_settings_key": (None, current_settings_key)
        }

        try:
            response = requests.post(
                url,
                params=self.params,
                headers=self.headers,
                files=files,
                timeout=30
            )

            try:
                response_json = response.json()
                success = response_json.get('success', False)

                if response.status_code == 200 and success:
                    log("Settings updated successfully!", "SUCCESS")
                    return True
                else:
                    log("Update failed", "WARNING")
                    error_msg = response_json.get("message", "Unknown error")
                    log(f"Error: {error_msg}", "WARNING")

                    # Debug response for troubleshooting
                    if "data" in response_json:
                        log(f"Response contains data field", "DEBUG")
                    return False

            except json.JSONDecodeError:
                log("Response is not valid JSON", "ERROR")
                log(f"Raw response: {response.text[:500]}...", "DEBUG")
                return False

        except requests.exceptions.Timeout:
            log("Request timed out", "ERROR")
            return False
        except requests.exceptions.RequestException as e:
            log(f"Network error during update: {e}", "ERROR")
            return False
        except Exception as e:
            log(f"Unexpected error in update_settings: {e}", "ERROR")
            return False
    def download_image(self, url: str, filename: str) -> Optional[str]:
        """
        Tải ảnh từ URL về local

        Args:
            url: URL của ảnh
            filename: Tên file lưu local

        Returns:
            str: Đường dẫn file local hoặc None nếu thất bại
        """
        try:
            filepath = os.path.join(self.images_dir, filename)

            # Download with timeout
            urllib.request.urlretrieve(url, filepath)

            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                log(f"Downloaded image: {filename} ({file_size} bytes)", "DEBUG")
                return filepath
            else:
                log(f"Download completed but file not found: {filepath}", "WARNING")
                return None

        except urllib.error.URLError as e:
            log(f"URL error downloading {url}: {e}", "ERROR")
            return None
        except Exception as e:
            log(f"Failed to download image {url}: {e}", "ERROR")
            return None

    def upload_to_pancake(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload ảnh lên Pancake và trả về photo object

        Args:
            file_path: Đường dẫn file ảnh local

        Returns:
            Dict: Photo object từ Pancake hoặc None nếu thất bại
        """
        if not os.path.exists(file_path):
            log(f"File does not exist: {file_path}", "ERROR")
            return None

        try:
            # Xác định MIME type
            mime_type = get_mime_type(file_path)
            filename = os.path.basename(file_path)

            # Upload với file
            with open(file_path, "rb") as f:
                files = {
                    "file": (filename, f, mime_type),
                    "action": (None, "upload"),
                    "needsCompress": (None, "false"),
                }

                response = requests.post(
                    self.contents_url,
                    headers=self.headers,
                    params=self.params,
                    files=files,
                    timeout=60  # Longer timeout for uploads
                )

            if response.status_code == 200:
                upload_data = response.json()
            
                if upload_data.get("success"):
                    # Tạo photo object dựa trên response từ Pancake
                    photo_obj = {
                        "id": upload_data.get("content_id", ""),
                        "image_data": upload_data.get("image_data", {"height": 0, "width": 0}),
                        "name": upload_data.get("name", filename),
                        "preview_url": upload_data.get("content_preview_url", ""),
                        "url": upload_data.get("content_url", "")
                    }
                    return photo_obj
                else:
                    log(f"Upload failed: {upload_data.get('message', 'Unknown error')}", "ERROR")
                    return None
            else:
                log(f"Upload HTTP error: {response.status_code}", "ERROR")
                return None

        except requests.exceptions.RequestException as e:
            log(f"Network error during upload: {e}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            log(f"Invalid JSON response during upload: {e}", "ERROR")
            return None
        except Exception as e:
            log(f"Unexpected error uploading {file_path}: {e}", "ERROR")
            return None

    def download_and_upload_image(self, url: str, filename: str) -> Dict[str, Any]:
        """
        Tải ảnh về local và upload lên Pancake

        Args:
            url: URL của ảnh gốc
            filename: Tên file

        Returns:
            Dict: Photo object (luôn trả về object, dù upload thành công hay không)
        """
        log(f"Processing image: {filename} from {url}", "DEBUG")

        # Tải về local
        local_path = self.download_image(url, filename)

        if local_path:
            # Upload lên Pancake
            photo_obj = self.upload_to_pancake(local_path)
            if photo_obj:
                return photo_obj
            else:
                log("Upload failed, falling back to original URL", "WARNING")

        # Fallback: trả về photo object với URL gốc
        fallback_obj = {
            "id": "",
            "image_data": {"height": 0, "width": 0},
            "name": filename,
            "preview_url": url,
            "url": url
        }
        log(f"Using fallback photo object for {filename}", "DEBUG")
        return fallback_obj

    def get_pages_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách tất cả pages

        Returns:
            List[Dict]: Danh sách pages hoặc None nếu có lỗi
        """
        log("Fetching pages list", "INFO")

        try:
            response = requests.get(self.pages_url, params=self.params, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                pages = data.get('categorized', {}).get('activated', [])
                log(f"Found {len(pages)} activated pages", "SUCCESS")
                return pages
            else:
                log(f"Failed to get pages: HTTP {response.status_code}", "ERROR")
                return None

        except Exception as e:
            log(f"Error getting pages list: {e}", "ERROR")
            return None

    def validate_token(self) -> bool:
        """
        Kiểm tra tính hợp lệ của access token

        Returns:
            bool: True nếu token hợp lệ, False nếu không
        """
        try:
            response = requests.get(self.pages_url, params=self.params, headers=self.headers, timeout=30)
            return response.status_code == 200
        except:
            return False


