#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NuclearBot Pipeline:
1. Kiểm tra tính toàn vẹn Core KB & Ontology
2. Xử lý tri thức Markdown chuyên đề
3. Bóc tách tài liệu PDF (sử dụng Multiprocessing tốc độ cao)
4. Xuất kết quả tổng hợp (JSONL, Markdown report)
"""

import os
import sys
import json
import glob
import time
import sqlite3
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def parse_args():
    parser = argparse.ArgumentParser(description="Chạy Pipeline tính toán & bóc tách tri thức NuclearBot")
    parser.add_argument("--pdf-dir", type=str, default="downloaded_pdfs", help="Thư mục chứa các file PDF")
    parser.add_argument("--max-pdfs", type=int, default=100, help="Số lượng file PDF tối đa cần xử lý (0 = tất cả)")
    parser.add_argument("--output-dir", type=str, default="output", help="Thư mục xuất kết quả")
    return parser.parse_args()

def check_databases(repo_root):
    """Kiểm tra SQLite DB"""
    db_paths = [
        os.path.join(repo_root, "automation_bridge", "core_kb.db"),
        os.path.join(repo_root, "automation_bridge", "ontology.db")
    ]
    report = []
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [r[0] for r in cursor.fetchall()]
                table_counts = {}
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM `{t}`;")
                    table_counts[t] = cursor.fetchone()[0]
                conn.close()
                report.append({
                    "db": os.path.basename(db_path),
                    "status": "OK",
                    "tables": table_counts
                })
            except Exception as e:
                report.append({"db": os.path.basename(db_path), "status": f"Error: {e}"})
        else:
            report.append({"db": os.path.basename(db_path), "status": "Not found"})
    return report

def process_single_pdf(pdf_path):
    """Bóc tách text từ 1 file PDF"""
    if fitz is None:
        return {"file": os.path.basename(pdf_path), "error": "PyMuPDF not installed"}
    
    start_time = time.time()
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        text_content = []
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text.strip():
                text_content.append({"page": page_num + 1, "text": text.strip()})
        doc.close()
        
        elapsed = round(time.time() - start_time, 2)
        return {
            "file": os.path.basename(pdf_path),
            "pages": total_pages,
            "extracted_pages": len(text_content),
            "time_seconds": elapsed,
            "status": "success",
            "content": text_content
        }
    except Exception as e:
        return {
            "file": os.path.basename(pdf_path),
            "error": str(e),
            "status": "failed"
        }

def scan_markdown_kb(repo_root):
    """Đếm và thống kê tài liệu markdown chuyên đề"""
    kb_dir = os.path.join(repo_root, "KHO_DU_LIEU_AI")
    md_files = glob.glob(os.path.join(kb_dir, "**", "*.md"), recursive=True)
    return len(md_files), [os.path.relpath(f, repo_root) for f in md_files[:10]]

def main():
    args = parse_args()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("==================================================")
    print("🚀 NUCLEARBOT KNOWLEDGE PROCESSING PIPELINE")
    print(f"Repository Root: {repo_root}")
    print(f"Output Directory: {out_dir}")
    print("==================================================")

    # 1. Kiểm tra CSDL
    print("\n[1/3] Đang kiểm tra Core Database...")
    db_report = check_databases(repo_root)
    for r in db_report:
        print(f" - {r['db']}: {r.get('status')} | Bảng: {r.get('tables', {})}")

    # 2. Quét kho Markdown chuyên đề
    print("\n[2/3] Đang kiểm tra Kho Tri Thức Markdown...")
    total_md, sample_md = scan_markdown_kb(repo_root)
    print(f" - Tổng số file Markdown chuyên đề: {total_md}")

    # 3. Quét và bóc tách PDF (nếu có)
    print("\n[3/3] Quét & Bóc tách PDF tài liệu...")
    pdf_dir = os.path.abspath(args.pdf_dir)
    pdf_files = []
    if os.path.exists(pdf_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
    
    # Kiểm tra thêm trong repo nếu có
    local_pdf_dir = os.path.join(repo_root, "KHO_DU_LIEU_AI")
    if not pdf_files and os.path.exists(local_pdf_dir):
        pdf_files = glob.glob(os.path.join(local_pdf_dir, "**", "*.pdf"), recursive=True)

    if args.max_pdfs > 0:
        pdf_files = pdf_files[:args.max_pdfs]

    print(f" - Tìm thấy {len(pdf_files)} file PDF để xử lý.")

    extracted_results = []
    if pdf_files:
        so_nhan = os.cpu_count() or 4
        print(f" - Bật đa tiến trình trên {so_nhan} nhân CPU...")
        start_all = time.time()
        
        with ProcessPoolExecutor(max_workers=so_nhan) as executor:
            future_to_file = {executor.submit(process_single_pdf, f): f for f in pdf_files}
            for future in as_completed(future_to_file):
                res = future.result()
                extracted_results.append(res)
                if res.get("status") == "success":
                    print(f"   [OK] {res['file']} ({res['pages']} trang, {res['time_seconds']}s)")
                else:
                    print(f"   [FAIL] {res['file']}: {res.get('error')}")

        total_time = round(time.time() - start_all, 2)
        print(f" - Xử lý xong {len(extracted_results)} file trong {total_time}s")

    # Lưu kết quả
    jsonl_output = os.path.join(out_dir, "extracted_knowledge.jsonl")
    with open(jsonl_output, "w", encoding="utf-8") as f:
        for item in extracted_results:
            # Ghi gọn không chứa toàn bộ raw text nếu quá nặng, hoặc ghi metadata
            meta = {k: v for k, v in item.items() if k != "content"}
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

    summary_file = os.path.join(out_dir, "PIPELINE_SUMMARY.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# Báo Cáo Xử Lý Dữ Liệu NuclearBot\n\n")
        f.write(f"- Thời gian thực hiện: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- Tổng số Markdown chuyên đề: {total_md}\n")
        f.write(f"- Số file PDF đã bóc tách: {len(extracted_results)}\n")
        f.write(f"- Trạng thái CSDL: {json.dumps(db_report, ensure_ascii=False, indent=2)}\n")

    print(f"\n✅ ĐÃ HOÀN TẤT! Kết quả được ghi nhận tại: {out_dir}")

if __name__ == "__main__":
    main()
