# feedback_db.py
import os, sqlite3, threading
from datetime import datetime
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "feedback.db")
_lock = threading.Lock()
 
def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn
 
def init_db():
    with _lock:
        conn = _get_conn()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                result_id TEXT,
                source TEXT,
                feedback TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
 
def store_feedback(query_text, result_id, source, feedback):
    with _lock:
        conn = _get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO feedback (query_text, result_id, source, feedback, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (query_text, result_id, source, feedback, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
 
def get_all_feedback(limit=100):
    with _lock:
        conn = _get_conn()
        c = conn.cursor()
        c.execute("SELECT id, query_text, result_id, source, feedback, created_at FROM feedback ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return rows
 
# init DB on import
init_db()