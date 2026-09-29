"""
Demo mô phỏng vật lý: Thế quang học Woods-Saxon cho tán xạ neutron-hạt nhân.
Tham số: V0 (độ sâu thực), W0 (độ sâu ảo), r0 (bán kính), L (độ mờ).

U(r) = -V0 / (1 + exp((r - R)/L))
R = r0 * A^(1/3)

Output CSV (key,value): U_center, U_surface, radius...
"""
import sys, json, math

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.csv"

    with open(input_file, "r", encoding="utf-8") as f:
        p = json.load(f)

    V0 = p.get("V0", 50.0)
    W0 = p.get("W0", 10.0)
    r0 = p.get("r0", 1.25)
    L  = p.get("L", 0.65)
    A  = p.get("A", 56)

    R = r0 * (A ** (1.0/3.0))
    def U(r):
        return -V0 / (1.0 + math.exp((r - R) / L))

    U_center = U(0.0)        # ~ -V0
    U_surface = U(R)         # = -V0/2
    U_tail = U(R + 3*L)      # gần 0

    rows = [
        ("V0", V0), ("W0", W0), ("r0", r0), ("L", L),
        ("radius", round(R, 4)),
        ("U_center", round(U_center, 4)),
        ("U_surface", round(U_surface, 4)),
        ("U_tail", round(U_tail, 4)),
    ]
    with open(output_file, "w", encoding="utf-8") as f:
        for k, v in rows:
            f.write(f"{k},{v}\n")
    print(f"[demo] R={R:.3f} fm | U_center={U_center:.2f} | U_surface={U_surface:.2f} MeV")

if __name__ == "__main__":
    main()
