# -*- coding: utf-8 -*-
"""
CẦU NỐI NHẬN THỨC (Cognitive Bridge) — mạng lưới TẠM THỜI liên kết Não 1 + Não 2.
Não 1 = ontology.db (khái niệm, CHẮC CHẮN) | Não 2 = core_kb.db (fact, TẠM THỜI).
Bảng cross_links lưu trong core_kb.db (giữ ontology.db "vô trùng"/read-only).
Mặc định: confidence=0.5, status='provisional'. Antigravity chốt.
"""
import sqlite3

KB_PATH = r"D:\dulieutraning\automation_bridge\core_kb.db"

SCHEMA = """
DROP TABLE IF EXISTS cross_links;
CREATE TABLE cross_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_node TEXT NOT NULL,
    fact_name TEXT NOT NULL,
    relation TEXT NOT NULL CHECK(relation IN ('grounds','about','instantiates','contradicts')),
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'provisional' CHECK(status IN ('provisional','verified','contradicted')),
    note TEXT,
    UNIQUE(ontology_node, fact_name, relation)
);
CREATE INDEX idx_cl_node ON cross_links(ontology_node);
CREATE INDEX idx_cl_fact ON cross_links(fact_name);
"""

# (fact_name, ontology_node, relation)
CROSS_LINKS = [
    # --- phương trình/công thức = nền tảng (grounds) ---
    ("schrodinger_equation", "Phương trình Schrödinger (TDSE/TISE)", "grounds"),
    ("half_life_equation", "Chu kỳ bán rã", "grounds"),
    ("binding_energy_formula", "Năng lượng liên kết", "grounds"),
    ("semi_empirical_mass_formula", "Công thức Weizsäcker", "grounds"),
    ("mass_energy_equation", "Năng lượng liên kết", "grounds"),
    ("de_broglie_wavelength", "Hàm sóng & |ψ|²", "grounds"),
    # --- hằng số = số liệu nền (grounds) ---
    ("reduced_planck_constant", "Phương trình Schrödinger (TDSE/TISE)", "grounds"),
    ("speed_of_light", "Năng lượng liên kết", "grounds"),
    ("neutron_mass", "Cấu tạo hạt nhân", "grounds"),
    ("proton_mass", "Cấu tạo hạt nhân", "grounds"),
    ("elementary_charge", "Lực Coulomb", "grounds"),
    ("fine_structure_constant", "Cấu trúc tinh tế & siêu tinh tế", "grounds"),
    ("decay_constant", "Chu kỳ bán rã", "grounds"),
    ("mass_defect", "Năng lượng liên kết", "grounds"),
    ("atomic_number", "Đồng vị & nuclide & isotone", "grounds"),
    ("mass_number", "Đồng vị & nuclide & isotone", "grounds"),
    ("neutron_number", "Đồng vị & nuclide & isotone", "grounds"),
    # --- định luật/khái niệm = mô tả (about) ---
    ("radioactive_decay_law", "Phân rã alpha/beta/gamma", "about"),
    ("conservation_of_energy", "Định luật bảo toàn", "about"),
    ("coulomb_law", "Lực Coulomb", "about"),
    ("energy_mass_equivalence", "Năng lượng liên kết", "about"),
    ("shell_model", "Mô hình lớp vỏ (shell model)", "about"),
    ("woods_saxon", "Thế Woods-Saxon", "about"),
    ("liquid_drop_model", "Mô hình giọt lỏng", "about"),
    ("strong_force", "Lực hạt nhân mạnh", "about"),
    ("nucleon", "Cấu tạo hạt nhân", "about"),
    ("half_life", "Chu kỳ bán rã", "about"),
    ("binding_energy", "Năng lượng liên kết", "about"),
    # --- đồng vị/nguyên tố = cụ thể hóa (instantiates) ---
    ("U-238", "Đồng vị & nuclide & isotone", "instantiates"),
    ("U-235", "Đồng vị & nuclide & isotone", "instantiates"),
    ("Th-234", "Đồng vị & nuclide & isotone", "instantiates"),
    ("H-1", "Đồng vị & nuclide & isotone", "instantiates"),
    ("H-2", "Đồng vị & nuclide & isotone", "instantiates"),
    ("H-3", "Đồng vị & nuclide & isotone", "instantiates"),
    ("He-4", "Đồng vị & nuclide & isotone", "instantiates"),
    ("element_uranium", "Bảng tuần hoàn", "instantiates"),
    ("element_thorium", "Bảng tuần hoàn", "instantiates"),
    ("element_hydrogen", "Bảng tuần hoàn", "instantiates"),
    ("element_helium", "Bảng tuần hoàn", "instantiates"),
]


def main():
    conn = sqlite3.connect(KB_PATH)
    conn.executescript(SCHEMA)
    # kiểm tra fact tồn tại
    fact_names = {r[0] for r in conn.execute("SELECT name FROM facts")}
    missing = [f for (f, _, _) in CROSS_LINKS if f not in fact_names]
    if missing:
        print("[WARN] fact khong ton tai (bo qua):", missing)
    ins = 0
    for fact_name, node, rel in CROSS_LINKS:
        if fact_name not in fact_names:
            continue
        cur = conn.execute(
            "INSERT OR IGNORE INTO cross_links(ontology_node, fact_name, relation, confidence, status) VALUES (?,?,?,0.5,'provisional')",
            (node, fact_name, rel))
        ins += cur.rowcount
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM cross_links").fetchone()[0]
    byrel = conn.execute("SELECT relation, COUNT(*) FROM cross_links GROUP BY relation").fetchall()
    bystatus = conn.execute("SELECT status, COUNT(*) FROM cross_links GROUP BY status").fetchall()
    print(f"=== CẦU NỐI xây xong ===")
    print(f"cross_links: {n} (mới insert: {ins})")
    print("theo relation:", dict(byrel))
    print("theo status:", dict(bystatus))
    conn.close()


if __name__ == "__main__":
    main()
