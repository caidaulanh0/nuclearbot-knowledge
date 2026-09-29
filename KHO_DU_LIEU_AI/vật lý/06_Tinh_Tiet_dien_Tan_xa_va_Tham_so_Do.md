# Chương 6: Tính Tiết diện Tán xạ và Tham số (arXiv:2505.10971)

## 6.1 Phương trình Tán xạ Kênh liên kết (Coupled-Channels)
Khi tính toán thực tế tiết diện tán xạ, tương tác giữa neutron và hạt nhân bia có thể kích thích hạt nhân lên các trạng thái tập thể (collective states). Sự ảnh hưởng này được mô phỏng bằng hệ phương trình vi phân liên kết (coupled-channels equations):
$$ \left[ \frac{d^2}{dr^2} - \frac{l_\alpha(l_\alpha+1)}{r^2} + k_\alpha^2 \right] u_\alpha(r) = \frac{2\mu}{\hbar^2} \sum_{\alpha'} V_{\alpha \alpha'}(r) u_{\alpha'}(r) $$
- Hàm sóng tán xạ được khai triển thành các sóng riêng phần $u_\alpha(r)$.
- Cần giải hệ phương trình này bằng các phương pháp tích phân số (thường là Numerov hoặc ma trận R) tính từ lõi $r=0$ ra đến vùng tiệm cận $R_{\text{max}} \sim 20$ fm.

## 6.2 Tính Tiết diện (Cross Sections) và Phân bố góc
Sau khi giải hệ phương trình và khớp nối với điều kiện biên tiệm cận, ta thu được Ma trận S (S-matrix).
Từ Ma trận S, ta có thể tính toán trực tiếp các đại lượng vật lý có thể đo được trong thực nghiệm:
- **Tiết diện tán xạ đàn hồi (Elastic scattering cross-section).**
- **Tiết diện hấp thụ (Absorption/Reaction cross-section).**
- **Phân cực (Analyzing power):** Đặc biệt nhạy cảm với thành phần Spin-Orbit $W_0$ của lực Skyrme.

Theo kết quả mô phỏng, các kích thích tập thể biên độ nhỏ ở năng lượng thấp làm thay đổi đáng kể sự phân bố dòng hạt tán xạ, tác động mạnh lên tiết diện tán xạ góc lớn. Điều này chứng minh rằng việc tính toán chính xác thế bậc hai (PVC) là bắt buộc.
