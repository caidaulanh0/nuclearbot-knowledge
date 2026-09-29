#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to download files or folders from Google Drive using gdown.
Supports both public folder URL, folder ID, or file URL.
"""

import sys
import os
import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description="Tự động tải dữ liệu từ Google Drive")
    parser.add_argument("--url", type=str, required=True, help="Link chia sẻ Google Drive (hoặc Folder ID)")
    parser.add_argument("--output", type=str, default="data_drive", help="Thư mục lưu dữ liệu tải về")
    return parser.parse_args()

def main():
    args = parse_args()
    url = args.url.strip()
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    print(f"=== BẮT ĐẦU TẢI DỮ LIỆU TỪ GOOGLE DRIVE ===")
    print(f"URL/ID : {url}")
    print(f"Đích đến: {output_dir}")

    # Chạy gdown
    # Nếu là link folder chứa 'folders/' hoặc query folder
    cmd = [
        sys.executable, "-m", "gdown",
        "--folder",
        url,
        "-O", output_dir,
        "--remaining-ok"
    ]

    print(f"Lệnh thực thi: {' '.join(cmd)}")
    try:
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            print("[Cảnh báo] Tải dạng folder gặp lỗi, thử chuyển sang tải dạng file đơn...")
            cmd_single = [sys.executable, "-m", "gdown", url, "-O", output_dir]
            subprocess.run(cmd_single, check=True)
    except Exception as e:
        print(f"[Lỗi] Quá trình tải thất bại: {e}")
        sys.exit(1)

    # Đếm số lượng file tải về
    downloaded_files = []
    for root, _, files in os.walk(output_dir):
        for f in files:
            downloaded_files.append(os.path.join(root, f))

    print(f"=== TẢI XONG: Đã tải {len(downloaded_files)} file về {output_dir} ===")

if __name__ == "__main__":
    main()
