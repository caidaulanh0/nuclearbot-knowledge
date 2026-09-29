import os
import json
import uuid
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Vui lòng cài đặt PyMuPDF: pip install pymupdf")
    exit(1)

import hashlib

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "physics_kb"
VECTOR_SIZE = 1024

def init_qdrant():
    """ Khởi tạo collection trong Qdrant qua REST API """
    print(f"[{datetime.now().isoformat()}] Initializing Qdrant collection '{COLLECTION_NAME}'...")
    
    # 1. Kiểm tra collection tồn tại
    check_url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}"
    try:
        req = urllib.request.Request(check_url, method="GET")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"Collection '{COLLECTION_NAME}' already exists.")
                return True
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Error checking collection: {e.read().decode('utf-8')}")
            return False
    except Exception as e:
        print(f"Cannot connect to Qdrant at {QDRANT_URL}: {e}")
        return False
        
    # 2. Tạo collection nếu chưa có (Dense vector 1024, Cosine)
    create_url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}"
    payload = {
        "vectors": {
            "size": VECTOR_SIZE,
            "distance": "Cosine"
        }
    }
    try:
        req = urllib.request.Request(create_url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"Collection '{COLLECTION_NAME}' created successfully.")
                return True
    except Exception as e:
        print(f"Failed to create collection: {e}")
        return False

def parse_and_chunk(pdf_path: str, chunk_size: int = 1500, overlap: int = 150) -> List[Dict[str, Any]]:
    """ 
    Đọc PDF và chia chunk.
    - Cố gắng chia theo đoạn văn (\n\n) để giữ mạch toán học/vật lý (giữ [MATH]).
    - Overlap khoảng 10-15% (mặc định 150 ký tự).
    """
    chunks = []
    try:
        doc = fitz.open(pdf_path)
        filename = os.path.basename(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Trích xuất text gốc (PyMuPDF đã bảo toàn khá tốt format)
            text = page.get_text("text")
            
            # Xóa các dòng nối gạch ngang (hyphenation)
            text = text.replace('-\n', '')
            
            paragraphs = text.split('\n\n')
            
            # Hard limit: Đề phòng trường hợp 1 paragraph quá dài làm sập context 8192 của bge-m3
            safe_paragraphs = []
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                # Cắt cứng mỗi đoạn tối đa 2000 ký tự
                while len(p) > 2000:
                    safe_paragraphs.append(p[:2000])
                    p = p[2000:]
                if p:
                    safe_paragraphs.append(p)
                    
            current_chunk = ""
            
            for p in safe_paragraphs:
                # Nếu ghép vào bị lố chunk size -> Cắt chunk lưu lại
                if len(current_chunk) + len(p) > chunk_size and len(current_chunk) > 0:
                    chunks.append({
                        "text": current_chunk,
                        "source_file": filename,
                        "page": page_num + 1,
                        "section": "body", # Ở mức độ phức tạp hơn có thể detect Header
                        "doc_type": "pdf",
                        "ingested_date": datetime.now().isoformat()
                    })
                    # Overlap: lấy đuôi của chunk hiện tại
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + p
                else:
                    current_chunk += ("\n\n" if current_chunk else "") + p
                    
            # Chunk cuối cùng của trang
            if current_chunk:
                chunks.append({
                    "text": current_chunk,
                    "source_file": filename,
                    "page": page_num + 1,
                    "section": "body",
                    "doc_type": "pdf",
                    "ingested_date": datetime.now().isoformat()
                })
                
        doc.close()
    except Exception as e:
        print(f"Error parsing {pdf_path}: {e}")
        
    return chunks

def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """ Gọi Ollama API lấy embeddings (Dense 1024-dim) """
    url = "http://localhost:11434/api/embed"
    payload = {
        "model": "bge-m3",
        "input": texts
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={"Content-Type": "application/json"}, 
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result.get("embeddings", [])

def upsert_to_qdrant(chunks: List[Dict[str, Any]]):
    """ Nhúng văn bản ra Dense vector qua Ollama và Upsert vào Qdrant """
    if not chunks:
        return
        
    texts = [c["text"] for c in chunks]
    
    # Ollama API encode -> Dense 1024-dim, chia batch 64 để giảm tải GPU
    batch_size_embed = 64
    embeddings = []
    for i in range(0, len(texts), batch_size_embed):
        batch_texts = texts[i:i+batch_size_embed]
        try:
            batch_embs = get_ollama_embeddings(batch_texts)
            embeddings.extend(batch_embs)
        except Exception as e:
            print(f"Failed to get embeddings from Ollama: {e}")
            return
    
    points = []
    for i, emb in enumerate(embeddings):
        payload = chunks[i].copy()
        
        # Idempotency: Tạo ID cố định từ hash MD5 (chống trùng lặp 100%)
        unique_string = f"{payload['source_file']}_{payload['page']}_{i}"
        hash_hex = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
        chunk_id = str(uuid.UUID(hex=hash_hex))
        
        points.append({
            "id": chunk_id,
            "vector": emb,  # emb là kiểu list do Ollama trả về
            "payload": payload
        })
        
    upsert_url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points"
    
    # Upsert theo batch (tránh body request quá lớn, max 100 points)
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch_points = points[i:i+batch_size]
        payload = {"points": batch_points}
        try:
            req = urllib.request.Request(
                upsert_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={"Content-Type": "application/json"}, 
                method="PUT"
            )
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    print(f"Error upserting batch: {response.read().decode('utf-8')}")
        except Exception as e:
            print(f"Failed to upsert points: {e}")

def main():
    data_dir = r"D:\dulieutraning\KHO_DU_LIEU_AI"
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return
        
    if not init_qdrant():
        print("Failed to initialize Qdrant. Exiting.")
        return
        
    print(f"[{datetime.now().isoformat()}] Validating Ollama connection...")
    try:
        urllib.request.urlopen("http://localhost:11434/")
    except Exception:
        print("Không thể kết nối đến Ollama tại http://localhost:11434. Vui lòng chạy Ollama trước.")
        return
    
    pdf_files = []
    for root, _, files in os.walk(data_dir):
        for f in files:
            if f.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, f))
                
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    for idx, pdf_path in enumerate(pdf_files):
        print(f"\n[{datetime.now().isoformat()}] Processing {idx+1}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
        chunks = parse_and_chunk(pdf_path)
        print(f"Extracted {len(chunks)} chunks.")
        upsert_to_qdrant(chunks)
        
    print("\nIngestion pipeline completed successfully.")

if __name__ == "__main__":
    main()
