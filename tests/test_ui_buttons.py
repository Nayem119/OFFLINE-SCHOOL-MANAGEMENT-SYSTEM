import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tkinter as tk
from tkinter import ttk

import database.db as database
from ui.classes import ClassesFrame
from ui.staff import PersonFrame as StaffFrame
from ui.teachers import PersonFrame as TeacherFrame


class ButtonSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp_dir.name) / "school.db"
        database.init_db()
        self.root = tk.Tk()
        self.root.withdraw()
        self.user = {"username": "admin", "role": "Admin"}
        self.messages = patch.multiple(
            "tkinter.messagebox",
            showinfo=lambda *args, **kwargs: None,
            showwarning=lambda *args, **kwargs: None,
            showerror=lambda *args, **kwargs: None,
            askyesno=lambda *args, **kwargs: True,
        )
        self.messages.start()

    def tearDown(self):
        self.messages.stop()
        self.root.destroy()
        self.temp_dir.cleanup()

    @staticmethod
    def button(frame, text):
        for widget in frame.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)) and widget.cget("text") == text:
                return widget
            found = ButtonSmokeTests.find_button(widget, text)
            if found:
                return found
        raise AssertionError(f"Button not found: {text}")

    @staticmethod
    def find_button(widget, text):
        for child in widget.winfo_children():
            if isinstance(child, (tk.Button, ttk.Button)) and child.cget("text") == text:
                return child
            found = ButtonSmokeTests.find_button(child, text)
            if found:
                return found
        return None

    def exercise_person_buttons(self, frame_class, identifier, name):
        frame = frame_class(self.root, self.user)
        frame.vars["teacher_id" if "Teacher ID" in [field[0] for field in frame.fields] else "staff_id"].set(identifier)
        frame.vars["name"].set(name)
        popup_module = "ui.teachers" if frame_class is TeacherFrame else "ui.staff"
        class FakePopup:
            def __init__(self, _parent, _title, _fields, values=None, on_save=None):
                current = values or {key: variable.get() for key, variable in frame.vars.items()}
                on_save(current)
        with patch(f"{popup_module}.PopupForm", FakePopup):
            self.button(frame, "➕ Add Teacher" if frame_class is TeacherFrame else "➕ Add Staff").invoke()
        self.assertEqual(len(frame.tree.get_children()), 1)
        frame.selected_id = database.query("SELECT id FROM " + ("teachers" if frame_class is TeacherFrame else "staff") + " WHERE name=?", (name,))[0][0]
        frame.vars["name"].set(name + " Updated")
        with patch(f"{popup_module}.PopupForm", FakePopup):
            self.button(frame, "✏️ Edit Teacher" if frame_class is TeacherFrame else "✏️ Edit Staff").invoke()
        self.assertIn("Updated", str(frame.tree.item(frame.tree.get_children()[0])["values"]))
        self.button(frame, "🗑 Delete").invoke()
        self.assertEqual(len(frame.tree.get_children()), 0)
        frame.destroy()

    def test_teacher_and_staff_buttons(self):
        self.exercise_person_buttons(TeacherFrame, "T-UI", "UI Teacher")
        self.exercise_person_buttons(StaffFrame, "ST-UI", "UI Staff")

    def test_class_buttons(self):
        frame = ClassesFrame(self.root, self.user)
        frame.name.set("UI Class")
        self.button(frame, "➕ Add").invoke()
        self.assertEqual(len(frame.tree.get_children()), 2)
        item = [item for item in frame.tree.get_children() if frame.tree.item(item)["values"][1] == "UI Class"][0]
        frame.selected_class = frame.tree.item(item)["values"][0]
        frame.name.set("UI Class Updated")
        self.button(frame, "✏️ Update").invoke()
        self.assertTrue(any(frame.tree.item(item)["values"][1] == "UI Class Updated" for item in frame.tree.get_children()))
        self.button(frame, "🗑 Remove").invoke()
        self.assertFalse(frame.tree.exists(item))
        frame.destroy()


if __name__ == "__main__":
    unittest.main()
