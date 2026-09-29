# CHƯƠNG 3: TOÁN VẬT LÝ HẠT NHÂN: HARTREE-FOCK, PVC VÀ THẾ QUANG HỌC

## 1. Lý Thuyết Hartree-Fock (HF - Static Mean Field)
- **Định hình Slater Determinant:** Hàm sóng hạt nhân $A$ nucleon:
  $$\Phi(1, 2, \dots, A) = rac{1}{\sqrt{A!}} \det |\phi_i(j)|$$
- **Phương trình Self-Consistent Hartree-Fock:**
  $$h_{HF} \phi_i(r) = \left[ -rac{\hbar^2}{2m}
abla^2 + V_{HF}(r) ight] \phi_i(r) = \epsilon_i \phi_i(r)$$
  với thế trung tâm $V_{HF}$ bao gồm thế Direct (Hartree) và thế Exchange (Fock).
- **Tương tác Skyrme & Gogny:** Dạng tương tác hiệu dụng 2 hạt dùng trong HF hạt nhân.

## 2. Thế Quang Học (Optical Potential - Nucleon-Nucleus Scattering)
- **Dạng Tham Số Woods-Saxon:**
  $$V(r) = -V_0 f(r, R_0, a_0) - i W_v f(r, R_w, a_w) + 4 i a_s W_s rac{d}{dr}f(r, R_s, a_s) + V_{so} \left(rac{\hbar}{m_\pi c}ight)^2 rac{1}{r}rac{d}{dr}f(r, R_{so}, a_{so}) (ec{l}\cdotec{s})$$
  trong đó hàm dạng Woods-Saxon:
  $$f(r, R, a) = rac{1}{1 + \exp\left(rac{r - R}{a}ight)}$$
  $R = r_0 A^{1/3}$.
- **Tán xạ Sóng Từng Phần (Partial Wave Analysis):**
  Hàm sóng tán xạ $Y_{lm}$, Ma trận $S_l = e^{2i\delta_l}$ với $\delta_l$ là độ lệch pha (phase shift).
  Tiết diện toàn phần $\sigma_{tot}$, tiết diện đàn hồi $\sigma_{el}$, tiết diện phản ứng $\sigma_{r} = \sigma_{tot} - \sigma_{el}$.

## 3. Ghép Cặp Hạt - Dao Động (PVC - Particle-Vibration Coupling)
- **Phương Trình Dyson Cho Propagator $G(E)$:**
  $$[E - h_{HF} - \Sigma(E, r, r')] G(E, r, r') = \delta(r - r')$$
- **Mass Operator $\Sigma(E)$ (Self-Energy):**
  $$\Sigma(E) = \Sigma_{\infty} + \Delta\Sigma(E)$$
  - $\Sigma_{\infty} = h_{HF}$: Thế trung bình tĩnh Hartree-Fock.
  - $\Delta\Sigma(E)$: Phần động năng năng lượng phụ thuộc do PVC đóng góp (tương tác với phonon $2p1h, 2h1p$).
- **Phần Tử Ma Trận Ghép Cặp Phonon (Coupling Matrix Element $M_{lpha, i}^{(n)}$):**
  $$\Sigma_{lphaeta}(E) = \sum_{n, i} rac{M_{lpha, i}^{(n)\dagger} M_{i, eta}^{(n)}}{E - (\epsilon_i + \Omega_n) + i\eta} + 	ext{phần lỗ}$$
  với $\Omega_n$ là năng lượng kích thích phonon (RPA mode), $\eta 	o 0^+$ tạo phần ảo đại diện cho sự hấp thụ / phân rã sức hạt đơn.
- **Tác động của PVC:**
  - Làm tăng khối lượng hiệu dụng $m^*/m > 1$ gần bề mặt Fermi.
  - Tạo ra phần ảo cho Thế quang học hiển vi (Microscopic Optical Potential).
