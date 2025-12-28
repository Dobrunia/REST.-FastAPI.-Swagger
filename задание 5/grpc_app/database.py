import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "glossary.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE NOT NULL,
            definition TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def get_all_terms() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM terms ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_term_by_name(term_name: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM terms WHERE term = ?", (term_name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_term(term_name: str, definition: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO terms (term, definition) VALUES (?, ?)",
            (term_name, definition)
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return get_term_by_id(last_id)
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_term_by_id(term_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM terms WHERE id = ?", (term_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_term(term_name: str, new_definition: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE terms SET definition = ?, updated_at = datetime('now') WHERE term = ?",
        (new_definition, term_name)
    )
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    if changes == 0:
        return None
    return get_term_by_name(term_name)


def delete_term(term_name: str) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM terms WHERE term = ?", (term_name,))
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    return changes > 0


# Initialize database on module import
init_db()

