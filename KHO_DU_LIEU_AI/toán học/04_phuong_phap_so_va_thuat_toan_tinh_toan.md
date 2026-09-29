# CHƯƠNG 4: PHƯƠNG PHÁP SỐ VÀ THUẬT TOÁN TÍNH TOÁN VẬT LÝ HẠT NHÂN

## 1. Phương Pháp Tính Tích Phân Số (Numerical Integration)
- **Quy Tắc Simpson 1/3 & 3/8:**
  $$\int_{x_0}^{x_2} f(x) dx pprox rac{h}{3} [f(x_0) + 4f(x_1) + f(x_2)]$$
- **Tích Phân Cầu Gauss-Legendre & Gauss-Laguerre:**
  $$\int_{-1}^1 f(x) dx pprox \sum_{i=1}^N w_i f(x_i)$$
  với $x_i$ là nghiệm của đa thức Legendre $P_N(x)$ và $w_i$ là trọng số (Gauss weights).

## 2. Giải Phương Trình Vi Phân Số Trong Vật Lý Hạt Nhân
- **Phương Pháp Runge-Kutta Bậc 4 (RK4):** Tích phân từng bước phương trình vi phân cấp 1 và cấp 2.
- **Thuật Toán Numerov:** Chuyên dùng giải phương trình Schrödinger dạng $y''(x) + k^2(x) y(x) = 0$:
  $$\left(1 + rac{h^2}{12} k_{n+1}^2ight) y_{n+1} - 2\left(1 - rac{5h^2}{12} k_n^2ight) y_n + \left(1 + rac{h^2}{12} k_{n-1}^2ight) y_{n-1} = 0$$

## 3. Thuật Toán Chéo Hóa Ma Trận Kích Thước Lớn
- **Thuật Toán Lanczos & Davidson:** Tìm một số ít giá trị riêng nhỏ nhất (trạng thái cơ bản & kích thích thấp) của ma trận Hamilton HF/RPA có kích thước hàng triệu chiều mà không cần lưu toàn bộ ma trận.

## 4. Tối Ưu Hóa & Điều Chỉnh Tham Số (Parameter Fitting)
- **Phương Pháp Bình Phương Tối Thiểu (Least-Squares Fitting):**
  $$\chi^2(ec{p}) = \sum_{i=1}^M \left( rac{y_i^{exp} - y_i^{calc}(ec{p})}{\sigma_i} ight)^2$$
- **Thuật Toán Nelder-Mead Simplex & Levenberg-Marquardt:** Tự động điều chỉnh các tham số thế quang học $(V_0, W_0, R_0, a_0, V_{so})$ hoặc tham số Skyrme $(t_0, t_1, t_2, t_3, x_0,...)$ để khớp với số liệu thực nghiệm.
