# -*- coding: utf-8 -*-
"""
LỚP NÃO THỨ 2 — Core Knowledge Base (mạng lưới tri thức sự kiện)
Đập đi xây lại core_kb.db theo thiết kế Antigravity chốt:
  - 2 bảng: facts (cột type) + fact_edges
  - Ingest HYBRID: rule-based (regex + dictionary) cho constant/unit/equation,
    + links tường minh cho quan hệ chuyên môn; LLM bổ sung sau.
  - Mỗi lần nạp fact mới -> auto_link() tự xây edges -> mạng lưới chặt chẽ.

Chạy: python build_corekb.py   (idempotent: UNIQUE name / UNIQUE edge)
"""
import sqlite3, json, re, os, sys

KB_PATH = r"D:\dulieutraning\automation_bridge\core_kb.db"

TYPES = ('constant', 'law', 'equation', 'isotope', 'unit', 'definition')
RELATIONS = ('uses', 'defined_by', 'derived_from', 'appears_in', 'converts_to',
             'decays_to', 'relates_to', 'measured_in', 'composed_of',
             'is_isotope_of', 'interacts_via')

SCHEMA = """
DROP TABLE IF EXISTS constants;
DROP TABLE IF EXISTS fact_edges;
DROP TABLE IF EXISTS facts;
CREATE TABLE facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('constant','law','equation','isotope','unit','definition')),
    name TEXT NOT NULL UNIQUE,
    label TEXT,
    description TEXT,
    value_json TEXT,
    unit TEXT,
    source TEXT,
    verified_by TEXT DEFAULT 'user',
    verified_date TEXT,
    tags TEXT
);
CREATE TABLE fact_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation TEXT NOT NULL CHECK(relation IN ('uses','defined_by','derived_from','appears_in','converts_to','decays_to','relates_to','measured_in','composed_of','is_isotope_of','interacts_via')),
    weight REAL DEFAULT 1.0,
    note TEXT,
    UNIQUE(source_id, target_id, relation)
);
CREATE INDEX idx_fe_src ON fact_edges(source_id);
CREATE INDEX idx_fe_tgt ON fact_edges(target_id);
"""

# Dictionary tham chiếu: token (xuất hiện trong latex/description) -> (tên fact, quan hệ)
# Rule-based Lớp 1 — chính xác tuyệt đối, không ảo giác.
SYMBOL_MAP = [
    (r'\\hbar|\bhbar\b|\bh_bar\b', 'reduced_planck_constant', 'uses'),
    (r'\\lambda|\blambda\b|\bdecay constant\b', 'decay_constant', 'uses'),
    (r'\bm_p\b|\bproton mass\b', 'proton_mass', 'uses'),
    (r'\bm_n\b|\bneutron mass\b', 'neutron_mass', 'uses'),
    (r'\bm_e\b|\belectron mass\b', 'electron_mass', 'uses'),
    (r'c\^2|\bc\s*²', 'speed_of_light', 'uses'),
    (r'\\alpha|\bfine[- ]structure\b', 'fine_structure_constant', 'uses'),
    (r't_\{1/2\}|t1/2|\bhalf[- ]life\b|\bchu kỳ bán rã\b', 'half_life', 'uses'),
    (r'\bN_0\b|\bN0\b', 'initial_quantity', 'uses'),
    (r'\\Delta m|\bmass defect\b|\bđộ hụt khối\b', 'mass_defect', 'uses'),
    (r'[^a-zA-Z]Z[^a-zA-Z]|\batomic number\b|\bsố proton\b', 'atomic_number', 'uses'),
    (r'\bneutron number\b|\bsố neutron\b', 'neutron_number', 'uses'),
    (r'\bmass number\b|\bsố khối\b', 'mass_number', 'uses'),
    (r'\bWoods[- ]Saxon\b', 'woods_saxon', 'uses'),
    (r'\bSchr[öo]dinger\b', 'schrodinger_equation', 'uses'),
]

# Ký hiệu hóa học -> tên fact nguyên tố (cho auto is_isotope_of)
ELEMENT_SYMBOL = {
    'U': 'element_uranium', 'Th': 'element_thorium', 'H': 'element_hydrogen',
    'He': 'element_helium', 'C': 'element_carbon', 'O': 'element_oxygen',
    'N': 'element_nitrogen', 'Fe': 'element_iron',
}

# ============ SEED DATA ============
SEED = [
    # ---- UNITS ----
    {"type":"unit","name":"kg","label":"kilogram","description":"Đơn vị khối lượng SI.","unit":"kg"},
    {"type":"unit","name":"MeV","label":"mega-electronvolt","description":"Đơn vị năng lượng thông dụng trong vật lý hạt nhân.","unit":"MeV"},
    {"type":"unit","name":"MeV/c2","label":"MeV/c²","description":"Đơn vị khối lượng qua hệ thức E=mc².","unit":"MeV/c²","links":[{"target":"kg","relation":"converts_to","note":"1 u = 931.494 MeV/c²"}]},
    {"type":"unit","name":"barn","label":"barn","description":"Đơn vị tiết diện phản ứng = 10⁻²⁸ m².","unit":"barn"},
    {"type":"unit","name":"fm","label":"femtometer","description":"Đơn vị độ dài hạt nhân = 10⁻¹⁵ m.","unit":"fm"},
    {"type":"unit","name":"u","label":"đơn vị khối lượng nguyên tử","description":"1 u ≈ 931.494 MeV/c², xấp xỉ khối lượng nucleon.","unit":"u","links":[{"target":"MeV/c2","relation":"converts_to","note":"1 u ≈ 931.494 MeV/c²"}]},

    # ---- CONSTANTS ----
    {"type":"constant","name":"speed_of_light","label":"tốc độ ánh sáng c","description":"Tốc độ ánh sáng trong chân không.","value":{"value":2.99792458e8,"unit":"m/s"},"unit":"m/s","source":"CODATA 2018","tags":"hằng số cơ bản"},
    {"type":"constant","name":"reduced_planck_constant","label":"hằng số Planck rút gọn ℏ","description":"ℏ = h/2π, dùng trong cơ học lượng tử.","value":{"value":6.582119569e-22,"unit":"MeV·s"},"unit":"MeV·s","source":"CODATA 2018"},
    {"type":"constant","name":"neutron_mass","label":"khối lượng neutron","description":"Khối lượng nghỉ của neutron.","value":{"value":939.56542052,"unit":"MeV/c²"},"unit":"MeV/c2","source":"CODATA 2018"},
    {"type":"constant","name":"proton_mass","label":"khối lượng proton","description":"Khối lượng nghỉ của proton.","value":{"value":938.27208816,"unit":"MeV/c²"},"unit":"MeV/c2","source":"CODATA 2018"},
    {"type":"constant","name":"electron_mass","label":"khối lượng electron","description":"Khối lượng nghỉ của electron.","value":{"value":0.51099895,"unit":"MeV/c²"},"unit":"MeV/c2","source":"CODATA 2018"},
    {"type":"constant","name":"elementary_charge","label":"điện tích nguyên tố e","description":"Điện tích của proton.","value":{"value":1.602176634e-19,"unit":"C"},"unit":"C","source":"CODATA 2018"},
    {"type":"constant","name":"fine_structure_constant","label":"hằng số cấu trúc tinh tế α","description":"α ≈ 1/137, đặc trưng cường độ tương tác điện từ.","value":{"value":0.0072973525693,"unit":""},"source":"CODATA 2018"},
    {"type":"constant","name":"decay_constant","label":"hằng số phân rã λ","description":"Xác suất phân rã trên đơn vị thời gian.","value":{"value":None,"unit":"1/s"},"unit":"1/s","links":[{"target":"half_life","relation":"relates_to","note":"t½ = ln2/λ"}]},

    # ---- LAWS ----
    {"type":"law","name":"radioactive_decay_law","label":"Định luật phân rã phóng xạ","description":"N(t) = N0 e^{-λt}: số hạt nhân giảm theo hàm mũ.","links":[{"target":"decay_constant","relation":"uses"},{"target":"half_life_equation","relation":"defined_by","note":"t½ = ln2/λ"}]},
    {"type":"law","name":"energy_mass_equivalence","label":"Tương đương khối lượng–năng lượng","description":"E = mc²: khối lượng và năng lượng tương đương.","links":[{"target":"speed_of_light","relation":"uses"},{"target":"mass_energy_equation","relation":"defined_by"}]},
    {"type":"law","name":"conservation_of_energy","label":"Định luật bảo toàn năng lượng","description":"Năng lượng toàn phần bảo toàn trong hệ kín.","links":[{"target":"binding_energy_formula","relation":"relates_to"}]},
    {"type":"law","name":"coulomb_law","label":"Định luật Coulomb","description":"Lực tĩnh điện giữa hai điện tích điểm.","links":[{"target":"elementary_charge","relation":"uses"}]},

    # ---- EQUATIONS ----
    {"type":"equation","name":"mass_energy_equation","label":"E = mc²","description":"Năng lượng nghỉ tương đương khối lượng.","value":{"latex":"E = mc^2"},"links":[{"target":"speed_of_light","relation":"uses"}]},
    {"type":"equation","name":"half_life_equation","label":"Chu kỳ bán rã","description":"t½ = ln2/λ.","value":{"latex":"t_{1/2} = \\frac{\\ln 2}{\\lambda}"},"links":[{"target":"decay_constant","relation":"uses"},{"target":"half_life","relation":"derived_from"}]},
    {"type":"equation","name":"de_broglie_wavelength","label":"Bước sóng de Broglie","description":"λ = ℏ/p.","value":{"latex":"\\lambda = \\frac{\\hbar}{p}"},"links":[{"target":"reduced_planck_constant","relation":"uses"}]},
    {"type":"equation","name":"binding_energy_formula","label":"Công thức năng lượng liên kết","description":"BE = [Z·mp + N·mn − M]c².","value":{"latex":"BE = [Z m_p + N m_n - M]c^2"},"links":[{"target":"proton_mass","relation":"uses"},{"target":"neutron_mass","relation":"uses"},{"target":"speed_of_light","relation":"uses"},{"target":"mass_defect","relation":"derived_from"}]},
    {"type":"equation","name":"semi_empirical_mass_formula","label":"Công thức bán thực nghiệm Weizsäcker","description":"B = a_V A − a_S A^{2/3} − a_C Z²/A^{1/3} − a_A (N−Z)²/A + δ.","value":{"latex":"B = a_V A - a_S A^{2/3} - a_C \\frac{Z^2}{A^{1/3}} - a_A \\frac{(N-Z)^2}{A} + \\delta"},"links":[{"target":"liquid_drop_model","relation":"derived_from"},{"target":"atomic_number","relation":"uses"},{"target":"mass_number","relation":"uses"},{"target":"neutron_number","relation":"uses"}]},
    {"type":"equation","name":"schrodinger_equation","label":"Phương trình Schrödinger","description":"Ĥψ = Eψ, phương trình nền tảng cơ học lượng tử.","value":{"latex":"\\hat{H}\\psi = E\\psi"},"links":[{"target":"reduced_planck_constant","relation":"uses"}]},

    # ---- ISOTOPES ----
    {"type":"isotope","name":"U-238","label":"Uranium-238","description":"Đồng vị uranium phổ biến, phân rã alpha → Th-234.","value":{"value":{"A":238,"Z":92,"N":146}},"links":[{"target":"element_uranium","relation":"is_isotope_of"},{"target":"Th-234","relation":"decays_to","note":"phân rã alpha"}]},
    {"type":"isotope","name":"U-235","label":"Uranium-235","description":"Đồng vị uranium phân hạch được, dùng trong lò phản ứng.","value":{"value":{"A":235,"Z":92,"N":143}},"links":[{"target":"element_uranium","relation":"is_isotope_of"}]},
    {"type":"isotope","name":"Th-234","label":"Thorium-234","description":"Sản phẩm phân rã alpha của U-238.","value":{"value":{"A":234,"Z":90,"N":144}},"links":[{"target":"element_thorium","relation":"is_isotope_of"}]},
    {"type":"isotope","name":"H-1","label":"protium","description":"Đồng vị hydrogen nhẹ nhất, 1 proton.","value":{"value":{"A":1,"Z":1,"N":0}},"links":[{"target":"element_hydrogen","relation":"is_isotope_of"}]},
    {"type":"isotope","name":"H-2","label":"deuterium","description":"Hydrogen nặng, 1 proton + 1 neutron.","value":{"value":{"A":2,"Z":1,"N":1}},"links":[{"target":"element_hydrogen","relation":"is_isotope_of"},{"target":"nucleon","relation":"composed_of"}]},
    {"type":"isotope","name":"H-3","label":"tritium","description":"Hydrogen phóng xạ, 1 proton + 2 neutron.","value":{"value":{"A":3,"Z":1,"N":2}},"links":[{"target":"element_hydrogen","relation":"is_isotope_of"},{"target":"nucleon","relation":"composed_of"}]},
    {"type":"isotope","name":"He-4","label":"hạt alpha","description":"Hạt nhân helium-4, 2 proton + 2 neutron, rất bền.","value":{"value":{"A":4,"Z":2,"N":2}},"links":[{"target":"element_helium","relation":"is_isotope_of"},{"target":"nucleon","relation":"composed_of"}]},

    # ---- DEFINITIONS ----
    {"type":"definition","name":"half_life","label":"Chu kỳ bán rã","description":"Thời gian để một nửa số hạt nhân phóng xạ phân rã.","unit":"s"},
    {"type":"definition","name":"mass_defect","label":"Độ hụt khối","description":"Chênh lệch giữa tổng khối lượng nucleon tự do và khối lượng hạt nhân.","links":[{"target":"binding_energy","relation":"relates_to"}]},
    {"type":"definition","name":"binding_energy","label":"Năng lượng liên kết","description":"Năng lượng cần để tách hạt nhân thành nucleon tự do.","links":[{"target":"mass_defect","relation":"relates_to"}]},
    {"type":"definition","name":"atomic_number","label":"Số nguyên tử Z","description":"Số proton trong hạt nhân.","unit":""},
    {"type":"definition","name":"neutron_number","label":"Số neutron N","description":"Số neutron trong hạt nhân.","unit":""},
    {"type":"definition","name":"mass_number","label":"Số khối A","description":"A = Z + N, tổng số nucleon.","links":[{"target":"atomic_number","relation":"relates_to"},{"target":"neutron_number","relation":"relates_to"}]},
    {"type":"definition","name":"nucleon","label":"Nucleon","description":"Thành phần của hạt nhân: proton và neutron.","links":[{"target":"proton_mass","relation":"relates_to"},{"target":"neutron_mass","relation":"relates_to"},{"target":"strong_force","relation":"interacts_via"}]},
    {"type":"definition","name":"liquid_drop_model","label":"Mô hình giọt lỏng","description":"Mô hình vĩ mô hạt nhân, nền tảng công thức Weizsäcker.","links":[{"target":"semi_empirical_mass_formula","relation":"relates_to"}]},
    {"type":"definition","name":"strong_force","label":"Lực tương tác mạnh","description":"Lực liên kết nucleon trong hạt nhân, tầm ngắn.","unit":""},
    {"type":"definition","name":"woods_saxon","label":"Thế Woods-Saxon","description":"Thế trường trung bình hạt nhân dạng Fermi.","links":[{"target":"fm","relation":"measured_in"},{"target":"shell_model","relation":"relates_to"}]},
    {"type":"definition","name":"shell_model","label":"Mô hình lớp vỏ (Shell Model)","description":"Mô hình cấu trúc hạt nhân theo mức năng lượng đơn hạt.","links":[{"target":"schrodinger_equation","relation":"uses"},{"target":"woods_saxon","relation":"uses"}]},
    {"type":"definition","name":"initial_quantity","label":"Số hạt ban đầu N0","description":"Số hạt nhân tại thời điểm t=0.","unit":""},

    # ---- ELEMENTS (cho is_isotope_of) ----
    {"type":"definition","name":"element_uranium","label":"Uranium (U)","description":"Nguyên tố Z=92, nhiên liệu hạt nhân chính."},
    {"type":"definition","name":"element_thorium","label":"Thorium (Th)","description":"Nguyên tố Z=90."},
    {"type":"definition","name":"element_hydrogen","label":"Hydrogen (H)","description":"Nguyên tố Z=1, nhẹ nhất."},
    {"type":"definition","name":"element_helium","label":"Helium (He)","description":"Nguyên tố Z=2."},
]


def connect():
    conn = sqlite3.connect(KB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def find_by_name(conn, name):
    cur = conn.execute("SELECT id FROM facts WHERE name = ?", (name,))
    r = cur.fetchone()
    return r[0] if r else None


def add_edge(conn, src, tgt, relation, weight=1.0, note=""):
    if src is None or tgt is None or src == tgt:
        return False
    try:
        conn.execute(
            "INSERT OR IGNORE INTO fact_edges(source_id, target_id, relation, weight, note) VALUES (?,?,?,?,?)",
            (src, tgt, relation, weight, note or None))
        return True
    except Exception:
        return False


def auto_link(conn, fid, fact):
    """Rule-based auto-link Lớp 1: measured_in + uses (symbol map) + is_isotope_of."""
    created = 0
    umap = {"kg":"kg","MeV":"MeV","MeV/c²":"MeV/c2","MeV·s":"MeV","m/s":"m_per_s",
            "1/s":"per_second","C":"coulomb","barn":"barn","fm":"fm","u":"u","s":"second","MeV/c2":"MeV/c2"}
    # 1) measured_in: fact.unit -> unit fact
    if fact.get("unit") and fact["type"] != "unit":
        uname = umap.get(fact["unit"])
        if uname:
            uid = find_by_name(conn, uname)
            if uid and add_edge(conn, fid, uid, "measured_in", 1.0, f"đo bằng {fact['unit']}"):
                created += 1

    # 2) uses: quét description + latex tìm SYMBOL_MAP
    if fact["type"] in ("equation", "law", "definition"):
        text = json.dumps(str(fact.get("value", "")) + " " + str(fact.get("description", "")), ensure_ascii=False)
        seen = set()
        for pattern, target, rel in SYMBOL_MAP:
            if re.search(pattern, text):
                tid = find_by_name(conn, target)
                if tid and tid not in seen:
                    seen.add(tid)
                    if add_edge(conn, fid, tid, rel, 1.0, f"chứa {target}"):
                        created += 1

    # 3) is_isotope_of: parse element từ name
    if fact["type"] == "isotope":
        m = re.match(r"^([A-Z][a-z]?)-", fact["name"])
        if m and m.group(1) in ELEMENT_SYMBOL:
            eid = find_by_name(conn, ELEMENT_SYMBOL[m.group(1)])
            if eid and add_edge(conn, fid, eid, "is_isotope_of", 1.0, "thuộc nguyên tố"):
                created += 1
    return created


def ingest_facts(conn, facts):
    inserted, total_edges = 0, 0
    # Pha 1: insert tất cả facts (tránh forward-reference khi tạo link)
    for f in facts:
        name = f["name"]
        if find_by_name(conn, name):
            continue  # idempotent: đã có
        value_json = json.dumps(f.get("value", None), ensure_ascii=False) if f.get("value") is not None else None
        conn.execute(
            """INSERT INTO facts(type, name, label, description, value_json, unit, source, tags)
               VALUES (?,?,?,?,?,?,?,?)""",
            (f["type"], name, f.get("label", name), f.get("description", ""),
             value_json, f.get("unit"), f.get("source"), f.get("tags")))
        inserted += 1
    # Pha 2: tạo edges cho TẤT CẢ facts (mọi fact đã tồn tại; idempotent nhờ UNIQUE)
    for f in facts:
        fid = find_by_name(conn, f["name"])
        if not fid:
            continue
        total_edges += auto_link(conn, fid, f)
        for link in f.get("links", []):
            tid = find_by_name(conn, link["target"])
            if tid and add_edge(conn, fid, tid, link["relation"], link.get("weight", 1.0), link.get("note")):
                total_edges += 1
    conn.commit()
    return inserted, total_edges


def main():
    conn = connect()
    init_schema(conn)
    inserted, edges = ingest_facts(conn, SEED)
    nf = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    ne = conn.execute("SELECT COUNT(*) FROM fact_edges").fetchone()[0]
    bytype = conn.execute("SELECT type, COUNT(*) FROM facts GROUP BY type").fetchall()
    byrel = conn.execute("SELECT relation, COUNT(*) FROM fact_edges GROUP BY relation").fetchall()
    print("=== CORE KB xây xong ===")
    print(f"facts: {nf} (mới insert: {inserted}) | edges: {ne} (mới: {edges})")
    print("theo type:", dict(bytype))
    print("theo relation:", dict(byrel))
    conn.close()


if __name__ == "__main__":
    main()
