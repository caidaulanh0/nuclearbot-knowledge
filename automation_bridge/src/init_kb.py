import sqlite3

def init_db():
    conn = sqlite3.connect('core_kb.db')
    cursor = conn.cursor()
    
    # Xóa bảng cũ nếu tồn tại để chạy lại dễ dàng
    cursor.execute('DROP TABLE IF EXISTS constants')
    
    cursor.execute('''
        CREATE TABLE constants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity TEXT NOT NULL,
            property TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            uncertainty REAL,
            source TEXT
        )
    ''')
    
    # Dữ liệu mẫu (CODATA 2018)
    constants = [
        ("neutron", "mass", 1.67492749804e-27, "kg", 9.5e-38, "CODATA 2018"),
        ("proton", "mass", 1.67262192369e-27, "kg", 5.1e-38, "CODATA 2018"),
        ("electron", "rest_energy", 0.51099895000, "MeV", 1.5e-10, "CODATA 2018")
    ]
    
    cursor.executemany('''
        INSERT INTO constants (entity, property, value, unit, uncertainty, source)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', constants)
    
    conn.commit()
    conn.close()
    print("Database core_kb.db created and populated successfully.")

if __name__ == "__main__":
    init_db()
