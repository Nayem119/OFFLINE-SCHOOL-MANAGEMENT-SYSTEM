import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database.db import query, execute, log_activity
from utils.permissions import require_admin
from utils.helpers import today
from utils.popup import PopupForm
from utils.pdf_style import draw_brand_header, draw_footer

def grade_gpa(pct):
    if pct >= 80: return "A+", 5.00
    if pct >= 70: return "A", 4.00
    if pct >= 60: return "A-", 3.50
    if pct >= 50: return "B", 3.00
    if pct >= 40: return "C", 2.00
    if pct >= 33: return "D", 1.00
    return "F", 0.00

class ExamsFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master,padding=10)
        self.user=user
        self.selected_exam=None
        self.build()
        self.refresh()

    def build(self):
        nb=ttk.Notebook(self);nb.pack(fill="both",expand=True)
        self.exam_tab=ttk.Frame(nb,padding=8)
        self.mark_tab=ttk.Frame(nb,padding=8);self.result_tab=ttk.Frame(nb,padding=8)
        nb.add(self.exam_tab,text="📝 Exams")
        nb.add(self.mark_tab,text="🧮 Marks Entry")
        nb.add(self.result_tab,text="🧾 Results / Report Card")
        self.build_exams();self.build_marks();self.build_results()

    def build_exams(self):
        f=ttk.LabelFrame(self.exam_tab,text="Create Exam",padding=10);f.pack(fill="x")
        self.ev={k:tk.StringVar() for k in ["name","type","class","section","date"]}
        self.ev["type"].set("Midterm");self.ev["date"].set(today())
        fields=[("Exam Name","name"),("Exam Type","type"),("Class","class"),("Section","section"),("Date","date")]
        for i,(l,k) in enumerate(fields):
            ttk.Label(f,text=l).grid(row=0,column=i,padx=4,sticky="w")
            if k=="type": w=ttk.Combobox(f,textvariable=self.ev[k],values=["Test","Midterm","Final","Model Test","Monthly","Other"],state="readonly")
            elif k=="class":
                w=ttk.Combobox(f,textvariable=self.ev[k],values=[r["class_name"] for r in query("SELECT DISTINCT class_name FROM classes ORDER BY class_name")],state="readonly")
            elif k=="section":
                w=ttk.Combobox(f,textvariable=self.ev[k],values=[r["section"] for r in query("SELECT DISTINCT section FROM classes ORDER BY section")],state="readonly")
            elif k=="date":
                date_box=ttk.Frame(f);date_box.grid(row=1,column=i,sticky="ew",padx=4);date_box.columnconfigure(0,weight=1)
                w=ttk.Entry(date_box,textvariable=self.ev[k]);w.grid(row=0,column=0,sticky="ew")
                ttk.Button(date_box,text="Calendar",command=lambda variable=self.ev[k]:PopupForm.open_calendar(self,variable)).grid(row=0,column=1,padx=(4,0))
                continue
            else:w=ttk.Entry(f,textvariable=self.ev[k])
            w.grid(row=1,column=i,padx=4,sticky="ew")
            f.columnconfigure(i,weight=1)
        ttk.Button(f,text="➕ Add Exam",command=self.add_exam).grid(row=1,column=5,padx=8)
        ttk.Button(f,text="✏️ Update",command=self.update_exam).grid(row=1,column=6,padx=4)
        ttk.Button(f,text="🗑 Remove",command=self.delete_exam).grid(row=1,column=7,padx=4)
        self.exam_tree=ttk.Treeview(self.exam_tab,columns=("id","name","type","class","section","date"),show="headings")
        for c,h in [("id","ID"),("name","Exam"),("type","Type"),("class","Class"),("section","Section"),("date","Date")]:
            self.exam_tree.heading(c,text=h);self.exam_tree.column(c,width=130)
        self.exam_tree.pack(fill="both",expand=True,pady=8)
        self.exam_tree.bind("<<TreeviewSelect>>",self.select_exam)

    def build_subjects(self):
        f=ttk.LabelFrame(self.sub_tab,text="Subject Management",padding=10);f.pack(fill="x")
        self.sv={k:tk.StringVar() for k in ["code","name","full","pass"]}
        self.sv["full"].set("100");self.sv["pass"].set("33")
        for i,(l,k) in enumerate([("Code","code"),("Subject Name","name"),("Full Marks","full"),("Pass Marks","pass")]):
            ttk.Label(f,text=l).grid(row=0,column=i,sticky="w",padx=5)
            ttk.Entry(f,textvariable=self.sv[k]).grid(row=1,column=i,sticky="ew",padx=5)
            f.columnconfigure(i,weight=1)
        ttk.Button(f,text="➕ Add Subject",command=self.add_subject).grid(row=1,column=4,padx=8)
        self.sub_tree=ttk.Treeview(self.sub_tab,columns=("id","code","name","full","pass","status"),show="headings")
        for c,h in [("id","ID"),("code","Code"),("name","Subject"),("full","Full Marks"),("pass","Pass Marks"),("status","Status")]:
            self.sub_tree.heading(c,text=h);self.sub_tree.column(c,width=140)
        self.sub_tree.pack(fill="both",expand=True,pady=8)

    def build_marks(self):
        top=ttk.Frame(self.mark_tab);top.pack(fill="x")
        self.exam_sel=tk.StringVar();self.mark_student=tk.StringVar();self.mark_subject=tk.StringVar();self.mark_value=tk.StringVar()
        ttk.Label(top,text="Exam").pack(side="left")
        self.exam_combo=ttk.Combobox(top,textvariable=self.exam_sel,state="readonly",width=35);self.exam_combo.pack(side="left",padx=5)
        ttk.Label(top,text="Student ID").pack(side="left")
        ttk.Entry(top,textvariable=self.mark_student,width=16).pack(side="left",padx=5)
        ttk.Label(top,text="Subject").pack(side="left")
        self.subject_combo=ttk.Combobox(top,textvariable=self.mark_subject,state="readonly",width=25);self.subject_combo.pack(side="left",padx=5)
        ttk.Label(top,text="Marks").pack(side="left")
        ttk.Entry(top,textvariable=self.mark_value,width=10).pack(side="left",padx=5)
        ttk.Button(top,text="💾 Save / Update",command=self.save_mark).pack(side="left",padx=5)
        ttk.Button(top,text="🗑️ Delete Selected",command=self.delete_mark).pack(side="left",padx=5)
        self.mark_tree=ttk.Treeview(self.mark_tab,columns=("id","student","name","subject","marks","full","status"),show="headings")
        for c,h in [("id","ID"),("student","Student ID"),("name","Student"),("subject","Subject"),("marks","Marks"),("full","Full"),("status","Status")]:
            self.mark_tree.heading(c,text=h);self.mark_tree.column(c,width=120)
        self.mark_tree.pack(fill="both",expand=True,pady=10)
        self.mark_tree.bind("<<TreeviewSelect>>",self.select_mark)

    def build_results(self):
        f=ttk.LabelFrame(self.result_tab,text="Result Search",padding=10);f.pack(fill="x")
        self.rv={k:tk.StringVar() for k in ["student","exam"]}
        ttk.Label(f,text="Student ID").grid(row=0,column=0);ttk.Entry(f,textvariable=self.rv["student"]).grid(row=1,column=0,padx=5)
        ttk.Label(f,text="Exam").grid(row=0,column=1);self.result_exam=ttk.Combobox(f,textvariable=self.rv["exam"],state="readonly",width=35);self.result_exam.grid(row=1,column=1,padx=5)
        ttk.Button(f,text="🔎 Student Result",command=self.student_result).grid(row=1,column=2,padx=5)
        ttk.Button(f,text="📋 Class Result",command=self.class_result).grid(row=1,column=3,padx=5)
        ttk.Button(f,text="📈 Progress Chart",command=self.progress_chart).grid(row=1,column=4,padx=5)
        ttk.Button(f,text="🖨️ Print-ready View",command=self.print_view).grid(row=1,column=5,padx=5)
        ttk.Button(f,text="📕 Export PDF",command=self.export_result_pdf).grid(row=1,column=6,padx=5)
        self.result_text=tk.Text(self.result_tab,font=("Courier New",10))
        self.result_text.pack(fill="both",expand=True,pady=10)

    def refresh(self):
        self.load_exams();self.load_marks()
        vals=[f"{r['id']} | {r['exam_name']} | {r['exam_type']} | {r['class_name']}" for r in query("SELECT * FROM exams ORDER BY id DESC")]
        self.exam_combo["values"]=vals;self.result_exam["values"]=vals
        self.subject_combo["values"]=[f"{r['id']} | {r['subject_code']} | {r['subject_name']} | {r['class_name']} {r['section']}" for r in query("SELECT * FROM subjects WHERE active=1 ORDER BY class_name,subject_name")]

    def load_exams(self):
        for x in self.exam_tree.get_children():self.exam_tree.delete(x)
        for r in query("SELECT * FROM exams ORDER BY id DESC"):
            self.exam_tree.insert("", "end",values=(r["id"],r["exam_name"],r["exam_type"],r["class_name"],r["section"],r["exam_date"]))

    def select_exam(self,_=None):
        item=self.exam_tree.focus()
        if not item:return
        values=self.exam_tree.item(item)["values"];self.selected_exam=values[0]
        for key,value in zip(["name","type","class","section","date"],values[1:]):self.ev[key].set(value)

    def update_exam(self):
        if not self.selected_exam:return messagebox.showwarning("Select","আগে একটি exam নির্বাচন করুন।")
        if not self.ev["name"].get().strip() or not self.ev["class"].get().strip() or not self.ev["date"].get().strip():return messagebox.showwarning("Required","Exam name, class এবং date আবশ্যক।")
        try:
            execute("UPDATE exams SET exam_name=?,exam_type=?,class_name=?,section=?,exam_date=? WHERE id=?",(self.ev["name"].get().strip(),self.ev["type"].get(),self.ev["class"].get().strip(),self.ev["section"].get().strip(),self.ev["date"].get().strip(),self.selected_exam));log_activity(self.user["username"],"Updated exam "+self.ev["name"].get().strip());self.selected_exam=None;self.refresh()
        except Exception as e:messagebox.showerror("Error",str(e))

    def delete_exam(self):
        if not self.selected_exam:return messagebox.showwarning("Select","আগে একটি exam নির্বাচন করুন।")
        if not messagebox.askyesno("Confirm","এই exam এবং এর marks remove করবেন?"):return
        execute("DELETE FROM marks WHERE exam_id=?",(self.selected_exam,));execute("DELETE FROM exams WHERE id=?",(self.selected_exam,));log_activity(self.user["username"],"Removed exam");self.selected_exam=None;self.refresh()

    def load_subjects(self):
        for x in self.sub_tree.get_children():self.sub_tree.delete(x)
        for r in query("SELECT * FROM subjects ORDER BY id DESC"):
            self.sub_tree.insert("", "end",values=(r["id"],r["subject_code"],r["subject_name"],r["full_marks"],r["pass_marks"],"Active" if r["active"] else "Inactive"))

    def load_marks(self):
        if not hasattr(self,"mark_tree"):return
        for x in self.mark_tree.get_children():self.mark_tree.delete(x)
        rows=query("""SELECT m.id,m.student_id,s.name,sub.subject_name,m.marks,sub.full_marks
                     FROM marks m JOIN students s ON s.student_id=m.student_id
                     JOIN subjects sub ON sub.id=m.subject_id ORDER BY m.id DESC LIMIT 500""")
        for r in rows:
            status="Pass" if float(r["marks"])>=float(query("SELECT pass_marks FROM subjects WHERE id=(SELECT subject_id FROM marks WHERE id=?)",(r["id"],))[0]["pass_marks"]) else "Fail"
            self.mark_tree.insert("", "end",values=(r["id"],r["student_id"],r["name"],r["subject_name"],r["marks"],r["full_marks"],status))

    def add_exam(self):
        if not self.ev["name"].get().strip() or not self.ev["class"].get().strip() or not self.ev["date"].get().strip():
            return messagebox.showwarning("Required","Exam name, class এবং date আবশ্যক।")
        try:
            execute("INSERT INTO exams(exam_name,exam_type,class_name,section,exam_date) VALUES(?,?,?,?,?)",
                    (self.ev["name"].get(),self.ev["type"].get(),self.ev["class"].get(),self.ev["section"].get(),self.ev["date"].get()))
            log_activity(self.user["username"],"Added exam "+self.ev["name"].get());self.refresh()
        except Exception as e:messagebox.showerror("Error",str(e))

    def add_subject(self):
        if not self.sv["code"].get().strip() or not self.sv["name"].get().strip():
            return messagebox.showwarning("Required","Subject code এবং name আবশ্যক।")
        try:
            full=float(self.sv["full"].get());passed=float(self.sv["pass"].get())
            if full<=0 or passed<0 or passed>full:raise ValueError("Pass marks must be between 0 and full marks")
            execute("INSERT INTO subjects(subject_code,subject_name,full_marks,pass_marks) VALUES(?,?,?,?)",
                    (self.sv["code"].get().strip(),self.sv["name"].get().strip(),full,passed))
            log_activity(self.user["username"],"Added subject "+self.sv["name"].get());self.refresh()
        except Exception as e:messagebox.showerror("Error",str(e))

    def save_mark(self):
        try:
            sid=self.mark_student.get().strip()
            if not query("SELECT id FROM students WHERE student_id=?",(sid,)):raise ValueError("Student not found")
            exam_id=int(self.exam_sel.get().split("|")[0].strip())
            subject_id=int(self.mark_subject.get().split("|")[0].strip())
            mark=float(self.mark_value.get())
            sub=query("SELECT full_marks FROM subjects WHERE id=?",(subject_id,))[0]
            if mark<0 or mark>float(sub["full_marks"]):raise ValueError("Marks exceed full marks")
            execute("""INSERT INTO marks(exam_id,student_id,subject_id,marks) VALUES(?,?,?,?)
                       ON CONFLICT(exam_id,student_id,subject_id) DO UPDATE SET marks=excluded.marks""",
                    (exam_id,sid,subject_id,mark))
            log_activity(self.user["username"],f"Saved marks: {sid}")
            self.load_marks()
        except Exception as e:messagebox.showerror("Error",str(e))

    def select_mark(self,_=None):
        item=self.mark_tree.focus()
        if not item:return
        v=self.mark_tree.item(item)["values"]
        self.mark_student.set(v[1]);self.mark_value.set(v[4])

    def delete_mark(self):
        item=self.mark_tree.focus()
        if not item:return
        if not require_admin(self.user, messagebox, "marks delete"):return
        mid=self.mark_tree.item(item)["values"][0]
        if messagebox.askyesno("Confirm","Delete selected marks?"):
            execute("DELETE FROM marks WHERE id=?",(mid,));log_activity(self.user["username"],"Deleted marks");self.load_marks()

    def selected_exam_id(self,var):
        return int(var.get().split("|")[0].strip())

    def student_result(self):
        sid=self.rv["student"].get().strip()
        if not sid:return messagebox.showwarning("Required","Student ID দিন।")
        eid=self.selected_exam_id(self.rv["exam"])
        student=query("SELECT * FROM students WHERE student_id=?",(sid,))
        exam=query("SELECT * FROM exams WHERE id=?",(eid,))
        if not student or not exam:return messagebox.showwarning("Not Found","Student/Exam পাওয়া যায়নি।")
        rows=query("""SELECT sub.subject_name,sub.full_marks,sub.pass_marks,m.marks
                      FROM marks m JOIN subjects sub ON sub.id=m.subject_id
                      WHERE m.exam_id=? AND m.student_id=? ORDER BY sub.subject_name""",(eid,sid))
        self.render_result(student[0],exam[0],rows)

    def class_result(self):
        eid=self.selected_exam_id(self.rv["exam"])
        ex=query("SELECT * FROM exams WHERE id=?",(eid,))[0]
        rows=query("""SELECT s.student_id,s.name,COALESCE(SUM(m.marks),0) total,
                      COALESCE(SUM(sub.full_marks),0) full
                      FROM students s LEFT JOIN marks m ON m.student_id=s.student_id AND m.exam_id=?
                      LEFT JOIN subjects sub ON sub.id=m.subject_id
                      WHERE s.class_name=? AND (?='' OR s.section=?)
                      GROUP BY s.student_id,s.name ORDER BY total DESC""",
                   (eid,ex["class_name"],ex["section"],ex["section"]))
        self.result_text.delete("1.0","end")
        self.result_text.insert("end",f"CLASS RESULT — {ex['exam_name']}\nClass: {ex['class_name']} {ex['section']}\n"+"="*72+"\n")
        self.result_text.insert("end",f"{'Rank':<6}{'ID':<16}{'Student':<28}{'Total':>8}{'%':>8}{'Grade':>8}\n"+"-"*72+"\n")
        for i,r in enumerate(rows,1):
            pct=(float(r["total"])/float(r["full"])*100) if r["full"] else 0
            g,gpa=grade_gpa(pct)
            self.result_text.insert("end",f"{i:<6}{r['student_id']:<16}{r['name'][:26]:<28}{r['total']:>8.1f}{pct:>8.2f}{g:>8}\n")
        log_activity(self.user["username"],f"Viewed class result for exam {eid}")

    def progress_chart(self):
        sid=self.rv["student"].get().strip()
        if not sid:return messagebox.showwarning("Required","Student ID দিন।")
        student=query("SELECT name FROM students WHERE student_id=?",(sid,))
        if not student:return messagebox.showwarning("Not Found","Student পাওয়া যায়নি।")
        rows=query("""SELECT e.exam_name,e.exam_date,COALESCE(SUM(m.marks),0) total,COALESCE(SUM(sub.full_marks),0) full
                      FROM exams e JOIN marks m ON m.exam_id=e.id JOIN subjects sub ON sub.id=m.subject_id
                      WHERE m.student_id=? GROUP BY e.id,e.exam_name,e.exam_date ORDER BY e.exam_date,e.id""",(sid,))
        if not rows:return messagebox.showinfo("No Results","এই student-এর কোনো result পাওয়া যায়নি।")
        win=tk.Toplevel(self);win.title(f"Progress Chart - {student[0]['name']}");win.geometry("760x430");win.transient(self.winfo_toplevel())
        ttk.Label(win,text=f"{student[0]['name']} ({sid})",font=("TkDefaultFont",15,"bold")).pack(anchor="w",padx=16,pady=(14,2))
        ttk.Label(win,text="Exam-wise percentage progress",foreground="#5d7180").pack(anchor="w",padx=16)
        canvas=tk.Canvas(win,height=300,bg="#ffffff",highlightthickness=1,highlightbackground="#dce5ea");canvas.pack(fill="both",expand=True,padx=16,pady=14)
        canvas.update_idletasks();width=max(canvas.winfo_width(),600);height=300;left=55;bottom=245;plot_width=width-90;plot_height=190
        canvas.create_line(left,55,left,bottom,fill="#9fb0b8");canvas.create_line(left,bottom,width-25,bottom,fill="#9fb0b8")
        for level in (0,25,50,75,100):
            y=bottom-(level/100)*plot_height;canvas.create_line(left,y,width-25,y,fill="#edf1f3");canvas.create_text(left-20,y,text=str(level),fill="#5d7180",font=("TkDefaultFont",8))
        points=[]
        for index,row in enumerate(rows):
            percent=float(row["total"])/float(row["full"])*100 if row["full"] else 0
            x=left+(plot_width*index/max(len(rows)-1,1));y=bottom-(min(percent,100)/100)*plot_height;points.append((x,y))
            canvas.create_oval(x-5,y-5,x+5,y+5,fill="#2a9d8f",outline="#17324d");canvas.create_text(x,y-16,text=f"{percent:.1f}%",fill="#17324d",font=("TkDefaultFont",8));canvas.create_text(x,bottom+16,text=row["exam_name"][:14],fill="#5d7180",font=("TkDefaultFont",8))
        for first,second in zip(points,points[1:]):canvas.create_line(*first,*second,fill="#2a9d8f",width=3)

    def render_result(self,student,exam,rows):
        total=sum(float(r["marks"]) for r in rows);full=sum(float(r["full_marks"]) for r in rows)
        pct=(total/full*100) if full else 0
        failed=any(float(r["marks"])<float(r["pass_marks"]) for r in rows)
        grade,gpa=grade_gpa(pct)
        if failed:grade="F";gpa=0.0
        self.result_text.delete("1.0","end")
        lines=[
            "="*64,"SCHOOL MANAGEMENT SYSTEM","ACADEMIC REPORT CARD",
            "="*64,f"Student ID : {student['student_id']}",f"Student    : {student['name']}",
            f"Class      : {student['class_name']}  Section: {student['section']}",
            f"Exam       : {exam['exam_name']} ({exam['exam_type']})",f"Date       : {exam['exam_date']}",
            "-"*64,f"{'Subject':<28}{'Full':>10}{'Marks':>10}{'Status':>12}","-"*64
        ]
        for r in rows:
            st="PASS" if float(r["marks"])>=float(r["pass_marks"]) else "FAIL"
            lines.append(f"{r['subject_name'][:26]:<28}{float(r['full_marks']):>10.1f}{float(r['marks']):>10.1f}{st:>12}")
        lines += ["-"*64,f"Total      : {total:.2f} / {full:.2f}",f"Percentage : {pct:.2f}%",
                  f"Grade      : {grade}",f"GPA        : {gpa:.2f}",f"Result     : {'FAIL' if failed else 'PASS'}",
                  "="*64]
        self.result_text.insert("1.0","\n".join(lines))
        log_activity(self.user["username"],f"Viewed student result {student['student_id']}")

    def print_view(self):
        if not self.result_text.get("1.0","end").strip():return messagebox.showwarning("Empty","আগে result তৈরি করুন।")
        win=tk.Toplevel(self);win.title("Print-ready Result");win.geometry("800x700")
        t=tk.Text(win,font=("Courier New",11));t.pack(fill="both",expand=True);t.insert("1.0",self.result_text.get("1.0","end"))
        ttk.Button(win,text="Close",command=win.destroy).pack(pady=5)

    def export_result_pdf(self):
        content=self.result_text.get("1.0","end").strip()
        if not content:return messagebox.showwarning("Empty","আগে একটি result তৈরি করুন।")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            return messagebox.showwarning("PDF Export","Result PDF-এর জন্য reportlab install করুন: pip install reportlab")
        path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")],initialfile="student_result.pdf")
        if not path:return
        try:
            pdf=canvas.Canvas(path,pagesize=A4);width,height=A4;settings=dict(query("SELECT * FROM settings WHERE id=1")[0]);y=draw_brand_header(pdf,"Academic Result",settings,width,height);pdf.setFont("Courier",9)
            for line in content.splitlines():
                if y<48:draw_footer(pdf,width);pdf.showPage();y=draw_brand_header(pdf,"Academic Result",settings,width,height);pdf.setFont("Courier",9)
                pdf.drawString(34,y,line[:115]);y-=12
            draw_footer(pdf,width)
            pdf.save();messagebox.showinfo("Export Complete",f"Result PDF saved:\n{path}")
        except Exception as e:messagebox.showerror("PDF Error",str(e))
