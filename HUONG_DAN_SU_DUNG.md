# HƯỚNG DẪN ĐẨY LÊN GITHUB & CHẠY TÍNH TOÁN VỚI GOOGLE DRIVE

Dự án này đã được cấu hình sẵn sàng:
- **Toàn bộ Code, Cấu hình, Modelfiles và 50 bài viết Markdown tri thức chuyên sâu** được quản lý bằng Git (chỉ nặng ~3.7 MB, đẩy lên GitHub trong vài giây).
- **1,071 file PDF (~2.73 GB)** được tách riêng qua file `.gitignore` để không làm nghẽn Git và tránh lỗi vượt 100MB của GitHub.
- **GitHub Actions (`.github/workflows/run_pipeline.yml`)** đã cấu hình sẵn để tự động kéo file từ Google Drive về máy chủ GitHub và chạy bóc tách/tính toán đa tiến trình (4 vCPU, 16GB RAM).

---

## BƯỚC 1: Đẩy dự án lên GitHub

1. Mở trình duyệt, truy cập [GitHub.com](https://github.com) -> Bấm **New repository** (Tạo repo mới).
   - Đặt tên Repo (ví dụ: `nuclearbot-knowledge`).
   - Chọn **Public** hoặc **Private** tùy ý bạn.
   - **Không** tích chọn "Add a README file" hay "Add .gitignore" (vì ta đã tạo sẵn rồi).
   - Bấm **Create repository**.
2. Mở cửa sổ **PowerShell** hoặc **Terminal** tại thư mục `D:\dulieutraning`, copy và chạy các lệnh sau:

```powershell
# 1. Đưa tất cả file vào trạng thái sẵn sàng commit
git add .

# 2. Tạo commit đầu tiên
git commit -m "Khoi tao du an NuclearBot: Code, Markdown KB va Pipeline GitHub Actions"

# 3. Đổi tên nhánh chính thành main
git branch -M main

# 4. Gắn link repository GitHub của bạn (thay URL bên dưới bằng link repo thật vừa tạo)
git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repo>.git

# 5. Đẩy lên GitHub
git push -u origin main
```

---

## BƯỚC 2: Tải thư mục PDF lên Google Drive

1. Mở Google Drive trên trình duyệt.
2. Kéo thả thư mục `KHO_DU_LIEU_AI` (hoặc thư mục chứa các file PDF) từ máy tính lên Google Drive.
3. Sau khi tải lên xong:
   - Bấm chuột phải vào thư mục đó trên Google Drive -> Chọn **Chia sẻ** (Share) -> **Chia sẻ**.
   - Tại mục **Quyền truy cập chung**, chuyển từ *Hạn chế* sang:
     👉 **"Bất kỳ ai có đường liên kết" (Anyone with the link) - Người xem (Viewer)**.
   - Bấm **Sao chép đường liên kết** (Copy link).

---

## BƯỚC 3: Bấm nút chạy tính toán trên GitHub Actions

1. Trên trang Repository GitHub của bạn, bấm vào tab **Actions**.
2. Ở cột bên trái, bấm vào workflow: **"Run NuclearBot Training & Data Pipeline"**.
3. Ở bên phải, bấm vào nút **Run workflow**:
   - Ô **Link chia sẻ Google Drive**: Dán đường link bạn vừa sao chép ở Bước 2.
   - Ô **Số lượng file PDF tối đa**: Nhập số lượng bạn muốn chạy thử nghiệm (ví dụ `20`, `50` hoặc nhập `0` nếu muốn chạy toàn bộ).
4. Bấm nút màu xanh **Run workflow**.

---

## BƯỚC 4: Xem tiến trình và Tải kết quả

- GitHub sẽ tự động bật máy ảo (Ubuntu 4 vCPU, 16 GB RAM).
- Máy chủ sẽ tự động tải các file PDF từ Google Drive của bạn về với tốc độ mạng ~1 Gbps.
- Script đa tiến trình sẽ tận dụng cả 4 nhân CPU để bóc tách và phân tích dữ liệu song song.
- Sau khi chạy xong, ở mục **Artifacts** phía dưới trang kết quả, bạn sẽ thấy file:
  📦 `ket-qua-pipeline-nuclearbot.zip` -> Bấm vào để tải toàn bộ kết quả về máy tính!
