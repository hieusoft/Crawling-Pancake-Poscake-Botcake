import gdown
import requests
import re
import os
import sys
from typing import Optional, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    print(f"[{level}] {message}")


class GoogleDriveImageDownloader:

    def __init__(self):
        self.output_dir = "Downloads"
        os.makedirs(self.output_dir, exist_ok=True)

    def download_image(self, file_id: str) -> Optional[str]:
        """
        Tải ảnh từ Google Drive bằng file ID
        File sẽ được lưu trong thư mục "download" với tên là file_id

        Args:
            file_id: Google Drive file ID hoặc direct URL

        Returns:
            str: Đường dẫn file local hoặc None nếu thất bại
        """
        try:
            # Check if it's already a direct URL
            if file_id.startswith('http'):
                download_url = file_id
                # Extract filename from URL
                filename = file_id.split('/')[-1].split('?')[0]
                if not filename:
                    filename = f"downloaded_image_{hash(file_id) % 10000}.jpg"
            else:
                # Create download URL from file ID
                download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
                filename = f"{file_id}.jpg"

            output_path = os.path.join(self.output_dir, filename)

            # Try multiple download methods
            downloaded_path = None

            # Method 1: Use gdown with fuzzy matching
            try:
                downloaded_path = gdown.download(
                    url=download_url,
                    output=output_path,
                    quiet=True,
                    fuzzy=True
                )
            except Exception as e:
                pass  # Silent fail for gdown method

            # Method 2: Direct requests download (fallback)
            if not downloaded_path:
                try:
                    response = requests.get(download_url, stream=True, timeout=30)

                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        downloaded_path = output_path

                except Exception as e:
                    log(f"Direct requests method failed: {e}", "DEBUG")

            # Method 3: Try alternative Google Drive URL formats
            if not downloaded_path:
                alternative_urls = [
                    f"https://drive.google.com/uc?export=download&id={file_id}",
                    f"https://docs.google.com/uc?export=download&id={file_id}",
                    f"https://drive.google.com/file/d/{file_id}/view?usp=sharing",  # This won't work for download
                ]

                for alt_url in alternative_urls:
                    try:
                        downloaded_path = gdown.download(
                            url=alt_url,
                            output=output_path,
                            quiet=True,
                            fuzzy=True
                        )
                        if downloaded_path:
                            break
                    except Exception as e:
                        continue

            # Check result
            if downloaded_path and os.path.exists(downloaded_path):
                return downloaded_path
            else:
                log(f"All download methods failed for: {file_id}", "ERROR")
                log("NOTE: Make sure Google Drive files are set to 'Anyone with the link can view'", "WARNING")
                log("Check: https://github.com/wkentaro/gdown?tab=readme-ov-file#faq", "WARNING")
                return None

        except Exception as e:
            log(f"Error downloading image {file_id}: {e}", "ERROR")
            return None

    def download_from_direct_url(self, direct_url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download từ direct Google Drive URL (share link)

        Args:
            direct_url: Direct Google Drive share URL
            filename: Tên file lưu local

        Returns:
            str: Đường dẫn file local hoặc None nếu thất bại
        """
        try:
            log(f"Downloading from direct URL: {direct_url}", "INFO")

            # Extract file ID from share URL
            file_id = self._extract_file_id_from_url(direct_url)
            if not file_id:
                log("Could not extract file ID from direct URL", "ERROR")
                return None

            # Use the improved download method
            return self.download_image(file_id)

        except Exception as e:
            log(f"Error downloading from direct URL: {e}", "ERROR")
            return None

    def create_download_script_for_folder(self, folder_url: str) -> str:
        """
        Tạo script để download tất cả images từ folder

        Args:
            folder_url: Google Drive folder URL

        Returns:
            str: Python script content
        """
        script = f'''#!/usr/bin/env python3
"""
Download all images from Google Drive folder
Folder: {folder_url}

This script tries multiple download methods for files that may have permission issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.DriverImages import GoogleDriveImageDownloader

def main():
    print("=== DOWNLOADING IMAGES FROM GOOGLE DRIVE FOLDER ===")
    print(f"Folder: {folder_url}")

    downloader = GoogleDriveImageDownloader()

    # List of known image filenames from your folder
    # Update these with the actual filenames from your Google Drive folder
    image_filenames = [
        "z7397359279360_bdb8ca99f53e7707d5b5fd086f9a24f1.jpg",
        "z7397359835229_42ec8892f74c232d254e6850a3f9bffc.jpg",
        "z7397360974735_fe73f954867b7f95fca687f3c0129c2c.jpg"
    ]

    print(f"Attempting to download {{len(image_filenames)}} images...")

    successful = 0

    for filename in image_filenames:
        print(f"\\n--- Downloading: {{filename}} ---")

        # Method 1: Try direct folder URL + filename
        folder_download_url = f"{folder_url}/{{filename}}"
        print(f"Trying: {{folder_download_url}}")
        result1 = downloader.download_from_direct_url(folder_download_url, filename)

        if result1:
            print(f"✓ Success with folder URL: {{result1}}")
            successful += 1
            continue

        # Method 2: If you have direct share URLs, add them here
        # Example direct URLs (replace with actual share URLs):
        direct_urls = [
            # "https://drive.google.com/file/d/FILE_ID1/view?usp=sharing",
            # "https://drive.google.com/file/d/FILE_ID2/view?usp=sharing",
        ]

        for direct_url in direct_urls:
            print(f"Trying direct URL: {{direct_url}}")
            result2 = downloader.download_from_direct_url(direct_url, filename)
            if result2:
                print(f"✓ Success with direct URL: {{result2}}")
                successful += 1
                break
        else:
            print(f"✗ All methods failed for: {{filename}}")

    print(f"\\n{'='*50}")
    print(f"SUMMARY: {{successful}}/{{len(image_filenames)}} images downloaded successfully")

    if successful == 0:
        print("\\nTROUBLESHOOTING:")
        print("1. Ensure Google Drive files are set to 'Anyone with the link can view'")
        print("2. Try using direct share URLs instead of file IDs")
        print("3. Check network connection and file permissions")

if __name__ == "__main__":
    main()
'''

        return script


def demo_usage():
    """Demo class usage"""
    print("=== GOOGLE DRIVE IMAGE DOWNLOADER DEMO ===")

    # Initialize
    downloader = GoogleDriveImageDownloader()

    print("Usage:")
    print('downloader = GoogleDriveImageDownloader()')
    print('filepath = downloader.download_image("1VR558T2QptoXlrsghuIRzNwn3-NRUsnR")')
    print()
    print("File will be saved as: download/1VR558T2QptoXlrsghuIRzNwn3-NRUsnR.jpg")


def test_real_download():
    """Test with real file ID"""
    print("=== TESTING REAL DOWNLOAD ===")

    downloader = GoogleDriveImageDownloader()
    test_file_id = "1VR558T2QptoXlrsghuIRzNwn3-NRUsnR"

    print(f"Testing download of file ID: {test_file_id}")

    try:
        result = downloader.download_image(test_file_id)
        if result:
            print(f"[SUCCESS] Downloaded to: {result}")
            print(f"File exists: {os.path.exists(result)}")
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"File size: {size} bytes")
        else:
            print("[FAILED] Download failed")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

    print("=== REAL DOWNLOAD TEST COMPLETED ===")


if __name__ == "__main__":
 
    demo_usage()

    print("\n" + "="*50)

    
    test_real_download()

