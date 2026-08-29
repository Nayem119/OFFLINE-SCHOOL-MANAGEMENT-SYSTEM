import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, execute, log_activity
from utils.helpers import today
from utils.permissions import require_admin
from utils.popup import PopupForm

class AttendanceFrame(ttk.Frame):
    def __init__(self,master,user):
        super().__init__(master,padding=12);self.user=user
        self.date=tk.StringVar(value=today());self.kind=tk.StringVar(value="Student")
        self.class_name=tk.StringVar(value="All Classes")
        self.status=tk.StringVar(value="Present");self.note=tk.StringVar()
        self.build();self.load_people()
    def build(self):
        top=ttk.LabelFrame(self,text="📅 Attendance",padding=10);top.pack(fill="x")
        ttk.Label(top,text="Type").grid(row=0,column=0,padx=5);cb=ttk.Combobox(top,textvariable=self.kind,values=["Student","Teacher","Staff"],state="readonly");cb.grid(row=1,column=0,padx=5);cb.bind("<<ComboboxSelected>>",lambda e:self.load_people())
        ttk.Label(top,text="Date (YYYY-MM-DD)").grid(row=0,column=1,padx=5);date_box=ttk.Frame(top);date_box.grid(row=1,column=1,padx=5);ttk.Entry(date_box,textvariable=self.date).pack(side="left");ttk.Button(date_box,text="Calendar",command=lambda:PopupForm.open_calendar(self,self.date)).pack(side="left",padx=(4,0))
        ttk.Label(top,text="Class").grid(row=0,column=2,padx=5);self.class_combo=ttk.Combobox(top,textvariable=self.class_name,state="readonly");self.class_combo.grid(row=1,column=2,padx=5);self.class_combo.bind("<<ComboboxSelected>>",lambda _event:self.load_people())
        ttk.Label(top,text="Status").grid(row=0,column=3,padx=5);ttk.Combobox(top,textvariable=self.status,values=["Present","Absent","Late","Leave"],state="readonly").grid(row=1,column=3,padx=5)
        ttk.Label(top,text="Note").grid(row=0,column=4,padx=5);ttk.Entry(top,textvariable=self.note,width=24).grid(row=1,column=4,padx=5)
        ttk.Button(top,text="💾 Save Selected",command=self.save).grid(row=1,column=5,padx=8)
        ttk.Button(top,text="✅ Present All",command=self.present_all).grid(row=1,column=6,padx=5)
        ttk.Button(top,text="🔄 Load",command=self.load_people).grid(row=1,column=7,padx=5)
        ttk.Button(top,text="🗑 Remove Selected",command=self.remove_selected).grid(row=1,column=8,padx=5)
        self.tree=ttk.Treeview(self,columns=("id","name","class","status"),show="headings",selectmode="extended")
        for c,h in [("id","ID"),("name","নাম"),("class","Class/Subject"),("status","Today Status")]:self.tree.heading(c,text=h);self.tree.column(c,width=180)
        self.tree.pack(fill="both",expand=True,pady=10)
    def load_people(self):
        for x in self.tree.get_children():self.tree.delete(x)
        k=self.kind.get()
        if k=="Student":
            classes=[r["class_name"] for r in query("SELECT DISTINCT class_name FROM students WHERE class_name<>'' ORDER BY class_name")]
            self.class_combo["values"]=["All Classes"]+classes
            if self.class_name.get() not in self.class_combo["values"]:self.class_name.set("All Classes")
        if k=="Student":
            sql="SELECT student_id id,name,class_name info FROM students WHERE status='Active'"
            params=[]
            if self.class_name.get()!="All Classes":sql+=" AND class_name=?";params.append(self.class_name.get())
            rows=query(sql+" ORDER BY name",params)
        elif k=="Teacher":
            self.class_name.set("All Classes");self.class_combo["values"]=["All Classes"]
            rows=query("SELECT teacher_id id,name,subject info FROM teachers WHERE status='Active' ORDER BY name")
        else:
            self.class_name.set("All Classes");self.class_combo["values"]=["All Classes"]
            rows=query("SELECT staff_id id,name,designation info FROM staff WHERE status='Active' ORDER BY name")
        for r in rows:
            a=query("SELECT status FROM attendance WHERE person_type=? AND person_id=? AND attendance_date=?",(k,r["id"],self.date.get()))
            st=a[0]["status"] if a else "Not Marked"
            self.tree.insert("", "end",values=(r["id"],r["name"],r["info"],st))
    def save(self):
        items=self.tree.selection()
        if not items:messagebox.showwarning("Select","কমপক্ষে একজন person নির্বাচন করুন।");return
        try:
            for item in items:
                pid,name=self.tree.item(item)["values"][:2]
                execute("""INSERT INTO attendance(person_type,person_id,person_name,attendance_date,status,note)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(person_type,person_id,attendance_date) DO UPDATE SET status=excluded.status,note=excluded.note""",
                (self.kind.get(),pid,name,self.date.get(),self.status.get(),self.note.get().strip()))
            log_activity(self.user["username"],f"Attendance {self.kind.get()}: {len(items)} record(s) marked {self.status.get()}")
            self.load_people()
        except Exception as e:messagebox.showerror("Error",str(e))

    def present_all(self):
        children=self.tree.get_children()
        if not children:return messagebox.showwarning("No People","এই filter-এ কোনো active person নেই।")
        self.tree.selection_set(children);self.status.set("Present");self.save()

    def remove_selected(self):
        items=self.tree.selection()
        if not items:return messagebox.showwarning("Select","কমপক্ষে একজন person নির্বাচন করুন।")
        if not require_admin(self.user,messagebox,"attendance remove"):return
        if not messagebox.askyesno("Confirm",f"{len(items)}টি attendance record remove করবেন?"):return
        for item in items:
            person_id=self.tree.item(item)["values"][0]
            execute("DELETE FROM attendance WHERE person_type=? AND person_id=? AND attendance_date=?",(self.kind.get(),person_id,self.date.get()))
        log_activity(self.user["username"],f"Removed {len(items)} {self.kind.get()} attendance record(s)");self.load_people()
