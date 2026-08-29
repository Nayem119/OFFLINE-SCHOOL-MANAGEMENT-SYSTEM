import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "Offline School Management System"

# Installed applications should not write user data beside the executable in
# Program Files. Source runs keep the existing project-local data layout.
if getattr(sys, "frozen", False):
    DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME
else:
    DATA_DIR = BASE_DIR

DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "school_management.db"
BACKUP_DIR = DATA_DIR / "backups"
STUDENT_PHOTO_DIR = DATA_DIR / "photos" / "students"

APP_VERSION = "1.0.1"
DEVELOPER = "Nayem Ahammad"

DB_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)
STUDENT_PHOTO_DIR.mkdir(parents=True, exist_ok=True)
