# modules/database.py
import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = 'cyberscan.db'


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TEXT,
            targets TEXT,
            total_hosts INTEGER,
            total_ports INTEGER,
            max_risk REAL,
            avg_risk REAL,
            results_json TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_scan(df: pd.DataFrame, targets=None):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        '''INSERT INTO scans 
           (scan_time, targets, total_hosts, total_ports, max_risk, avg_risk, results_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ', '.join(targets) if targets else '',
            int(df['ip'].nunique()),
            len(df),
            float(df['risk_score'].max()),
            float(df['risk_score'].mean()),
            df.to_json(orient='records')
        )
    )

    conn.commit()
    conn.close()


def load_history():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query(
        '''SELECT id, scan_time, targets, total_hosts, total_ports, max_risk, avg_risk
           FROM scans ORDER BY id DESC''',
        conn
    )

    conn.close()
    return df


def load_scan_by_id(scan_id):
    conn = sqlite3.connect(DB_FILE)

    row = conn.execute(
        'SELECT results_json FROM scans WHERE id = ?',
        (scan_id,)
    ).fetchone()

    conn.close()

    if row:
        return pd.read_json(row[0])
    return pd.DataFrame()


# auto-create DB
init_db()