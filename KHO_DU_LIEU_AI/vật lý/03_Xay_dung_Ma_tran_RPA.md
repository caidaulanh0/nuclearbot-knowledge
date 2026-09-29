# Chương 3: Xây dựng Ma trận RPA và Trạng thái Kích thích Tập thể

## 3.1 Phương trình RPA (Random Phase Approximation)
Sau khi có các trạng thái đơn hạt từ HF, ta cần tính các trạng thái kích thích của toàn bộ hạt nhân (ví dụ: cộng hưởng khổng lồ - Giant Resonances). Khung RPA được sử dụng phổ biến bằng cách giải phương trình trị riêng dạng ma trận:

$$ \begin{pmatrix} A & B \\ B^* & A^* \end{pmatrix} \begin{pmatrix} X \\ Y \end{pmatrix} = \hbar\omega_\nu \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} \begin{pmatrix} X \\ Y \end{pmatrix} $$

Trong đó:
- $\omega_\nu$ là tần số (hoặc năng lượng) kích thích của trạng thái phonon thứ $\nu$.
- $X, Y$ là các biên độ vector riêng (eigenvectors), đại diện cho xác suất tìm thấy cấu hình hạt-trống (particle-hole) tạo ra (X) hoặc hủy (Y) phonon.

## 3.2 Các thành phần của Ma trận A và B
Theo bài báo, các phần tử ma trận được định nghĩa bởi:
$$ A_{php'h'} = (\epsilon_p - \epsilon_h) \delta_{pp'}\delta_{hh'} + \tilde{v}_{ph'p'h} $$
$$ B_{php'h'} = \tilde{v}_{pp'h'h} $$

Với $\tilde{v}$ là thành phần ma trận của tương tác thặng dư $V_{\text{res}}$ (dựa trên tương tác Skyrme SLy5). Trong tính toán, xấp xỉ Quasi-Boson (QBA) được áp dụng: $[c_h^\dagger c_p, c_{p'}^\dagger c_{h'}] \approx \delta_{pp'} \delta_{hh'}$.

## 3.3 Điều kiện cắt cụt (Truncation) trong Code
Để giải ma trận này trên máy tính, không gian cấu hình hạt-lỗ phải bị giới hạn (cắt cụt) để tránh nổ kích thước ma trận:
- Trong mã HF/RPA, các trạng thái lỗ (holes) được lấy toàn bộ, nhưng các trạng thái hạt (particles - chưa chiếm chỗ) được giới hạn ở các mức $\epsilon_\lambda < 50 \text{ MeV}$.
- Chỉ các trạng thái phonon có năng lượng $< 50 \text{ MeV}$ và độ đa cực (multipolarity) $L$ từ 0 đến 5 mới được giữ lại.
- Dùng quy tắc tổng năng lượng EWSR (Energy-Weighted Sum Rule) để kiểm tra độ tin cậy. Các trạng thái mạnh (như $3^-$ và $4^+$) có thể đạt $> 99.5\%$ EWSR.
- Trạng thái giả (Spurious states) liên quan đến chuyển động khối tâm ở mode $1^-$ bị loại bỏ thủ công.

## 3.4 Hàm Jost trong RPA
Để xác định chính xác năng lượng phức $E = E_R - i\Gamma/2$ của cộng hưởng lưỡng cực khổng lồ (GDR) ở $^{16}\text{O}$ (như trong arXiv:2212.02276), bài toán tìm nghiệm được mở rộng ra mặt phẳng phức bằng cách tìm điểm không (zeros) của định thức hàm Jost:
$$ \det \mathcal{J}(E) = 0 $$
Các cực (poles) này cho biết vị trí năng lượng và bề rộng phân rã của cộng hưởng một cách chính xác mà không phụ thuộc vào nền liên tục.
