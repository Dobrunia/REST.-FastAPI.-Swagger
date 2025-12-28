from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# SQLite with WAL mode for better concurrency
DATABASE_URL = f"sqlite:///{BASE_DIR}/db/glossary.db?check_same_thread=False"

API_TITLE = "Glossary REST API"
API_DESCRIPTION = "REST API for glossary terms"
API_VERSION = "1.0.0"

