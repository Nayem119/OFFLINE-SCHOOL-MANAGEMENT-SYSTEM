import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, execute, log_activity

class CrudFrame(ttk.Frame):
    def __init__(self, master, user, title, table, fields, order="id DESC", search_cols=None):
        super().__init__(master,padding=12); self.user=user; self.title=title; self.table=table; self.fields=fields; self.selected=None; self.order=order
        self.vars={k:tk.StringVar() for k,_,_ in fields}; self.build(); self.load()
    def build(self):
        ttk.Label(self,text=self.title,font=("TkDefaultFont",18,"bold")).pack(anchor="w")
        form=ttk.LabelFrame(self,text="Information",padding=10);form.pack(fill="x",pady=8)
        for i,(label,key,values) in enumerate(self.fields):
            r,c=divmod(i,4); ttk.Label(form,text=label).grid(row=r*2,column=c,sticky="w",padx=4)
            w=ttk.Combobox(form,textvariable=self.vars[key],values=values,state="readonly") if values else ttk.Entry(form,textvariable=self.vars[key])
            w.grid(row=r*2+1,column=c,sticky="ew",padx=4,pady=(0,5)); form.columnconfigure(c,weight=1)
        bar=ttk.Frame(self);bar.pack(fill="x",pady=5)
        for t,c in [("➕ Add",self.add),("✏️ Update",self.update),("🗑 Delete",self.delete),("🧹 Clear",self.clear)]:
            ttk.Button(bar,text=t,command=c).pack(side="left",padx=3)
        self.tree=ttk.Treeview(self,columns=[x[1] for x in self.fields],show="headings")
        for _,k,_ in self.fields:self.tree.heading(k,text=k.replace("_"," ").title());self.tree.column(k,width=130)
        self.tree.pack(fill="both",expand=True,pady=8);self.tree.bind("<<TreeviewSelect>>",self.select)
    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        cols=",".join(k for _,k,_ in self.fields)
        for r in query(f"SELECT id,{cols} FROM {self.table} ORDER BY {self.order}"):
            self.tree.insert("", "end", iid=str(r["id"]), values=[r[k] for _,k,_ in self.fields])
    def select(self,_=None):
        item=self.tree.focus()
        if not item:return
        self.selected=int(item); r=query(f"SELECT * FROM {self.table} WHERE id=?",(self.selected,))[0]
        for _,k,_ in self.fields:self.vars[k].set(r[k] or "")
    def vals(self):return [self.vars[k].get().strip() for _,k,_ in self.fields]
    def add(self):
        v=self.vals()
        if not v[0]:messagebox.showwarning("Required","Required field is empty.");return
        cols=",".join(k for _,k,_ in self.fields); qs=",".join("?" for _ in v)
        try: execute(f"INSERT INTO {self.table} ({cols}) VALUES ({qs})",v);log_activity(self.user["username"],f"Added {self.title}");self.clear();self.load()
        except Exception as e:messagebox.showerror("Error",str(e))
    def update(self):
        if not self.selected:return
        v=self.vals(); cols=",".join(f"{k}=?" for _,k,_ in self.fields)
        try:execute(f"UPDATE {self.table} SET {cols} WHERE id=?",v+[self.selected]);log_activity(self.user["username"],f"Updated {self.title}");self.load()
        except Exception as e:messagebox.showerror("Error",str(e))
    def delete(self):
        if not self.selected:return
        if messagebox.askyesno("Confirm","Delete selected record?"):
            execute(f"DELETE FROM {self.table} WHERE id=?",(self.selected,));log_activity(self.user["username"],f"Deleted {self.title}");self.clear();self.load()
    def clear(self):
        self.selected=None
        for v in self.vars.values():v.set("")

class GuardianFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"👨‍👩‍👧 Parent / Guardian Management","guardians",[("Guardian ID","guardian_id",None),("Name","name",None),("Relation","relation",["Father","Mother","Guardian"]),("Phone","phone",None),("Email","email",None),("Address","address",None),("Emergency Contact","emergency_contact",None)])

class NoticeFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"📢 Notice & Notification","notices",[("Title","title",None),("Category","category",["General","Fee Due","Attendance","Exam/Result","Event"]),("Target Class","target_class",None),("Section","target_section",None),("Priority","priority",["Low","Normal","High","Urgent"]),("Message","message",None)])

class CalendarFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"📅 Academic Calendar","calendar_events",[("Title","title",None),("Type","event_type",["Holiday","Exam","Event","Meeting","Admission","Result","Vacation"]),("Start Date","start_date",None),("End Date","end_date",None),("Description","description",None)])

class TimetableFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"🗓️ Timetable","timetables",[("Class","class_name",None),("Section","section",None),("Day","day",["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]),("Period","period",None),("Subject","subject",None),("Teacher","teacher",None),("Room","room",None),("Start","start_time",None),("End","end_time",None)])

class HealthFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"🏥 Student Health Information","health_records",[("Student ID","student_id",None),("Blood Group","blood_group",["A+","A-","B+","B-","AB+","AB-","O+","O-"]),("Height","height",None),("Weight","weight",None),("Emergency Contact","emergency_contact",None),("Allergy / Medical Notes","allergy_notes",None),("Checkup Date","checkup_date",None),("Notes","notes",None)])

class EventFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"🎉 Events & Activities","events",[("Title","title",None),("Type","event_type",["Sports","Cultural","Debate","Science Fair","Educational Tour","Competition","General"]),("Date","event_date",None),("Venue","venue",None),("Description","description",None)])

class AwardFrame(CrudFrame):
    def __init__(self,m,u):super().__init__(m,u,"🏆 Student Awards","student_awards",[("Student ID","student_id",None),("Award Type","award_type",["Academic Award","Attendance Award","Sports Award","Cultural Award","Best Student"]),("Title","title",None),("Date","award_date",None),("Description","description",None)])

class PermissionsFrame(ttk.Frame):
    def __init__(self,m,u):
        super().__init__(m,padding=12);self.user=u;self.build();self.load()
    def build(self):
        ttk.Label(self,text="🔐 Advanced User Permissions",font=("TkDefaultFont",18,"bold")).pack(anchor="w")
        bar=ttk.Frame(self);bar.pack(fill="x",pady=8)
        self.role=tk.StringVar(value="Teacher");ttk.Label(bar,text="Role").pack(side="left");ttk.Combobox(bar,textvariable=self.role,values=["Admin","Teacher","Accountant","Receptionist","Staff"],state="readonly").pack(side="left",padx=6);ttk.Button(bar,text="Load",command=self.load).pack(side="left")
        self.tree=ttk.Treeview(self,columns=("module","view","add","edit","delete"),show="headings")
        for c in self.tree["columns"]:self.tree.heading(c,text=c.title());self.tree.column(c,width=140)
        self.tree.pack(fill="both",expand=True)
        ttk.Label(self,text="Double-click a permission cell to toggle. Admin permissions are always treated as full access.",foreground="#666").pack(anchor="w",pady=5)
        self.tree.bind("<Double-1>",self.toggle)
    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        for r in query("SELECT module,can_view,can_add,can_edit,can_delete FROM permissions WHERE role=? ORDER BY module",(self.role.get(),)):
            self.tree.insert("", "end",values=(r["module"],"✓" if r["can_view"] else "—","✓" if r["can_add"] else "—","✓" if r["can_edit"] else "—","✓" if r["can_delete"] else "—"))
    def toggle(self,e):
        if self.role.get()=="Admin":return
        item=self.tree.identify_row(e.y);col=self.tree.identify_column(e.x)
        if not item or col not in ("#2","#3","#4","#5"):return
        idx=int(col[1:])-2; key=["can_view","can_add","can_edit","can_delete"][idx]; module=self.tree.item(item)["values"][0]
        r=query(f"SELECT {key} FROM permissions WHERE role=? AND module=?",(self.role.get(),module))[0]
        execute(f"UPDATE permissions SET {key}=? WHERE role=? AND module=?",(0 if r[key] else 1,self.role.get(),module));log_activity(self.user["username"],f"Changed permission {self.role.get()} {module} {key}");self.load()

class LogsFrame(ttk.Frame):
    def __init__(self,m,u):
        super().__init__(m,padding=12);ttk.Label(self,text="🧾 Advanced Activity Logs",font=("TkDefaultFont",18,"bold")).pack(anchor="w")
        tree=ttk.Treeview(self,columns=("user","date","action"),show="headings")
        for c in tree["columns"]:tree.heading(c,text=c.title());tree.column(c,width=180)
        tree.pack(fill="both",expand=True,pady=8)
        for r in query("SELECT username,created_at,action FROM activity_logs ORDER BY id DESC"):
            tree.insert("", "end",values=(r["username"],r["created_at"],r["action"]))
