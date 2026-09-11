import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv, shutil, sqlite3

from database.db import query
from config import DB_PATH
from utils.helpers import today
from utils.permissions import require_admin
from database.db import execute
from utils.pdf_style import draw_brand_header, draw_footer

class ReportsFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, padding=12)
        self.user = user
        self.build()

    def build(self):
        top = ttk.LabelFrame(self, text="📊 Reports & Export", padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Report").grid(row=0, column=0, sticky="w")
        self.report_type = tk.StringVar(value="Student List")
        self.combo = ttk.Combobox(top, textvariable=self.report_type, state="readonly",
            values=["Student List","Teacher List","Staff List","Attendance Report",
                    "Fee Collection","Fee Due","Payment History","Exam Marks","Result Summary"], width=25)
        self.combo.grid(row=1, column=0, padx=5)
        ttk.Button(top, text="🔎 Generate", command=self.generate).grid(row=1,column=1,padx=5)
        ttk.Button(top, text="📄 Export CSV", command=self.export_csv).grid(row=1,column=2,padx=5)
        ttk.Button(top, text="📊 Export Excel", command=self.export_excel).grid(row=1,column=3,padx=5)
        ttk.Button(top, text="🖨️ Print-ready", command=self.print_ready).grid(row=1,column=4,padx=5)
        ttk.Button(top, text="📕 Export PDF", command=self.export_pdf).grid(row=1,column=5,padx=5)

        backup = ttk.LabelFrame(self, text="💾 Database Backup & Restore", padding=10)
        backup.pack(fill="x", pady=10)
        ttk.Button(backup, text="💾 Backup Database", command=self.backup).pack(side="left", padx=5)
        ttk.Button(backup, text="♻️ Restore Database", command=self.restore).pack(side="left", padx=5)
        ttk.Button(backup, text="🔍 Integrity Check", command=self.integrity).pack(side="left", padx=5)
        ttk.Button(backup, text="🧾 Backup History", command=self.backup_history).pack(side="left", padx=5)

        self.text = tk.Text(self, font=("Courier New", 10))
        self.text.pack(fill="both", expand=True)

    def rows(self):
        t = self.report_type.get()
        if t == "Student List":
            return query("SELECT student_id,name,class_name,section,phone,gender FROM students ORDER BY class_name,section,name"), ["student_id","name","class_name","section","phone","gender"]
        if t == "Teacher List":
            return query("SELECT teacher_id,name,subject,phone,email FROM teachers ORDER BY name"), ["teacher_id","name","subject","phone","email"]
        if t == "Staff List":
            return query("SELECT staff_id,name,designation,phone,email FROM staff ORDER BY name"), ["staff_id","name","designation","phone","email"]
        if t == "Attendance Report":
            return query("SELECT person_type,person_id,person_name,attendance_date,status,note FROM attendance ORDER BY attendance_date DESC"), ["person_type","person_id","person_name","attendance_date","status","note"]
        if t == "Fee Collection":
            return query("SELECT receipt_no,student_id,student_name,payment_date,amount,fee_type,note FROM fee_payments ORDER BY payment_date DESC,id DESC"), ["receipt_no","student_id","student_name","payment_date","amount","fee_type","note"]
        if t == "Fee Due":
            return query("""SELECT sf.student_id,s.name,sf.fee_name,sf.amount,sf.due_date,sf.status,sf.note
                            FROM student_fees sf LEFT JOIN students s ON s.student_id=sf.student_id
                            WHERE sf.status='Due' ORDER BY sf.due_date"""), ["student_id","name","fee_name","amount","due_date","status","note"]
        if t == "Payment History":
            return query("SELECT receipt_no,student_id,student_name,payment_date,amount,fee_type,note FROM fee_payments ORDER BY id DESC"), ["receipt_no","student_id","student_name","payment_date","amount","fee_type","note"]
        if t == "Exam Marks":
            return query("""SELECT e.exam_name,s.student_id,s.name,sub.subject_name,m.marks,sub.full_marks,sub.pass_marks
                            FROM marks m JOIN exams e ON e.id=m.exam_id
                            JOIN students s ON s.student_id=m.student_id JOIN subjects sub ON sub.id=m.subject_id
                            ORDER BY e.exam_date DESC,s.name"""), ["exam_name","student_id","name","subject_name","marks","full_marks","pass_marks"]
        return query("""SELECT e.exam_name,s.student_id,s.name,COALESCE(SUM(m.marks),0) total,
                        COALESCE(SUM(sub.full_marks),0) full_marks
                        FROM marks m JOIN exams e ON e.id=m.exam_id JOIN students s ON s.student_id=m.student_id
                        JOIN subjects sub ON sub.id=m.subject_id GROUP BY e.id,s.student_id,s.name
                        ORDER BY e.exam_date DESC,total DESC"""), ["exam_name","student_id","name","total","full_marks"]

    def generate(self):
        try:
            rows, cols = self.rows()
            self.text.delete("1.0","end")
            title = self.report_type.get().upper()
            self.text.insert("end", f"{title}\nGenerated: {datetime.now():%Y-%m-%d %H:%M:%S}\n" + "="*100 + "\n")
            self.text.insert("end", " | ".join(cols) + "\n" + "-"*100 + "\n")
            for r in rows:
                self.text.insert("end", " | ".join(str(r[c] if r[c] is not None else "") for c in cols) + "\n")
            self.text.insert("end", f"\nTotal Records: {len(rows)}")
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    def export_csv(self):
        try:
            rows, cols = self.rows()
            path = filedialog.asksaveasfilename(defaultextension=".csv",
                filetypes=[("CSV file","*.csv")], initialfile=f"{self.report_type.get().replace(' ','_')}.csv")
            if not path: return
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.writer(f); w.writerow(cols)
                for r in rows: w.writerow([r[c] for c in cols])
            messagebox.showinfo("Export Complete", f"CSV saved:\n{path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def export_excel(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showwarning("Excel Export", "Excel export requires openpyxl.\nInstall with: pip install openpyxl")
            return
        try:
            rows, cols = self.rows()
            path=filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel","*.xlsx")],
                initialfile=f"{self.report_type.get().replace(' ','_')}.xlsx")
            if not path:return
            wb=openpyxl.Workbook();ws=wb.active;ws.title="Report"
            ws.append(cols)
            for r in rows: ws.append([r[c] for c in cols])
            for cell in ws[1]: cell.font=openpyxl.styles.Font(bold=True)
            ws.freeze_panes="A2"
            wb.save(path)
            messagebox.showinfo("Export Complete", f"Excel saved:\n{path}")
        except Exception as e: messagebox.showerror("Excel Error", str(e))

    def print_ready(self):
        if not self.text.get("1.0","end").strip(): self.generate()
        win=tk.Toplevel(self);win.title("Print-ready Report");win.geometry("1000x700")
        t=tk.Text(win,font=("Courier New",9));t.pack(fill="both",expand=True)
        t.insert("1.0",self.text.get("1.0","end"))
        ttk.Button(win,text="Close",command=win.destroy).pack(pady=5)

    def export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            messagebox.showwarning("PDF Export", "PDF export requires reportlab. Install with: pip install reportlab")
            return
        try:
            rows, cols = self.rows()
            path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")],initialfile=f"{self.report_type.get().replace(' ','_')}.pdf")
            if not path:return
            pdf=canvas.Canvas(path,pagesize=A4);width,height=A4;settings=dict(query("SELECT * FROM settings WHERE id=1")[0]);y=draw_brand_header(pdf,self.report_type.get().upper(),settings,width,height)
            pdf.setFont("Courier",7)
            for line in [" | ".join(cols), "-"*120] + [" | ".join(str(r[c] or "") for c in cols) for r in rows]:
                if y<48:draw_footer(pdf,width);pdf.showPage();y=draw_brand_header(pdf,self.report_type.get().upper(),settings,width,height);pdf.setFont("Courier",7)
                pdf.drawString(36,y,line[:145]);y-=10
            draw_footer(pdf,width)
            pdf.save();messagebox.showinfo("Export Complete",f"PDF saved:\n{path}")
        except Exception as e:messagebox.showerror("PDF Error",str(e))

    def backup(self):
        path=filedialog.asksaveasfilename(defaultextension=".db",filetypes=[("SQLite Database","*.db")],
            initialfile=f"school_backup_{datetime.now():%Y%m%d_%H%M%S}.db")
        if not path:return
        try:
            source=sqlite3.connect(DB_PATH); target=sqlite3.connect(path)
            try: source.backup(target)
            finally: target.close(); source.close()
            execute("INSERT INTO backup_history(action,file_path) VALUES(?,?)", ("Manual backup", path))
            messagebox.showinfo("Backup Complete", f"Backup saved:\n{path}")
        except Exception as e:messagebox.showerror("Backup Error",str(e))

    def restore(self):
        if not require_admin(self.user, messagebox, "Database restore"):return
        path=filedialog.askopenfilename(filetypes=[("SQLite Database","*.db")])
        if not path:return
        if not messagebox.askyesno("Confirm Restore","Restore this database? Current data will be replaced."):
            return
        try:
            # close/check source first
            con=sqlite3.connect(path); result=con.execute("PRAGMA integrity_check").fetchone()[0]; con.close()
            if result != "ok": raise ValueError(f"Backup integrity check failed: {result}")
            source=sqlite3.connect(path); target=sqlite3.connect(DB_PATH)
            try: source.backup(target)
            finally: target.close(); source.close()
            execute("INSERT INTO backup_history(action,file_path) VALUES(?,?)", ("Database restore", path))
            messagebox.showinfo("Restore Complete","Database restored. Please restart the application.")
        except Exception as e:messagebox.showerror("Restore Error",str(e))

    def integrity(self):
        try:
            con=sqlite3.connect(DB_PATH)
            result=con.execute("PRAGMA integrity_check").fetchone()[0]
            con.close()
            messagebox.showinfo("Database Integrity", result)
        except Exception as e:messagebox.showerror("Integrity Error",str(e))

    def backup_history(self):
        win=tk.Toplevel(self);win.title("Backup History");win.geometry("820x420");win.transient(self.winfo_toplevel())
        tree=ttk.Treeview(win,columns=("action","path","date"),show="headings")
        for column,title,width in [("action","Action",180),("path","File Path",470),("date","Date",150)]:tree.heading(column,text=title);tree.column(column,width=width)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        for row in query("SELECT action,file_path,created_at FROM backup_history ORDER BY id DESC LIMIT 50"):
            tree.insert("","end",values=(row["action"],row["file_path"],row["created_at"]))
