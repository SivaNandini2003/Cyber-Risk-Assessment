import sqlite3

def init_db():
    conn = sqlite3.connect("cyberscan.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_time TEXT,
        total_hosts INTEGER,
        total_ports INTEGER,
        max_risk REAL
    )
    """)
    conn.commit()
    conn.close()

def save_scan(df):
    conn = sqlite3.connect("cyberscan.db")

    conn.execute(
        "INSERT INTO scans (scan_time, total_hosts, total_ports, max_risk) VALUES (?, ?, ?, ?)",
        (
            str(df.shape[0]),
            df["ip"].nunique(),
            len(df),
            float(df["risk_score"].max())
        )
    )

    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect("cyberscan.db")
    data = conn.execute("SELECT * FROM scans").fetchall()
    conn.close()
    return data