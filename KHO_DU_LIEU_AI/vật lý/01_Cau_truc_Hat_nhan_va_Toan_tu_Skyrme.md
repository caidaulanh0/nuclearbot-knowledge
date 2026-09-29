# Chương 1: Cấu trúc hạt nhân và Toán tử Skyrme

## 1.1 Mở đầu về Tương tác Nucleon-Nucleon
Trong vật lý hạt nhân, tương tác giữa các nucleon (proton và neutron) rất phức tạp. Để giải quyết bài toán nhiều hạt, người ta sử dụng các tương tác hiệu dụng (effective interactions). Tương tác Skyrme là một trong những tương tác hiệu dụng thành công nhất, được thiết kế dưới dạng lực tiếp xúc (zero-range) nhưng phụ thuộc vào vận tốc và mật độ.

## 1.2 Dạng toán học của Toán tử Skyrme
Theo bài báo *Phys. Rev. C 102, 034608 (2020)*, tương tác Skyrme chuẩn trong không gian tọa độ được viết dưới dạng:

$$ V_{\text{Skyrme}} = t_0(1+x_0 P_\sigma)\delta(\mathbf{r}) + \frac{1}{2}t_1(1+x_1 P_\sigma)[\mathbf{k}'^2 \delta(\mathbf{r}) + \delta(\mathbf{r})\mathbf{k}^2] + t_2(1+x_2 P_\sigma)\mathbf{k}'\cdot \delta(\mathbf{r})\mathbf{k} + i W_0(\mathbf{\sigma}_1 + \mathbf{\sigma}_2)\cdot [\mathbf{k}' \times \delta(\mathbf{r})\mathbf{k}] $$

Giải thích các đại lượng:
- $\mathbf{r} = \mathbf{r}_1 - \mathbf{r}_2$ là vector khoảng cách tương đối.
- $\mathbf{k} = \frac{1}{2i}(\vec{\nabla}_1 - \vec{\nabla}_2)$ là toán tử xung lượng tương đối tác dụng sang phải, $\mathbf{k}'$ tác dụng sang trái.
- $P_\sigma$ là toán tử hoán vị spin.
- $t_0, x_0$: Các tham số của số hạng trung tâm (central term).
- $t_1, x_1, t_2, x_2$: Các tham số của số hạng phụ thuộc vận tốc (velocity-dependent terms).
- $W_0$: Tham số của tương tác spin-quỹ đạo (spin-orbit).

## 1.3 Ứng dụng trong Tính toán
Khi lập trình (Fortran/Python) để mô phỏng tương tác này, chúng ta không tính toán trực tiếp với các hàm Delta Dirac, mà thay vào đó sẽ tích phân chúng để xây dựng mật độ thế năng (energy density functional - EDF).
Trong bài toán tán xạ, các số hạng $t_1, t_2$ sinh ra tính phi địa phương (non-locality), dẫn đến sự phụ thuộc khối lượng hiệu dụng (effective mass $m^*(r)$) vào bán kính $r$, làm thay đổi hình dạng của hàm sóng tán xạ so với thế địa phương thông thường. Số hạng $W_0$ đóng vai trò then chốt trong việc giải thích độ phân cực spin (analyzing powers).
