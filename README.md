# 🏫 Offline School Management System

> একটি আধুনিক, শক্তিশালী এবং সম্পূর্ণ **Offline School Management Desktop Application**, যা স্কুলের শিক্ষার্থী, শিক্ষক, কর্মচারী, উপস্থিতি, ফি, পরীক্ষা, ফলাফল, রিপোর্ট এবং ডেটা ম্যানেজমেন্ট সহজ করার জন্য তৈরি করা হয়েছে।

---

## 🚀 Project Overview

**Offline School Management System** হলো একটি Python-based Desktop Application যা সম্পূর্ণভাবে **Offline Mode**-এ কাজ করার জন্য ডিজাইন করা হয়েছে।

এই সফটওয়্যারের মাধ্যমে একটি স্কুলের দৈনন্দিন প্রশাসনিক ও একাডেমিক কার্যক্রম একটি কেন্দ্রীয় সিস্টেম থেকে পরিচালনা করা যাবে।

### ✨ মূল বৈশিষ্ট্য

- 🖥️ সম্পূর্ণ Offline Desktop Application
- 🇧🇩 বাংলা-বান্ধব Interface
- 👨‍🎓 Student Management
- 👨‍🏫 Teacher Management
- 👨‍💼 Staff Management
- 📅 Attendance Management
- 💰 Fees & Payment Management
- 📝 Examination Management
- 🎓 Result & GPA Calculation
- 📊 Reports & Analytics
- 📄 CSV / Excel Export
- 🖨️ Print-ready Reports
- 💾 SQLite Database
- 🔐 User Management
- 💾 Database Backup & Restore
- 🎓 Certificate Generation

---

# 🛠️ Technology Stack

| Technology | Usage |
|---|---|
| 🐍 Python | Main Programming Language |
| 🖼️ Tkinter | Desktop User Interface |
| 🗄️ SQLite | Offline Database |
| 📊 OpenPyXL | Excel Export |
| 📄 CSV | Data Export |
| 🖨️ Tkinter Print View | Print-ready Reports |
| 💾 PyInstaller | EXE Build |
| 📦 Inno Setup | Windows Installer |

---

# 📁 Project Structure

```text
Offline_School_Management_System/
│
├── main.py
├── app.py
├── README.md
├── LICENSE
│
├── database/
│   ├── db.py
│   └── school.db
│
├── ui/
│   ├── login.py
│   ├── dashboard.py
│   ├── students.py
│   ├── teachers.py
│   ├── staff.py
│   ├── attendance.py
│   ├── classes.py
│   ├── users.py
│   ├── fees.py
│   ├── exams.py
│   ├── reports.py
│   ├── certificates.py
│   └── settings.py
│
├── utils/
│   └── helpers.py
│
├── assets/
│   ├── icon.ico
│   ├── logo.png
│   │
│   ├── icons/
│   │
│   └── images/
│
└── backups/
```

---

# 🚀 Phase 1 — Core Foundation System

Phase 1-এ সফটওয়্যারের মূল ভিত্তি তৈরি করা হয়েছে।

## 🔐 Authentication System

- Admin Login
- Username & Password
- User Authentication
- Secure Login Validation
- Logout System

## 👨‍🎓 Student Management

- Student Add
- Student View
- Student Search
- Student Information
- Student ID
- Class
- Section
- Roll Number
- Phone Number
- Address

## 🏫 School Settings

- School Name
- School Address
- Phone Number
- School Information

## 🗄️ Database

- SQLite Database
- Offline Data Storage
- Automatic Database Initialization

## 📊 Basic Dashboard

- Total Students
- Basic School Statistics
- Quick Navigation

---

# 🚀 Phase 2 — School Academic & Staff Management

Phase 2-এ Student Management আরও উন্নত করা হয়েছে এবং Teacher, Staff ও Attendance System যুক্ত করা হয়েছে।

---

## 👨‍🎓 Advanced Student Management

- Student Add
- Student Edit
- Student Delete
- Student Search
- Student Photo
- Student Information Update
- Class & Section Management

---

## 👨‍🏫 Teacher Management

- Teacher Add
- Teacher Edit
- Teacher Delete
- Teacher ID
- Teacher Name
- Subject
- Phone
- Email
- Teacher Information

---

## 👨‍💼 Staff Management

- Staff Add
- Staff Edit
- Staff Delete
- Staff ID
- Designation
- Phone
- Email
- Staff Information

---

## 📅 Attendance Management

Attendance System:

- 👨‍🎓 Student Attendance
- 👨‍🏫 Teacher Attendance
- 👨‍💼 Staff Attendance

Attendance Status:

- Present
- Absent
- Late
- Leave

---

## 📚 Class & Section Management

- Class Creation
- Section Management
- Student Class Assignment

---

## 👤 Better User Management

- User Create
- User Edit
- User Activate / Deactivate
- Username Management
- Role Management

---

# 🚀 Phase 3 — Fees & Payment System

Phase 3-এ সম্পূর্ণ Financial Management System যুক্ত করা হয়েছে।

---

## 💰 Fee Management

সমর্থিত Fee Types:

- Monthly Fee
- Admission Fee
- Exam Fee
- Other Fee

---

## ⚙️ Fee Settings

Admin পরিবর্তন করতে পারবেন:

- Fee Name
- Fee Amount
- Fee Frequency
- Fee Status

---

## 📌 Student-wise Due

প্রতিটি Student-এর জন্য:

- Due Amount
- Fee Type
- Due Date
- Due Status
- Due History

---

## 💳 Payment Collection

- Student Payment
- Fee Type Selection
- Payment Amount
- Payment Date
- Notes

---

## 🧾 Money Receipt

Automatic Receipt তৈরি হবে:

```text
================================================
               SCHOOL NAME

               MONEY RECEIPT
================================================

Receipt No : R-XXXXXXXX
Date       : YYYY-MM-DD

Student ID : ST-XXXX
Student    : Student Name

Fee Type   : Monthly Fee
Amount     : 0000.00

================================================
```

---

## 📜 Payment History

- Receipt Number
- Student ID
- Student Name
- Payment Date
- Fee Type
- Payment Amount

---

## 📊 Financial Reports

- Daily Collection
- Monthly Collection
- Payment History
- Student-wise Due
- Outstanding Fees

---

# 🚀 Phase 4 — Examination & Result Management

Phase 4-এ সম্পূর্ণ Examination ও Result Management System যুক্ত করা হয়েছে।

---

## 📝 Exam Management

- Create Exam
- Exam Name
- Exam Type
- Class
- Section
- Exam Date

---

## 📚 Exam Types

সমর্থিত Exam Types:

- Test
- Monthly Exam
- Midterm
- Final
- Model Test
- Other Exam

---

## 📖 Subject Management

প্রতিটি Subject-এর জন্য:

- Subject Code
- Subject Name
- Full Marks
- Pass Marks
- Active / Inactive Status

---

## 🧮 Marks Entry

- Student ID
- Exam Selection
- Subject Selection
- Marks Entry
- Marks Update

---

## ✏️ Marks Management

- Add Marks
- Edit Marks
- Update Marks
- Delete Marks

---

## 📊 Automatic Result Calculation

সফটওয়্যার স্বয়ংক্রিয়ভাবে হিসাব করবে:

- Total Marks
- Full Marks
- Percentage
- Grade
- GPA
- Pass / Fail

---

## 🎓 Grade System

| Percentage | Grade | GPA |
|---|---|---|
| 80+ | A+ | 5.00 |
| 70–79 | A | 4.00 |
| 60–69 | A- | 3.50 |
| 50–59 | B | 3.00 |
| 40–49 | C | 2.00 |
| 33–39 | D | 1.00 |
| Below 33 | F | 0.00 |

---

## 👨‍🎓 Student-wise Result

একজন শিক্ষার্থীর জন্য:

- Subject-wise Marks
- Total Marks
- Percentage
- Grade
- GPA
- Pass / Fail

---

## 📋 Class-wise Result

- Student Ranking
- Total Marks
- Percentage
- Grade
- Class Performance

---

## 🧾 Report Card

Print-ready Report Card:

```text
================================================
                REPORT CARD
================================================

Student Name
Student ID
Class
Section

Subject-wise Marks

Total Marks
Percentage
Grade
GPA
Result

================================================
```

---

## 🔎 Result Search

- Search by Student ID
- Search by Exam
- Student Result View
- Class Result View

---

# 🚀 Phase 5 — Reports, Export, Backup & Professional Features

Phase 5-এ সফটওয়্যারকে আরও Professional এবং Production-ready করার জন্য Reporting ও Backup System যুক্ত করা হয়েছে।

---

# 📊 Advanced Reports

## 👨‍🎓 Student Reports

- Complete Student List
- Student Information
- Class-wise Student Report

---

## 👨‍🏫 Teacher Reports

- Teacher List
- Subject Information
- Contact Information

---

## 👨‍💼 Staff Reports

- Staff List
- Designation
- Contact Information

---

## 📅 Attendance Reports

- Student Attendance
- Teacher Attendance
- Staff Attendance
- Attendance Status

---

## 💰 Financial Reports

- Fee Collection Report
- Student Due Report
- Payment History
- Collection Summary

---

## 📝 Examination Reports

- Exam Marks Report
- Result Summary
- Student Result
- Academic Performance

---

# 📄 CSV Export

Reports CSV format-এ Export করা যাবে।

সমর্থিত Data:

- Students
- Teachers
- Staff
- Attendance
- Fees
- Due
- Payments
- Marks
- Results

---

# 📊 Excel Export

Excel `.xlsx` Export:

```bash
pip install openpyxl
```

Excel Export করা যাবে:

- Student Report
- Teacher Report
- Staff Report
- Attendance
- Fee Collection
- Payment History
- Exam Marks
- Results

---

# 🖨️ Print-ready Reports

Print-ready View:

- Student Reports
- Attendance Reports
- Financial Reports
- Exam Reports
- Result Reports

---

# 💾 Database Backup

Database Backup তৈরি করা যাবে:

```text
school_backup_YYYYMMDD_HHMMSS.db
```

Backup ব্যবহার করে:

- Data নিরাপদ রাখা
- নতুন Computer-এ Data Transfer
- জরুরি Data Recovery

---

# ♻️ Database Restore

Backup Database থেকে:

- Database Restore
- Old Data Recovery
- System Data Recovery

⚠️ Restore করার আগে বর্তমান Database Backup নেওয়ার পরামর্শ দেওয়া হয়।

---

# 🔍 Database Integrity Check

SQLite Database-এর Integrity পরীক্ষা করা যাবে।

এটি Database সমস্যা শনাক্ত করতে সাহায্য করবে।

---

# 🎓 Certificate System

নিম্নলিখিত Certificate তৈরি করা যাবে:

- Character Certificate
- Transfer Certificate
- Testimonial
- Academic Certificate

Certificate-এ থাকবে:

- Student Name
- Student ID
- Class
- Section
- Issue Date
- School Signature Area

---

# 📊 Complete Feature Summary

```text
Offline School Management System
│
├── 🔐 Authentication
│
├── 👨‍🎓 Student Management
│   ├── Add
│   ├── Edit
│   ├── Delete
│   ├── Search
│   └── Photo
│
├── 👨‍🏫 Teacher Management
│
├── 👨‍💼 Staff Management
│
├── 📅 Attendance
│   ├── Students
│   ├── Teachers
│   └── Staff
│
├── 💰 Fees & Payment
│   ├── Monthly Fee
│   ├── Admission Fee
│   ├── Exam Fee
│   ├── Due
│   ├── Payment
│   └── Receipt
│
├── 📝 Examination
│   ├── Exam
│   ├── Subjects
│   ├── Marks
│   ├── Grade
│   ├── GPA
│   └── Result
│
├── 📊 Reports
│
├── 📄 CSV Export
│
├── 📊 Excel Export
│
├── 🖨️ Print-ready Reports
│
├── 💾 Backup & Restore
│
└── 🎓 Certificate System
```

---

# ▶️ Installation

## 1. Python Install করুন

Python 3 install করুন।

Python Version check:

```bash
python --version
```

অথবা Windows-এ:

```bash
py --version
```

---

## 2. Project Folder Open করুন

```bash
cd School_Management_System
```

---

## 3. Optional Excel Support Install করুন

```bash
pip install openpyxl
```

---

## 4. Application Run করুন

```bash
python main.py
```

Windows:

```bash
py main.py
```

---

# 🔐 Default Login

```text
Username: admin
Password: admin123
```

⚠️ প্রথম Login-এর পরে নিরাপত্তার জন্য Password পরিবর্তন করার পরামর্শ দেওয়া হচ্ছে।

---

# 💾 Database

এই Project SQLite ব্যবহার করে।

Database সম্পূর্ণ Offline-এ কাজ করে।

```text
database/
└── school.db
```

Internet Connection প্রয়োজন নেই।

---

# 🔒 Security

বর্তমান System-এ:

- User Authentication
- Login System
- User Management
- Activity Logging
- Active / Inactive Users
- Database Backup
- Database Restore

Production version-এ আরও যোগ করা যেতে পারে:

- Password Hashing
- Advanced Role Permissions
- Module Permissions
- Login History
- Session Management

---

# 📦 Windows EXE Build

PyInstaller ব্যবহার করে `.exe` তৈরি করা যাবে।

Install:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --noconfirm --onefile --windowed --name "School Management System" main.py
```

Icon সহ:

```bash
pyinstaller --noconfirm --onefile --windowed --icon=assets/icon.ico --name "School Management System" main.py
```

Build File:

```text
dist/
└── School Management System.exe
```

---

# 🖥️ Professional Windows Installer

Professional Installer তৈরির জন্য:

- PyInstaller
- Inno Setup 6

ব্যবহার করা যেতে পারে।

Installer-এ থাকবে:

```text
School Management System Setup.exe
│
├── Install Application
├── Start Menu Shortcut
├── Desktop Shortcut
└── Uninstaller
```

---

# 🔮 Future Development

পরবর্তী Phase-এ যোগ করা যেতে পারে:

## Phase 6 — School Operations & Communication

- 👨‍👩‍👧 Parent / Guardian Management
- 🪪 Student ID Card
- 🔳 QR Code
- 📢 Notice Management
- 🔔 Internal Notification
- 📅 Academic Calendar
- 🕒 Timetable Management
- 🏥 Student Health Information
- 🏆 Student Awards
- 🏃 Events & Activities
- 🔐 Advanced User Permissions
- 📝 Advanced Activity Logs
- 🇧🇩 Bangladesh School Support
- 📊 Final Dashboard Integration

---

# 🗺️ Development Roadmap

```text
Phase 1
Foundation System
        ↓
Phase 2
Student + Teacher + Staff + Attendance
        ↓
Phase 3
Fees & Payment Management
        ↓
Phase 4
Examination & Result Management
        ↓
Phase 5
Reports + Export + Backup + Certificates
        ↓
Phase 6
School Operations & Communication
```

---

# 👨‍💻 Developer

**Nayem Ahammad**

---

# 📜 License

Copyright © 2026 Nayem Ahammad.

All Rights Reserved.

This software, including its source code, database structure, documentation, user interface, graphics, assets and related materials, is protected by copyright law.

Unauthorized copying, modification, redistribution, resale, reverse engineering, or commercial use without written permission from the copyright holder is prohibited.

See the `LICENSE` file for complete license information.

---

# ⭐ Project Status

```text
████████████████████████████░░

Phase 1  ✅ Complete
Phase 2  ✅ Complete
Phase 3  ✅ Complete
Phase 4  ✅ Complete
Phase 5  ✅ Complete
Phase 6  🚧 Planned
```

---

## 🏫 Offline School Management System

### **A Professional, Secure & Modern School Management Solution**

**Built with ❤️ using Python & SQLite**

**© 2026 Nayem Ahammad. All Rights Reserved.**