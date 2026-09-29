# CHƯƠNG 1: TOÁN HỌC CƠ BẢN VÀ GIẢI TÍCH

## 1. Số Học Về Đại Số Cơ Bản
- **Phép tính số học:** Cộng, trừ, nhân, chia, lũy thừa ($a^n$), căn thức ($\sqrt[n]{x}$), logarithm ($\ln x, \log_{10} x$).
- **Số phức (Complex Numbers):**
  $$z = a + i b = r e^{i	heta}$$
  với $i^2 = -1$, $r = \sqrt{a^2 + b^2}$, $	heta = rctan(b/a)$. Công thức Euler: $e^{i	heta} = \cos	heta + i\sin	heta$.

## 2. Đạo Hàm và Nguyên Hàm / Tích Phân
- **Đạo hàm (Derivatives):**
  $$f'(x) = rac{df}{dx} = \lim_{\Delta x 	o 0} rac{f(x+\Delta x) - f(x)}{\Delta x}$$
  Quy tắc đạo hàm tích: $(uv)' = u'v + uv'$, quy tắc chuỗi: $rac{d}{dx}f(g(x)) = f'(g(x))g'(x)$.
- **Nguyên hàm & Tích phân (Integrals):**
  $$\int f(x) dx = F(x) + C$$
  Tích phân xác định: $\int_{a}^{b} f(x) dx = F(b) - F(a)$. Tích phân từng phần: $\int u dv = uv - \int v du$.
- **Đạo hàm riêng (Partial Derivatives):** Cho hàm nhiều biến $f(x, y, z)$, đạo hàm riêng theo $x$: $rac{\partial f}{\partial x}$.
- **Toán tử Gradient, Divergence, Curl, Laplacian:**
  $$
abla f = \left(rac{\partial f}{\partial x}, rac{\partial f}{\partial y}, rac{\partial f}{\partial z}ight)$$
  $$
abla^2 f = \Delta f = rac{\partial^2 f}{\partial x^2} + rac{\partial^2 f}{\partial y^2} + rac{\partial^2 f}{\partial z^2}$$

## 3. Khai Triển Chuỗi & Biến Đổi Integral
- **Khai triển Taylor / Maclaurin:**
  $$f(x) = \sum_{n=0}^{\infty} rac{f^{(n)}(a)}{n!} (x-a)^n$$
- **Biến đổi Fourier:**
  $$\hat{f}(\k) = \int_{-\infty}^{\infty} f(x) e^{-i k x} dx$$
- **Biến đổi Laplace:**
  $$F(s) = \int_{0}^{\infty} f(t) e^{-st} dt$$

## 4. Phương Trình Vi Phân (Differential Equations)
- **Phương trình vi phân thường (ODE):**
  $$rac{d^2 y}{dx^2} + p(x)rac{dy}{dx} + q(x)y = r(x)$$
- **Phương trình vi phân đạo hàm riêng (PDE):**
  - Phương trình Laplace: $
abla^2 \psi = 0$
  - Phương trình Wave: $
abla^2 \psi - rac{1}{v^2}rac{\partial^2 \psi}{\partial t^2} = 0$
  - Phương trình Schrödinger độc lập thời gian: $\left(-rac{\hbar^2}{2m}
abla^2 + V(ec{r})ight) \psi(ec{r}) = E \psi(ec{r})$
