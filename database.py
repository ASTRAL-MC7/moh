import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "bot.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            first_name  TEXT,
            joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS referrals (
            referrer_id INTEGER,
            referee_id  INTEGER,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (referrer_id, referee_id)
        );

        CREATE TABLE IF NOT EXISTS join_requests (
            user_id    INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS gifts (
            user_id      INTEGER PRIMARY KEY,
            received_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS gift_notified (
            user_id     INTEGER PRIMARY KEY,
            notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, first_name: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)",
        (user_id, first_name)
    )
    conn.commit()
    conn.close()

def get_total_users() -> int:
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    conn.close()
    return row[0]

def get_all_user_ids() -> list[int]:
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r[0] for r in rows]

def referral_exists(referrer_id: int, referee_id: int) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM referrals WHERE referrer_id=? AND referee_id=?",
        (referrer_id, referee_id)
    ).fetchone()
    conn.close()
    return row is not None

def add_referral(referrer_id: int, referee_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO referrals (referrer_id, referee_id) VALUES (?, ?)",
        (referrer_id, referee_id)
    )
    conn.commit()
    conn.close()

def get_referral_count(user_id: int) -> int:
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row[0]

def save_join_request(user_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO join_requests (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()

def has_join_request(user_id: int) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM join_requests WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row is not None

def gift_received(user_id: int) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM gifts WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row is not None

def mark_gift_received(user_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO gifts (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()

def gift_already_notified(user_id: int) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM gift_notified WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row is not None

def set_gift_notified(user_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO gift_notified (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()
