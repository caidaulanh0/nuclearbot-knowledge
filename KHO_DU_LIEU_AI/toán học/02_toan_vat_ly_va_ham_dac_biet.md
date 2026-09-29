# CHƯƠNG 2: TOÁN VẬT LÝ VÀ CÁC HÀM ĐẶC BIỆT

## 1. Đại Số Tuyến Tính Vận Dụng Trong Cơ Học Lượng Tử
- **Vector & Ma Trận:** Vector trạng thái $|\psiangle$, ma trận $A_{ij} = \langle i|A|jangle$.
- **Bài toán Giá trị riêng & Vector riêng (Eigenvalue Problem):**
  $$A ec{v} = \lambda ec{v} \iff \det(A - \lambda I) = 0$$
- **Không gian Hilbert & Ký hiệu Dirac Bra-Ket:**
  - Ket $|\psiangle$, Bra $\langle\phi|$, Tích trong $\langle\phi|\psiangle$.
  - Toán tử Hermite $H^\dagger = H$: Giá trị riêng của toán tử Hermite luôn là số thực (đại lượng vật lý đo được).
  - Đại số giao hoán (Commutator): $[A, B] = AB - BA$. Nguyên lý bất định Heisenberg: $[x, p_x] = i\hbar$.

## 2. Mô-men Động Lượng & Đại Số Racah (Angular Momentum Algebra)
- **Toán tử Mô-men động lượng:** $ec{J} = (J_x, J_y, J_z)$, $[J_i, J_j] = i\hbar \epsilon_{ijk} J_k$.
- **Hệ số Clebsch-Gordan (CG Coefficients):**
  Gặp trong việc cộng mô-men động lượng hạt nhân $j_1 + j_2 = J$:
  $$|j_1 j_2 J Mangle = \sum_{m_1, m_2} C_{j_1 m_1 j_2 m_2}^{J M} |j_1 m_1angle |j_2 m_2angle$$
- **Ký hiệu Wigner 3j, 6j, 9j:**
  $$egin{pmatrix} j_1 & j_2 & J \ m_1 & m_2 & -M \end{pmatrix} = rac{(-1)^{j_1 - j_2 + M}}{\sqrt{2J + 1}} C_{j_1 m_1 j_2 m_2}^{J M}$$
  Dùng để tính toán phần góc của phần tử ma trận tương tác hạt nhân (Wigner-Eckart theorem).

## 3. Các Hàm Đặc Biệt Trong Vật Lý Hạt Nhân
- **Đa thức Legendre & Associated Legendre Functions:**
  $$P_l(x) = rac{1}{2^l l!} rac{d^l}{dx^l}(x^2 - 1)^l$$
- **Hàm Spherical Harmonics ($Y_{lm}(	heta, \phi)$):**
  Nghiệm phần góc của phương trình Schrödinger trong trường thế trung tâm:
  $$Y_{lm}(	heta, \phi) = (-1)^m \sqrt{rac{2l+1}{4\pi} rac{(l-m)!}{(l+m)!}} P_l^m(\cos	heta) e^{i m \phi}$$
- **Hàm Bessel & Hankel (Cầu):**
  Nghiệm phần bán kính của hạt tự do hoặc hạt trong tán xạ: $j_l(kr), n_l(kr), h_l^{(1)}(kr), h_l^{(2)}(kr)$.
- **Hàm Gamma ($\Gamma(z)$) và Hàm Beta ($B(p, q)$):**
  $$\Gamma(z) = \int_0^\infty t^{z-1} e^{-t} dt$$
