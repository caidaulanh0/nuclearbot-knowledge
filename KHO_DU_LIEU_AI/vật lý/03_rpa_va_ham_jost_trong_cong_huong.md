# Gần đúng pha ngẫu nhiên (RPA) và Hàm Jost trong trạng thái cộng hưởng

## 1. Khuôn khổ RPA (Random Phase Approximation)
RPA là phương pháp lý thuyết cơ bản để mô tả các trạng thái kích thích tập thể (collective excited states) hay còn gọi là phonon trong hạt nhân. Trong RPA, các hạt nhân phản ứng lại các nhiễu loạn bên ngoài thông qua các dao động của toàn bộ hệ nucleon. 
Phương trình RPA có thể viết dưới dạng ma trận:
$$ \begin{pmatrix} A & B \\ B^* & A^* \end{pmatrix} \begin{pmatrix} X \\ Y \end{pmatrix} = \omega_\nu \begin{pmatrix} X \\ -Y \end{pmatrix} $$
Nghiệm của phương trình này cung cấp năng lượng kích thích $\omega_\nu$ và biên độ chuyển dời của các trạng thái tập thể (ví dụ: dao động đơn cực, lưỡng cực, tứ cực).

## 2. Cộng hưởng lưỡng cực khổng lồ (Giant Dipole Resonance - GDR) và Hàm Jost
Trạng thái cộng hưởng, chẳng hạn như GDR trong hạt nhân $^{16}\text{O}$, không phải là trạng thái liên kết thực sự mà là trạng thái phân rã, có năng lượng phức:
$$ E = E_R - i\frac{\Gamma}{2} $$
Trong đó $E_R$ là vị trí cộng hưởng và $\Gamma$ là bề rộng cộng hưởng.

Để khảo sát chính xác các năng lượng phức (complex eigenenergies) này trong khuôn khổ RPA, lý thuyết hàm Jost (Jost function) từ lý thuyết tán xạ được mở rộng. Bằng cách định vị các cực (poles) của ma trận tán xạ (S-matrix) trên mặt phẳng năng lượng phức thông qua hàm Jost, các nhà nghiên cứu có thể mô tả chính xác cả năng lượng và bề rộng phân rã của các mode tập thể khổng lồ.
