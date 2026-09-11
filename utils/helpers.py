from datetime import datetime
import sqlite3
from config import DB_PATH, BACKUP_DIR
from database.db import execute

def today():
    return datetime.now().strftime("%Y-%m-%d")

def backup_database():
    if not DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKUP_DIR / f"school_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    source = sqlite3.connect(DB_PATH)
    target = sqlite3.connect(path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    backups = sorted(BACKUP_DIR.glob("school_backup_*.db"), reverse=True)
    for old_backup in backups[10:]:
        old_backup.unlink(missing_ok=True)
    execute("INSERT INTO backup_history(action,file_path) VALUES(?,?)", ("Automatic backup", str(path)))
    return path
