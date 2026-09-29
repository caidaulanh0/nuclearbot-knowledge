# Tương tác Skyrme và Phương pháp Hartree-Fock

## 1. Tương tác hiệu dụng Skyrme
Tương tác Skyrme là một tương tác hiệu dụng giữa các nucleon (nucleon-nucleon interaction), thường được biểu diễn dưới dạng lực tiếp xúc (zero-range) phụ thuộc vào mật độ và vận tốc. Dạng tổng quát của tương tác Skyrme bao gồm nhiều số hạng:
$$ V_{Skyrme} = V_{central} + V_{density} + V_{velocity} + V_{spin-orbit} $$

Các tham số cơ bản thường bao gồm $t_0, t_1, t_2, t_3$ và $W_0$:
- **Số hạng trung tâm ($t_0$) và phụ thuộc mật độ ($t_3$):** Quyết định các tính chất cơ bản của vật chất hạt nhân như năng lượng liên kết và mật độ bão hòa.
- **Số hạng phụ thuộc vận tốc ($t_1, t_2$):** Phản ánh tính chất phi địa phương (non-locality) của lực hạt nhân, ảnh hưởng trực tiếp đến khối lượng hiệu dụng (effective mass) của nucleon. Các số hạng này đóng vai trò quan trọng trong việc mô tả sự tán xạ đàn hồi của neutron.
- **Số hạng spin-quỹ đạo ($W_0$):** Rất quan trọng trong việc tái tạo sự tách mức năng lượng spin-quỹ đạo, đồng thời có ảnh hưởng lớn đến độ phân cực (analyzing powers) trong các phản ứng tán xạ neutron.

## 2. Phương pháp Hartree-Fock (HF)
Phương pháp Hartree-Fock là một xấp xỉ trường trung bình (mean-field approximation), trong đó các nucleon được xem như chuyển động độc lập trong một thế năng trung bình được tạo ra bởi tất cả các nucleon khác.

Thế Hartree-Fock $V_{HF}$ (thế bậc nhất) được thu được từ tương tác Skyrme thông qua việc cực tiểu hóa hàm năng lượng:
$$ U_{HF}(\mathbf{r}) = U_{local}(\mathbf{r}) + U_{non-local}(\mathbf{r}, \mathbf{p}) $$

Mặc dù trường trung bình HF cung cấp một mô tả rất tốt về trạng thái cơ bản (ground state) của hạt nhân, nó chưa bao gồm các hiệu ứng động lực học như sự hấp thụ hạt trong quá trình tán xạ. Để giải quyết điều này, cần đến các bổ chính bậc cao hơn.
