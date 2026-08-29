import json
import tempfile
import unittest
from pathlib import Path

import database.db as database


class CrudWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp_dir.name) / "school.db"
        database.init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_class_subject_exam_update_and_remove(self):
        class_id = database.execute("INSERT INTO classes(class_name,section) VALUES(?,?)", ("Class X", "A"))
        database.execute("UPDATE classes SET class_name=? WHERE id=?", ("Class XI", class_id))
        self.assertEqual(database.query("SELECT class_name FROM classes WHERE id=?", (class_id,))[0][0], "Class XI")
        subject_id = database.execute("INSERT INTO subjects(subject_code,subject_name,full_marks,pass_marks,class_name,section) VALUES(?,?,?,?,?,?)", ("ENG", "English", 100, 33, "Class XI", "A"))
        database.execute("UPDATE subjects SET subject_name=? WHERE id=?", ("Advanced English", subject_id))
        self.assertEqual(database.query("SELECT subject_name FROM subjects WHERE id=?", (subject_id,))[0][0], "Advanced English")
        exam_id = database.execute("INSERT INTO exams(exam_name,exam_type,class_name,section,exam_date) VALUES(?,?,?,?,?)", ("Final", "Final", "Class XI", "A", "2026-12-01"))
        database.execute("UPDATE exams SET exam_name=? WHERE id=?", ("Final Updated", exam_id))
        database.execute("DELETE FROM exams WHERE id=?", (exam_id,))
        database.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        database.execute("DELETE FROM classes WHERE id=?", (class_id,))
        self.assertFalse(database.query("SELECT id FROM exams WHERE id=?", (exam_id,)))
        self.assertFalse(database.query("SELECT id FROM subjects WHERE id=?", (subject_id,)))
        self.assertFalse(database.query("SELECT id FROM classes WHERE id=?", (class_id,)))

    def test_student_archive_and_restore(self):
        student_id = database.execute("INSERT INTO students(student_id,name,class_name,section) VALUES(?,?,?,?)", ("S-1", "Test Student", "Class 1", "A"))
        record = dict(database.query("SELECT * FROM students WHERE id=?", (student_id,))[0])
        database.execute("INSERT INTO student_archive(student_id,record_json,archived_by) VALUES(?,?,?)", ("S-1", json.dumps(record), "admin"))
        database.execute("DELETE FROM students WHERE id=?", (student_id,))
        archived = database.query("SELECT record_json FROM student_archive WHERE student_id=?", ("S-1",))[0]
        restored = json.loads(archived[0]);restored.pop("id", None);restored.pop("created_at", None)
        columns=list(restored);values=[restored[column] for column in columns]
        database.execute(f"INSERT INTO students ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", values)
        self.assertEqual(database.query("SELECT name FROM students WHERE student_id=?", ("S-1",))[0][0], "Test Student")

    def test_people_attendance_due_user_and_marks_remove(self):
        teacher_id = database.execute("INSERT INTO teachers(teacher_id,name) VALUES(?,?)", ("T-1", "Teacher"))
        staff_id = database.execute("INSERT INTO staff(staff_id,name) VALUES(?,?)", ("ST-1", "Staff"))
        database.execute("UPDATE teachers SET name=? WHERE id=?", ("Updated Teacher", teacher_id))
        database.execute("UPDATE staff SET name=? WHERE id=?", ("Updated Staff", staff_id))
        database.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        database.execute("DELETE FROM staff WHERE id=?", (staff_id,))
        database.execute("INSERT INTO attendance(person_type,person_id,person_name,attendance_date,status) VALUES(?,?,?,?,?)", ("Student", "S-2", "Student", "2026-08-26", "Present"))
        database.execute("UPDATE attendance SET status=? WHERE person_id=?", ("Absent", "S-2"))
        database.execute("DELETE FROM attendance WHERE person_id=?", ("S-2",))
        due_id = database.execute("INSERT INTO student_fees(student_id,fee_name,amount,due_date) VALUES(?,?,?,?)", ("S-2", "Monthly Fee", 500, "2026-08-01"))
        database.execute("UPDATE student_fees SET amount=? WHERE id=?", (300, due_id))
        database.execute("DELETE FROM student_fees WHERE id=?", (due_id,))
        exam_id = database.execute("INSERT INTO exams(exam_name,exam_type,class_name,exam_date) VALUES(?,?,?,?)", ("Test", "Test", "Class 1", "2026-08-26"))
        subject_id = database.execute("INSERT INTO subjects(subject_code,subject_name) VALUES(?,?)", ("MATH", "Math"))
        mark_id = database.execute("INSERT INTO marks(exam_id,student_id,subject_id,marks) VALUES(?,?,?,?)", (exam_id, "S-2", subject_id, 60))
        database.execute("UPDATE marks SET marks=? WHERE id=?", (75, mark_id))
        database.execute("DELETE FROM marks WHERE id=?", (mark_id,))
        user_id = database.execute("INSERT INTO users(username,password,full_name) VALUES(?,?,?)", ("test", "hash", "Test User"))
        database.execute("UPDATE users SET full_name=? WHERE id=?", ("Updated User", user_id))
        database.execute("UPDATE users SET active=0 WHERE id=?", (user_id,))
        self.assertEqual(database.query("SELECT active FROM users WHERE id=?", (user_id,))[0][0], 0)
        self.assertFalse(database.query("SELECT id FROM teachers WHERE id=?", (teacher_id,)))
        self.assertFalse(database.query("SELECT id FROM staff WHERE id=?", (staff_id,)))
        self.assertFalse(database.query("SELECT id FROM attendance WHERE person_id=?", ("S-2",)))
        self.assertFalse(database.query("SELECT id FROM student_fees WHERE id=?", (due_id,)))
        self.assertFalse(database.query("SELECT id FROM marks WHERE id=?", (mark_id,)))


if __name__ == "__main__":
    unittest.main()
