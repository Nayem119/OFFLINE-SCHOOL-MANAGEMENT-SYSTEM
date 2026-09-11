import sqlite3
from contextlib import contextmanager
from config import DB_PATH
from utils.auth import hash_password

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Staff',
    full_name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    module TEXT NOT NULL,
    can_view INTEGER NOT NULL DEFAULT 1,
    can_add INTEGER NOT NULL DEFAULT 1,
    can_edit INTEGER NOT NULL DEFAULT 1,
    can_delete INTEGER NOT NULL DEFAULT 0,
    UNIQUE(role, module)
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    school_name TEXT NOT NULL DEFAULT 'আমাদের স্কুল',
    school_address TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    logo_path TEXT NOT NULL DEFAULT '',
    signature_path TEXT NOT NULL DEFAULT '',
    academic_year TEXT NOT NULL DEFAULT '2026',
    language TEXT NOT NULL DEFAULT 'বাংলা',
    theme TEXT NOT NULL DEFAULT 'Light'
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS backup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL DEFAULT 'A',
    class_teacher TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_name, section)
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    gender TEXT DEFAULT '',
    date_of_birth TEXT DEFAULT '',
    father_name TEXT DEFAULT '',
    mother_name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    guardian_phone TEXT DEFAULT '',
    emergency_contact TEXT DEFAULT '',
    blood_group TEXT DEFAULT '',
    academic_year TEXT DEFAULT '',
    address TEXT DEFAULT '',
    class_name TEXT DEFAULT '',
    section TEXT DEFAULT '',
    roll TEXT DEFAULT '',
    admission_date TEXT DEFAULT '',
    status TEXT DEFAULT 'Active',
    photo_path TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    record_json TEXT NOT NULL,
    archived_by TEXT NOT NULL,
    archived_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS promotion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    from_class TEXT NOT NULL DEFAULT '',
    from_section TEXT NOT NULL DEFAULT '',
    to_class TEXT NOT NULL,
    to_section TEXT NOT NULL DEFAULT '',
    promoted_by TEXT NOT NULL,
    promoted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    subject TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    joining_date TEXT DEFAULT '',
    designation TEXT DEFAULT 'Teacher',
    salary REAL DEFAULT 0,
    status TEXT DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    designation TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    joining_date TEXT DEFAULT '',
    salary REAL DEFAULT 0,
    status TEXT DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_type TEXT NOT NULL,
    person_id TEXT NOT NULL,
    person_name TEXT NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Present',
    note TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(person_type, person_id, attendance_date)
);


CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL,
    full_marks REAL NOT NULL DEFAULT 100,
    pass_marks REAL NOT NULL DEFAULT 33,
    class_name TEXT NOT NULL DEFAULT '',
    section TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT NOT NULL,
    exam_type TEXT NOT NULL,
    class_name TEXT NOT NULL,
    section TEXT DEFAULT '',
    exam_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    marks REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exam_id, student_id, subject_id),
    FOREIGN KEY(exam_id) REFERENCES exams(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS fee_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fee_name TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    frequency TEXT NOT NULL DEFAULT 'Monthly',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    fee_name TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Due',
    note TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fee_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_no TEXT UNIQUE NOT NULL,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    discount REAL NOT NULL DEFAULT 0,
    fee_type TEXT NOT NULL DEFAULT 'Other',
    payment_method TEXT NOT NULL DEFAULT 'Cash',
    note TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def _columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        # Upgrade databases created by Phase 1.
        if "active" not in _columns(conn, "users"):
            conn.execute("ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
        if "photo_path" not in _columns(conn, "students"):
            conn.execute("ALTER TABLE students ADD COLUMN photo_path TEXT DEFAULT ''")
        if "discount" not in _columns(conn, "fee_payments"):
            conn.execute("ALTER TABLE fee_payments ADD COLUMN discount REAL NOT NULL DEFAULT 0")
        if "payment_method" not in _columns(conn, "fee_payments"):
            conn.execute("ALTER TABLE fee_payments ADD COLUMN payment_method TEXT NOT NULL DEFAULT 'Cash'")
        if "logo_path" not in _columns(conn, "settings"):
            conn.execute("ALTER TABLE settings ADD COLUMN logo_path TEXT NOT NULL DEFAULT ''")
        if "signature_path" not in _columns(conn, "settings"):
            conn.execute("ALTER TABLE settings ADD COLUMN signature_path TEXT NOT NULL DEFAULT ''")
        if "class_name" not in _columns(conn, "subjects"):
            conn.execute("ALTER TABLE subjects ADD COLUMN class_name TEXT NOT NULL DEFAULT ''")
        if "section" not in _columns(conn, "subjects"):
            conn.execute("ALTER TABLE subjects ADD COLUMN section TEXT NOT NULL DEFAULT ''")
        for column in ["guardian_phone", "emergency_contact", "blood_group", "academic_year"]:
            if column not in _columns(conn, "students"):
                conn.execute(f"ALTER TABLE students ADD COLUMN {column} TEXT DEFAULT ''")
        if "theme" not in _columns(conn, "settings"):
            conn.execute("ALTER TABLE settings ADD COLUMN theme TEXT NOT NULL DEFAULT 'Light'")
        conn.execute(
            "INSERT OR IGNORE INTO users (username,password,role,full_name,active) VALUES (?,?,?,?,1)",
            ("admin", hash_password("admin123"), "Admin", "Administrator")
        )
        modules=["Dashboard","Students","Teachers","Staff","Attendance","Classes","Fees","Exams","Reports","Certificates","IDCards","Users","Permissions","Logs","Settings"]
        for module in modules:
            conn.execute("INSERT OR IGNORE INTO permissions(role,module,can_view,can_add,can_edit,can_delete) VALUES(?,?,?,?,?,?)",("Admin",module,1,1,1,1))
            conn.execute("INSERT OR IGNORE INTO permissions(role,module,can_view,can_add,can_edit,can_delete) VALUES(?,?,?,?,?,?)",("Staff",module,0 if module in ("Users","Permissions","Logs") else 1,1,1,0))
        conn.execute(
            "INSERT OR IGNORE INTO settings (id,school_name,academic_year,language) VALUES (1,?,?,?)",
            ("আমাদের স্কুল", "2026", "বাংলা")
        )
        conn.execute(
            "INSERT OR IGNORE INTO classes (class_name,section) VALUES (?,?)",
            ("Class 1", "A")
        )
        for fee_name, amount, frequency in [
            ("Monthly Fee", 0, "Monthly"),
            ("Admission Fee", 0, "One Time"),
            ("Exam Fee", 0, "Per Exam"),
            ("Other Fee", 0, "Other"),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO fee_settings (fee_name, amount, frequency) VALUES (?,?,?)",
                (fee_name, amount, frequency)
            )
        conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_students_lookup ON students(student_id, name, class_name, phone);
        CREATE INDEX IF NOT EXISTS idx_attendance_date_person ON attendance(attendance_date, person_type, person_id);
        CREATE INDEX IF NOT EXISTS idx_fee_payments_date_student ON fee_payments(payment_date, student_id);
        CREATE INDEX IF NOT EXISTS idx_student_fees_due ON student_fees(status, due_date, student_id);
        CREATE INDEX IF NOT EXISTS idx_marks_exam_student ON marks(exam_id, student_id);
        CREATE INDEX IF NOT EXISTS idx_activity_logs_recent ON activity_logs(id DESC);
        """)

def query(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()

def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.lastrowid

def log_activity(username, action):
    execute("INSERT INTO activity_logs (username,action) VALUES (?,?)", (username, action))
