# Chương 5: Thế Quang học Vi mô và Thế Bậc Hai

## 5.1 Xây dựng Thế Quang Học Vi Mô (MOP)
Thế quang học toàn phần được cấu thành từ hai thành phần: thế tĩnh và thế động (tương quan):
$$ V_{\text{opt}} = V_{HF} + \Delta\Sigma(\omega) $$
- $V_{HF}$ là thế trường trung bình (thế bậc nhất), là thế thực và đóng vai trò chính trong tán xạ đàn hồi.
- $\Delta\Sigma(\omega) = \Sigma(\omega) - \frac{1}{2}\Sigma^{(2)}(\omega)$ là thế bậc hai, đại diện cho toán tử khối lượng, chứa các hiệu ứng ghép cặp hạt-dao động (PVC) đã tính ở Chương 4. Thế này là số phức, phần ảo của nó gây ra sự hấp thụ.

## 5.2 Phần ảo của Thế Bậc Hai
Phần ảo $W(\mathbf{R}, \mathbf{s}) = \text{Im}\Delta\Sigma(\mathbf{r}, \mathbf{r'}, \omega)$ sinh ra hiện tượng hấp thụ (chuyển tán xạ đàn hồi thành phi đàn hồi). Phân tích thành phần sóng riêng phần:
$$ W(R, s) = \sum_{lj} \frac{2j+1}{4\pi} \text{Im}\Delta\Sigma_{lj}(r, r', \omega) $$
Trong đó $\mathbf{R}$ liên quan đến bán kính, $\mathbf{s}$ thể hiện tính phi địa phương. 

## 5.3 Tính phi địa phương (Nonlocality) của MOP (arXiv:2508.12699)
Thế quang học vi mô phụ thuộc vào hai tọa độ không gian $\mathbf{r}$ và $\mathbf{r'}$. Tính phi địa phương này có thể được lượng hóa bằng tham số $\beta(E, r)$ (theo xấp xỉ Perey-Buck):
$$ H(\mathbf{s}) = \frac{1}{(\pi \beta^2)^{3/2}} \exp\left( -\frac{\mathbf{s}^2}{\beta^2} \right) $$
MOP chứng minh rằng $\beta$ không phải là một hằng số phổ quát mà phụ thuộc năng lượng, bán kính và hạt nhân bia. Ở các hạt nhân nhẹ ($^{16}\text{O}$), tính phi địa phương ở lõi nhỏ hơn ở bề mặt, trong khi ở hạt nhân nặng ($^{208}\text{Pb}$), hai giá trị này tương đương nhau. Đây là sự khác biệt lớn so với các thế vĩ mô Woods-Saxon truyền thống (thường coi $\beta$ là hằng số hoặc bỏ qua).
