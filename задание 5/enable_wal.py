"""Enable WAL mode for SQLite databases."""
import sqlite3
from pathlib import Path

# Enable WAL for both databases
databases = [
    Path(__file__).parent / "rest_app" / "app" / "db" / "glossary.db",
    Path(__file__).parent / "grpc_app" / "glossary.db"
]

for DB_PATH in databases:
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH), timeout=60.0)
        # Enable WAL and optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=60000")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA wal_autocheckpoint=1000")
        conn.commit()
        
        # Verify WAL is enabled
        result = conn.execute("PRAGMA journal_mode").fetchone()
        conn.close()
        print(f"[OK] WAL mode enabled for {DB_PATH.name}: {result[0]}")
    else:
        print(f"[WARN] Database not found: {DB_PATH}")

