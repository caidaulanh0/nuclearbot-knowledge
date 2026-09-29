# BIÊN BẢN ĐỒNG THUẬN KIẾN TRÚC: TRỢ LÝ AI VẬT LÝ HẠT NHÂN OFFLINE (V3)

Bản thiết kế này quy định cấu trúc lõi, luồng hoạt động và các nguyên tắc quản lý dự án nghiêm ngặt của hệ thống Trợ lý AI.

## 1. Mục tiêu Tối thượng
Xây dựng một **Automation Bridge** hoạt động 100% offline (trên GPU AMD RX 6700 XT), có khả năng: tự động chạy mã nguồn tính toán vật lý (Fortran/C++/Python) trong môi trường an toàn (sandbox) → đọc kết quả → nhờ AI chẩn đoán dựa trên tri thức RAG/KG → đề xuất tinh chỉnh tham số (chờ User duyệt) → chạy lại.

## 2. Kiến trúc & Kỹ thuật cốt lõi

### ĐIỂM 1: Hạ tầng RAG
- **Quyết định:** Giữ nguyên AnythingLLM làm lõi RAG.
- **Lý do:** Đã nhúng thành công 2.081 tài liệu chuyên ngành.
- **Cách triển khai:** Gọi API của AnythingLLM. Sẽ xác minh endpoint chat/retrieval độc lập để đảm bảo phù hợp với luồng ReAct.

### ĐIỂM 2: Tool/Action cho Automation Bridge & Lớp Verification
- **Quyết định:** Bổ sung các Action chuyên biệt và tích hợp Lớp Tự Kiểm Chứng (Verification/Reflexion).
- **9 Action chính trong vòng lặp ReAct:** (Xem chi tiết tại Mục 5)

### ĐIỂM 3: Xử lý Model & Lỗi Parse JSON
- **Quyết định:** Tạm thời sử dụng `nuclear-bot` (Llama 3.1 8B).
- Ép kiểu JSON nghiêm ngặt và fallback. Ghi nhận giải pháp nâng cấp lên `Qwen3 8B` nếu cần tool-calling tốt hơn.

### ĐIỂM 4: Xử lý Công thức Toán
- **Quyết định:** File mới ưu tiên dùng `Marker` OCR. Trích xuất thủ công công thức quan trọng vào SQLite Core KB.

## 3. Quy ước Quản lý Dự án (5 Nguyên Tắc Của Chủ Nhân)

### N1. Cấu trúc Tài liệu (3 File Trụ Cột)
Dự án được điều hướng bởi 3 file cốt lõi: ARCHITECTURE.md, TASKS.md, STATE.md.

### N2. Contract-First Development (Hợp đồng Giao diện)
Trước khi viết code cho 9 Actions, phải chốt Hợp đồng Giao diện (Contract) trong `ARCHITECTURE.md`.

### N3. Quản lý Phiên bản & Cách ly Thư mục An Toàn
- **Vị trí Repo Code:** `D:\dulieutraning\automation_bridge`. (Nằm NGOÀI khu vực `KHO_DU_LIEU_AI`).
- **3 Cấm kỵ An Toàn (Red Lines):**
  1. Không bao giờ nạp (embed) mã nguồn từ thư mục `automation_bridge` vào AnythingLLM để tránh nhiễu loạn/ảo giác dữ liệu RAG.
  2. Mọi lệnh quét/dọn dẹp trùng lặp (dedup hash) phải LOẠI TRỪ thư mục `automation_bridge`.
  3. Thư mục `D:\dulieutraning\AnythingLLM` là "vùng cấm", tuyệt đối không chạm vào hay quét mã băm.
- **Quy tắc Commit (Git):** Mỗi commit gắn với Task ID (VD: `T-002: implement query_kg`). Một phiên làm việc chỉ giải quyết 1 task.

### N4. Architecture Decision Records (ADR)
Mọi quyết định quan trọng sẽ được ghi thành file ADR.

### N5. Người dùng là Gác Cổng (Human-in-the-loop)
**Mệnh lệnh tuyệt đối:** Không được phép merge hoặc chạy code vật lý nào nếu chưa được Chủ nhân (User) đọc và phê duyệt.

---
## 5. Hợp Đồng Giao Diện (Action Contracts)

Toàn bộ các Action phải trả về chuẩn Error Contract chung như sau nếu thất bại:
`{ "ok": false, "error": { "code": "ERR_CODE", "message": "Mô tả lỗi" } }`

### 1. `query_rag`
- **Mục đích:** Tìm kiếm ngữ liệu từ AnythingLLM.
- **Input:** `{ "query": "string" }`
- **Output:** `{ "ok": true, "data": { "context": "string", "sources": ["string"] } }`
- **Side Effects:** Gọi API mạng nội bộ (AnythingLLM).

### 2. `query_kg`
- **Mục đích:** Truy vấn cơ sở tri thức tĩnh (Hằng số, Công thức).
- **Input:** `{ "query": "string" }`
- **Output:** `{ "ok": true, "data": { "results": [ { "id": "string", "value": "number", "unit": "string", "uncertainty": "string_or_number", "source": "string" } ] } }`
- **Side Effects:** Đọc SQLite DB.

### 3. `calculate`
- **Mục đích:** Tính toán biểu thức toán học.
- **Input:** `{ "expression": "string", "variables": { "var_name": "number" } }`
- **Output:** `{ "ok": true, "data": { "result": "number", "unit": "string" } }`
- **Side Effects:** Không. (Ghi chú: Nếu cần xử lý thứ nguyên/đơn vị phức tạp (kg, MeV), khuyến nghị dùng thư viện `pint` thay vì `sympy` thuần).

### 4. `run_simulation`
- **Mục đích:** Thực thi code mô phỏng vật lý trong Sandbox.
- **Input:** `{ "executable": "string", "args": ["string"], "input_file": "string", "working_dir": "string", "timeout_sec": "number" }`
- **Output:** `{ "ok": true, "data": { "sandbox_dir": "string", "stdout_log_path": "string", "stderr_log_path": "string", "exit_code": "number" } }`
- **Side Effects:** Chạy Subprocess, Ghi file log, Tạo thư mục Sandbox cô lập, Kill tiến trình nếu timeout.

### 5. `read_output`
- **Mục đích:** Đọc số liệu từ file kết quả (CSV/TXT).
- **Input:** `{ "file_path": "string", "format": "csv|txt", "extract_keys": ["string"] }`
- **Output:** `{ "ok": true, "data": { "extracted_values": { "key": "number_or_string" } } }`
- **Side Effects:** Đọc file hệ thống.

### 6. `compare_experiment`
- **Mục đích:** Đối chiếu kết quả lý thuyết (mô phỏng) và thực nghiệm.
- **Input:** `{ "simulation_data": { "key": "number" }, "experiment_data": { "key": "number" } }`
- **Output:** `{ "ok": true, "data": { "deviations": { "key": "number" }, "conclusion": "string" } }`
- **Side Effects:** Không. (Ghi chú: Áp dụng chung công thức deviation = |sim - exp| / |exp| * 100%).

### 7. `propose_parameter_change`
- **Mục đích:** Yêu cầu User phê duyệt việc đổi tham số đầu vào.
- **Input:** `{ "parameters": { "param_name": { "old_value": "number", "new_value": "number", "reason": "string" } } }`
- **Output:** `{ "ok": true, "data": { "status": "approved|rejected", "feedback": "string" } }`
- **Side Effects:** Block tiến trình, hiển thị luồng phê duyệt (Human-in-the-loop).

### 8. `verify_claims`
- **Mục đích:** Đối chiếu độ lệch số liệu (Relative Tolerance 1%).
- **Input:** `{ "claims": [ { "entity": "string", "property": "string", "value": "number" } ] }`
- **Output:** `{ "ok": true, "data": { "passed": "boolean", "conflicts": [ { "claim": "string", "kb_value": "number", "difference_pct": "number" } ] } }`
- **Side Effects:** Đọc SQLite DB.

### 9. `finish`
- **Mục đích:** Chấm dứt vòng lặp ReAct, sinh dự thảo câu trả lời để chuyển qua `verify_claims`.
- **Input:** `{ "final_answer": "string" }`
- **Output:** `{ "ok": true, "data": { "status": "done" } }`
- **Side Effects:** Kết thúc vòng lặp.
