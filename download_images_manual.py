#!/usr/bin/env python3
"""
Download all images from Google Drive folder
Folder: https://drive.google.com/drive/u/0/folders/1I3RvB7t6rAktkhTVw8oKsKORJuKkoUr0

This script tries multiple download methods for files that may have permission issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.DriverImages import GoogleDriveImageDownloader

def main():
    print("=== DOWNLOADING IMAGES FROM GOOGLE DRIVE FOLDER ===")
    print(f"Folder: https://drive.google.com/drive/u/0/folders/1I3RvB7t6rAktkhTVw8oKsKORJuKkoUr0")

    downloader = GoogleDriveImageDownloader()

    # List of known image filenames from your folder
    # Update these with the actual filenames from your Google Drive folder
    image_filenames = [
        "z7397359279360_bdb8ca99f53e7707d5b5fd086f9a24f1.jpg",
        "z7397359835229_42ec8892f74c232d254e6850a3f9bffc.jpg",
        "z7397360974735_fe73f954867b7f95fca687f3c0129c2c.jpg"
    ]

    print(f"Attempting to download {len(image_filenames)} images...")

    successful = 0

    for filename in image_filenames:
        print(f"\n--- Downloading: {filename} ---")

        # Method 1: Try direct folder URL + filename
        folder_download_url = f"https://drive.google.com/drive/u/0/folders/1I3RvB7t6rAktkhTVw8oKsKORJuKkoUr0/{filename}"
        print(f"Trying: {folder_download_url}")
        result1 = downloader.download_from_direct_url(folder_download_url, filename)

        if result1:
            print(f"✓ Success with folder URL: {result1}")
            successful += 1
            continue

        # Method 2: If you have direct share URLs, add them here
        # Example direct URLs (replace with actual share URLs):
        direct_urls = [
            # "https://drive.google.com/file/d/FILE_ID1/view?usp=sharing",
            # "https://drive.google.com/file/d/FILE_ID2/view?usp=sharing",
        ]

        for direct_url in direct_urls:
            print(f"Trying direct URL: {direct_url}")
            result2 = downloader.download_from_direct_url(direct_url, filename)
            if result2:
                print(f"✓ Success with direct URL: {result2}")
                successful += 1
                break
        else:
            print(f"✗ All methods failed for: {filename}")

    print(f"\n==================================================")
    print(f"SUMMARY: {successful}/{len(image_filenames)} images downloaded successfully")

    if successful == 0:
        print("\nTROUBLESHOOTING:")
        print("1. Ensure Google Drive files are set to 'Anyone with the link can view'")
        print("2. Try using direct share URLs instead of file IDs")
        print("3. Check network connection and file permissions")

if __name__ == "__main__":
    main()
