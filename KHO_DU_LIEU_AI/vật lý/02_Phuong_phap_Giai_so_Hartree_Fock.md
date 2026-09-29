# Chương 2: Phương pháp Giải số Hartree-Fock

## 2.1 Phương trình Schrödinger Xuyên tâm (Radial Schrödinger Equation)
Từ tương tác Skyrme, ta thu được trường trung bình Hartree-Fock $U_{HF}(r, E)$. Quá trình giải bài toán tán xạ hạt nhân yêu cầu giải phương trình Schrödinger xuyên tâm:
$$ \left[ -\frac{\hbar^2}{2m^*(r)} \frac{d^2}{dr^2} + \frac{\hbar^2 l(l+1)}{2m^*(r)r^2} + U_{\text{central}}(r, E) + U_{\text{so}}(r, E)\mathbf{L}\cdot\mathbf{S} \right] u_{lj}(r) = E u_{lj}(r) $$

Trong đó:
- $m^*(r)$ là khối lượng hiệu dụng (effective mass) do sự có mặt của thế phụ thuộc vận tốc.
- $U_{\text{central}}$ là thế trung tâm cục bộ tương đương.
- $U_{\text{so}}$ là thế spin-quỹ đạo.
- $u_{lj}(r)$ là hàm sóng xuyên tâm (radial wavefunction) cho sóng riêng phần có xung lượng góc quỹ đạo $l$ và tổng xung lượng góc $j$.

## 2.2 Kỹ thuật Giải số (Numerical Methods)
Theo chi tiết tính toán trong bài báo:
- **Không gian tính toán:** Các phương trình xuyên tâm được giải trong một chiếc hộp không gian có bán kính $R_{\text{max}} = 15 \text{ fm}$ (hoặc có thể lên tới 20 fm để ghép nối chính xác với hàm sóng tiệm cận).
- **Lưới tọa độ (Mesh):** Trục bán kính được chia nhỏ (rời rạc hóa) với bước lưới $\Delta r = 0.1 \text{ fm}$.
- **Thuật toán:** Thường sử dụng phương pháp Numerov thay vì Runge-Kutta bậc 4 (RK4). Lý do là vì Numerov tối ưu cực tốt cho các phương trình vi phân dạng $y'' + f(x)y = 0$, đem lại sai số bậc $O(h^6)$ chỉ với 2 lần gọi hàm, tính toán nhanh hơn và ổn định hơn cho các hàm sóng dao động liên tục ở vùng xa lõi hạt nhân.

## 2.3 Đầu ra (Outputs)
Kết quả của phép giải HF cung cấp các trạng thái hạt đơn hạt $\phi_{\hat{\alpha}} = \frac{u_\alpha(r)}{r} \mathcal{Y}_{\hat{\alpha}} \chi_{q_a}$. Các trạng thái bị chiếm (occupied - holes) và chưa bị chiếm (unoccupied - particles) này sẽ làm đầu vào cho tính toán RPA tiếp theo.
