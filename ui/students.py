import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, json
from datetime import datetime
from pathlib import Path
from shutil import copy2
from database.db import query, execute, log_activity
from config import STUDENT_PHOTO_DIR
from utils.permissions import require_admin
from utils.popup import PopupForm
from utils.profiles import export_pdf
from utils.helpers import today

class StudentFrame(ttk.Frame):
    def __init__(self, master, user, refresh_dashboard=None):
        super().__init__(master,padding=12)
        self.user=user
        self.refresh_dashboard=refresh_dashboard
        self.selected_id=None
        keys=["student_id","name","gender","dob","father","mother","phone","guardian_phone","emergency_contact","blood_group","academic_year","address","class_name","section","roll","admission_date","status","photo_path"]
        self.vars={k:tk.StringVar() for k in keys}
        self.vars["status"].set("Active")
        self.build(); self.load()

    def build(self):
        form=ttk.LabelFrame(self,text="👨‍🎓 শিক্ষার্থী তথ্য",padding=10); form.pack(fill="x")
        fields=[("Student ID","student_id"),("নাম","name"),("Gender","gender"),("Date of Birth","dob"),
            ("পিতার নাম","father"),("মাতার নাম","mother"),("মোবাইল","phone"),("Guardian Phone","guardian_phone"),
            ("Emergency Contact","emergency_contact"),("Blood Group","blood_group"),("Academic Year","academic_year"),("ঠিকানা","address"),
                ("Class","class_name"),("Section","section"),("Roll","roll"),("Admission Date","admission_date"),("Status","status")]
        for i,(lab,key) in enumerate(fields):
            r,c=divmod(i,3)
            ttk.Label(form,text=lab).grid(row=r*2,column=c,sticky="w",padx=4,pady=(2,0))
            if key=="gender":widget=ttk.Combobox(form,textvariable=self.vars[key],values=["Male","Female","Other"],state="readonly")
            elif key=="blood_group":widget=ttk.Combobox(form,textvariable=self.vars[key],values=["A+","A-","B+","B-","AB+","AB-","O+","O-"],state="readonly")
            elif key=="status":widget=ttk.Combobox(form,textvariable=self.vars[key],values=["Active","Inactive","Transferred","Graduated"],state="readonly")
            elif key=="class_name":widget=ttk.Combobox(form,textvariable=self.vars[key],state="normal")
            elif key=="section":widget=ttk.Combobox(form,textvariable=self.vars[key],values=["A","B","C","D"],state="normal")
            else:widget=ttk.Entry(form,textvariable=self.vars[key])
            widget.grid(row=r*2+1,column=c,sticky="ew",padx=4,pady=(0,5))
        for c in range(3): form.columnconfigure(c,weight=1)
        form.pack_forget()

        actions=ttk.Frame(self); actions.pack(fill="x",pady=8)
        ttk.Button(actions,text="➕ Add Student",command=self.popup_add).pack(side="left",padx=3)
        ttk.Button(actions,text="✏️ Edit Student",command=self.popup_edit).pack(side="left",padx=3)
        ttk.Button(actions,text="🗑 Delete",command=self.delete).pack(side="left",padx=3)
        ttk.Button(actions,text="🖼️ Choose Photo",command=self.photo).pack(side="left",padx=3)
        ttk.Button(actions,text="⬆️ Promote",command=self.promote).pack(side="left",padx=3)
        ttk.Button(actions,text="📥 Import CSV",command=self.import_csv).pack(side="left",padx=3)
        ttk.Button(actions,text="🗃 Archive",command=self.archive_view).pack(side="left",padx=3)
        ttk.Button(actions,text="👁 Profile",command=self.show_profile).pack(side="left",padx=3)
        ttk.Button(actions,text="🧹 Clear",command=self.clear).pack(side="left",padx=3)

        s=ttk.Frame(self); s.pack(fill="x")
        self.search=tk.StringVar()
        ttk.Label(s,text="🔎 Search").pack(side="left")
        search_entry=ttk.Entry(s,textvariable=self.search,width=35);search_entry.pack(side="left",padx=6);search_entry.bind("<Return>",lambda _event:self.load())
        ttk.Button(s,text="Search",command=self.load).pack(side="left")
        self.tree=ttk.Treeview(self,columns=("id","name","class","section","roll","phone","status","photo"),show="headings")
        heads={"id":"Student ID","name":"নাম","class":"Class","section":"Section","roll":"Roll","phone":"মোবাইল","status":"Status","photo":"Photo"}
        for c in heads:
            self.tree.heading(c,text=heads[c]); self.tree.column(c,width=110)
        self.tree.column("name",width=180); self.tree.column("photo",width=60)
        self.tree.pack(fill="both",expand=True,pady=8)
        self.tree.bind("<<TreeviewSelect>>",self.select)

    def values(self):
        return {k:v.get().strip() for k,v in self.vars.items()}

    def popup_fields(self):
        classes=[row["class_name"] for row in query("SELECT DISTINCT class_name FROM classes ORDER BY class_name")]
        return [("Student ID","student_id",None),("Name","name",None),("Gender","gender",["Male","Female","Other"]),("Date of Birth","dob",None,"date"),("Father","father",None),("Mother","mother",None),("Phone","phone",None),("Guardian Phone","guardian_phone",None),("Emergency Contact","emergency_contact",None),("Blood Group","blood_group",["A+","A-","B+","B-","AB+","AB-","O+","O-"]),("Academic Year","academic_year",None),("Address","address",None),("Class","class_name",classes),("Section","section",["A","B","C","D"]),("Roll","roll",None),("Admission Date","admission_date",None,"date"),("Status","status",["Active","Inactive","Transferred","Graduated"])]

    def popup_add(self):
        PopupForm(self,"Add Student",self.popup_fields(),{"admission_date":today()},on_save=lambda values:self.popup_save(values,False),on_change=self.auto_student_fields)

    def popup_edit(self):
        if not self.selected_id:return messagebox.showwarning("Select","আগে একজন শিক্ষার্থী নির্বাচন করুন।")
        PopupForm(self,"Edit Student",self.popup_fields(),self.values(),on_save=lambda values:self.popup_save(values,True),on_change=self.auto_student_id)

    def auto_student_id(self, variables):
        if "student_id" not in variables or variables["student_id"].get().strip():return
        class_name=variables["class_name"].get().strip()
        section=variables["section"].get().strip()
        roll=variables["roll"].get().strip()
        if class_name and roll:
            class_code="".join(char for char in class_name.upper() if char.isalnum())[-8:]
            section_code="".join(char for char in section.upper() if char.isalnum())[:3] or "A"
            variables["student_id"].set(f"{class_code}-{section_code}-{roll.zfill(3)}")

    def auto_student_fields(self, variables):
        class_name=variables["class_name"].get().strip()
        section=variables["section"].get().strip()
        if class_name and section and not variables["roll"].get().strip():
            row=query("SELECT COALESCE(MAX(CAST(roll AS INTEGER)),0) maximum FROM students WHERE class_name=? AND section=?",(class_name,section))[0]
            variables["roll"].set(str(int(row["maximum"] or 0)+1))
        self.auto_student_id(variables)

    def popup_save(self,values,editing):
        for key,value in values.items():self.vars[key].set(value)
        if editing:self.update()
        else:self.add()
        return True

    def add(self):
        v=self.values()
        if not v["student_id"] or not v["name"]:
            messagebox.showwarning("Required","Student ID এবং নাম আবশ্যক."); return
        if not v["roll"] or not v["roll"].isdigit() or int(v["roll"])<1:
            messagebox.showwarning("Invalid Roll","Roll number 1 বা তার বেশি হতে হবে।");return
        if v["phone"] and not v["phone"].replace("+","").replace("-","").replace(" ","").isdigit():
            messagebox.showwarning("Invalid Phone","Phone number সঠিক নয়।");return
        for key in ["dob","admission_date"]:
            if v[key]:
                try:datetime.strptime(v[key],"%Y-%m-%d")
                except ValueError:messagebox.showwarning("Invalid Date",f"{key} YYYY-MM-DD format-এ দিন।");return
        try:
            execute("""INSERT INTO students
            (student_id,name,gender,date_of_birth,father_name,mother_name,phone,guardian_phone,emergency_contact,blood_group,academic_year,address,class_name,section,roll,admission_date,status,photo_path)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v["student_id"],v["name"],v["gender"],v["dob"],v["father"],v["mother"],v["phone"],v["guardian_phone"],v["emergency_contact"],v["blood_group"],v["academic_year"],v["address"],v["class_name"],v["section"],v["roll"],v["admission_date"],v["status"],v["photo_path"]))
            log_activity(self.user["username"],f"Added student {v['student_id']}")
            messagebox.showinfo("Success","শিক্ষার্থী যোগ হয়েছে."); self.clear(); self.load()
            if self.refresh_dashboard:self.refresh_dashboard()
        except Exception as e: messagebox.showerror("Error",str(e))

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Select","আগে একজন শিক্ষার্থী নির্বাচন করুন."); return
        v=self.values()
        if v["roll"] and (not v["roll"].isdigit() or int(v["roll"])<1):
            messagebox.showwarning("Invalid Roll","Roll number 1 বা তার বেশি হতে হবে।");return
        if v["phone"] and not v["phone"].replace("+","").replace("-","").replace(" ","").isdigit():
            messagebox.showwarning("Invalid Phone","Phone number সঠিক নয়।");return
        for key in ["dob","admission_date"]:
            if v[key]:
                try:datetime.strptime(v[key],"%Y-%m-%d")
                except ValueError:messagebox.showwarning("Invalid Date",f"{key} YYYY-MM-DD format-এ দিন।");return
        try:
            execute("""UPDATE students SET student_id=?,name=?,gender=?,date_of_birth=?,father_name=?,mother_name=?,
            phone=?,guardian_phone=?,emergency_contact=?,blood_group=?,academic_year=?,address=?,class_name=?,section=?,roll=?,admission_date=?,status=?,photo_path=? WHERE id=?""",
            (v["student_id"],v["name"],v["gender"],v["dob"],v["father"],v["mother"],v["phone"],v["guardian_phone"],v["emergency_contact"],v["blood_group"],v["academic_year"],v["address"],v["class_name"],v["section"],v["roll"],v["admission_date"],v["status"],v["photo_path"],self.selected_id))
            log_activity(self.user["username"],f"Updated student {v['student_id']}")
            messagebox.showinfo("Success","শিক্ষার্থীর তথ্য আপডেট হয়েছে."); self.load()
        except Exception as e: messagebox.showerror("Error",str(e))

    def delete(self):
        if not self.selected_id:return
        if not require_admin(self.user, messagebox, "শিক্ষার্থী delete"):return
        if not messagebox.askyesno("Confirm","এই শিক্ষার্থীকে Delete করবেন?"):return
        sid=self.vars["student_id"].get()
        record=dict(query("SELECT * FROM students WHERE id=?",(self.selected_id,))[0])
        record={key:record[key] for key in record.keys()}
        execute("INSERT INTO student_archive(student_id,record_json,archived_by) VALUES(?,?,?)",(sid,json.dumps(record,ensure_ascii=False),self.user["username"]))
        execute("DELETE FROM students WHERE id=?",(self.selected_id,))
        log_activity(self.user["username"],f"Archived student {sid}")
        self.clear(); self.load()
        if self.refresh_dashboard:self.refresh_dashboard()

    def archive_view(self):
        if not require_admin(self.user, messagebox, "archive view"):return
        win=tk.Toplevel(self);win.title("Student Archive");win.geometry("720x420");win.transient(self.winfo_toplevel())
        tree=ttk.Treeview(win,columns=("id","student","name","class","archived","by"),show="headings")
        for column,title,width in [("id","Archive ID",90),("student","Student ID",130),("name","Name",190),("class","Class",120),("archived","Archived At",150),("by","By",100)]:
            tree.heading(column,text=title);tree.column(column,width=width)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        def load():
            for item in tree.get_children():tree.delete(item)
            for row in query("SELECT id,student_id,record_json,archived_by,archived_at FROM student_archive ORDER BY id DESC"):
                data=json.loads(row["record_json"]);tree.insert("","end",iid=str(row["id"]),values=(row["id"],row["student_id"],data.get("name",""),f"{data.get('class_name','')} {data.get('section','')}",row["archived_at"],row["archived_by"]))
        def restore():
            item=tree.focus()
            if not item:return
            row=query("SELECT * FROM student_archive WHERE id=?",(item,))[0];data=json.loads(row["record_json"]);data.pop("id",None)
            columns=[key for key in data if key != "created_at"];values=[data[key] for key in columns]
            try:
                execute(f"INSERT INTO students ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",values)
                execute("DELETE FROM student_archive WHERE id=?",(item,));log_activity(self.user["username"],f"Restored student {row['student_id']} from archive");load();self.load()
            except Exception as error:messagebox.showerror("Restore Error",str(error),parent=win)
        ttk.Button(win,text="♻️ Restore Selected",command=restore).pack(pady=(0,12));load()

    def photo(self):
        if not self.selected_id and not self.vars["student_id"].get().strip():
            messagebox.showwarning("Photo","আগে Student ID দিন/Student নির্বাচন করুন."); return
        path=filedialog.askopenfilename(title="Select Student Photo",filetypes=[("Images","*.png *.jpg *.jpeg *.gif")])
        if not path:return
        sid=self.vars["student_id"].get().strip()
        ext=Path(path).suffix.lower()
        target=STUDENT_PHOTO_DIR/f"{sid}{ext}"
        copy2(path,target)
        self.vars["photo_path"].set(str(target))
        if self.selected_id:
            execute("UPDATE students SET photo_path=? WHERE id=?",(str(target),self.selected_id))
            log_activity(self.user["username"],f"Updated photo for student {sid}")
        messagebox.showinfo("Photo","Student photo সংরক্ষণ হয়েছে।")

    def promote(self):
        if not self.selected_id:
            messagebox.showwarning("Select","আগে একজন শিক্ষার্থী নির্বাচন করুন।");return
        if self.user.get("role") != "Admin":
            messagebox.showwarning("Admin Required","Student promote করতে Admin permission প্রয়োজন।");return
        win=tk.Toplevel(self);win.title("Promote Student");win.geometry("420x230");win.transient(self.winfo_toplevel())
        new_class=tk.StringVar(value=self.vars["class_name"].get());new_section=tk.StringVar(value=self.vars["section"].get())
        classes=[r["class_name"] for r in query("SELECT DISTINCT class_name FROM classes ORDER BY class_name")]
        for row,(label,var) in enumerate([("New Class",new_class),("New Section",new_section)]):
            ttk.Label(win,text=label).grid(row=row,column=0,padx=14,pady=12,sticky="w")
            widget=ttk.Combobox(win,textvariable=var,values=classes if row==0 else [],state="normal",width=25)
            widget.grid(row=row,column=1,padx=14,pady=12,sticky="ew")
        win.columnconfigure(1,weight=1)
        def save():
            if not new_class.get().strip() or not new_section.get().strip():
                messagebox.showwarning("Required","Class এবং Section আবশ্যক।",parent=win);return
            old=f"{self.vars['class_name'].get()}-{self.vars['section'].get()}"
            execute("INSERT INTO promotion_history(student_id,from_class,from_section,to_class,to_section,promoted_by) VALUES(?,?,?,?,?,?)",(self.vars["student_id"].get(),self.vars["class_name"].get(),self.vars["section"].get(),new_class.get().strip(),new_section.get().strip(),self.user["username"]))
            execute("UPDATE students SET class_name=?,section=? WHERE id=?",(new_class.get().strip(),new_section.get().strip(),self.selected_id))
            log_activity(self.user["username"],f"Promoted student {self.vars['student_id'].get()} from {old} to {new_class.get().strip()}-{new_section.get().strip()}")
            self.vars["class_name"].set(new_class.get().strip());self.vars["section"].set(new_section.get().strip())
            win.destroy();self.load();messagebox.showinfo("Success","Student promote হয়েছে।")
        ttk.Button(win,text="⬆️ Promote",command=save).grid(row=2,column=0,columnspan=2,pady=12)

    def show_profile(self):
        if not self.selected_id:return messagebox.showwarning("Select","আগে একজন শিক্ষার্থী নির্বাচন করুন।")
        student=query("SELECT * FROM students WHERE id=?",(self.selected_id,))[0]
        attendance=query("SELECT COUNT(*) total,SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) present FROM attendance WHERE person_type='Student' AND person_id=?",(student["student_id"],))[0]
        fees=query("SELECT COALESCE(SUM(amount),0) paid FROM fee_payments WHERE student_id=?",(student["student_id"],))[0]
        due=query("SELECT COALESCE(SUM(amount),0) total FROM student_fees WHERE student_id=? AND status='Due'",(student["student_id"],))[0]
        win=tk.Toplevel(self);win.title(f"Student Profile - {student['name']}");win.geometry("620x560");win.transient(self.winfo_toplevel())
        ttk.Label(win,text=student["name"],font=("TkDefaultFont",20,"bold")).pack(anchor="w",padx=20,pady=(18,2))
        ttk.Label(win,text=f"{student['student_id']}  •  {student['class_name']} {student['section']}",foreground="#5d7180").pack(anchor="w",padx=20)
        summary=ttk.LabelFrame(win,text="Overview",padding=12);summary.pack(fill="x",padx=20,pady=16)
        attendance_rate=(float(attendance["present"] or 0)/int(attendance["total"])*100) if attendance["total"] else 0
        ttk.Label(summary,text=f"Attendance: {attendance_rate:.1f}%   |   Paid: ৳ {float(fees['paid']):,.2f}   |   Due: ৳ {float(due['total']):,.2f}").pack(anchor="w")
        details=ttk.LabelFrame(win,text="Student Information",padding=12);details.pack(fill="both",expand=True,padx=20,pady=(0,20))
        for label,value in [("Gender",student["gender"]),("Date of Birth",student["date_of_birth"]),("Father",student["father_name"]),("Mother",student["mother_name"]),("Guardian Phone",student["guardian_phone"]),("Emergency Contact",student["emergency_contact"]),("Blood Group",student["blood_group"]),("Academic Year",student["academic_year"]),("Address",student["address"])]:
            ttk.Label(details,text=f"{label}: {value or '-'}").pack(anchor="w",pady=3)
        history=query("SELECT from_class,from_section,to_class,to_section,promoted_at FROM promotion_history WHERE student_id=? ORDER BY id DESC LIMIT 5",(student["student_id"],))
        if history:
            ttk.Label(details,text="Recent Promotions",font=("TkDefaultFont",10,"bold")).pack(anchor="w",pady=(10,2))
            for row in history:ttk.Label(details,text=f"{row['from_class']} {row['from_section']} → {row['to_class']} {row['to_section']} ({row['promoted_at']})").pack(anchor="w")
        fields=[("Student ID","student_id"),("Name","name"),("Gender","gender"),("Date of Birth","date_of_birth"),("Father","father_name"),("Mother","mother_name"),("Guardian Phone","guardian_phone"),("Emergency Contact","emergency_contact"),("Blood Group","blood_group"),("Academic Year","academic_year"),("Class","class_name"),("Section","section"),("Roll","roll"),("Status","status")]
        ttk.Button(win,text="📕 Export Profile PDF",command=lambda:export_pdf("Student Profile - "+student["name"],dict(student),fields)).pack(pady=(0,14))

    def import_csv(self):
        if self.user.get("role") != "Admin":
            messagebox.showwarning("Admin Required","CSV import করতে Admin permission প্রয়োজন।");return
        path=filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path:return
        required={"student_id","name"};imported=0;skipped=0
        try:
            with open(path,"r",encoding="utf-8-sig",newline="") as source:
                reader=csv.DictReader(source)
                if not required.issubset(set(reader.fieldnames or [])):raise ValueError("CSV must contain student_id and name columns")
                for row in reader:
                    values={key:(row.get(key) or "").strip() for key in ["student_id","name","gender","date_of_birth","father_name","mother_name","phone","address","class_name","section","roll","admission_date","status","photo_path"]}
                    if not values["student_id"] or not values["name"]:skipped+=1;continue
                    try:
                        execute("""INSERT INTO students(student_id,name,gender,date_of_birth,father_name,mother_name,phone,address,class_name,section,roll,admission_date,status,photo_path)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",tuple(values.values()));imported+=1
                    except Exception:skipped+=1
            log_activity(self.user["username"],f"Imported students CSV: {imported} added, {skipped} skipped")
            self.load();messagebox.showinfo("Import Complete",f"Imported: {imported}\nSkipped: {skipped}")
        except Exception as e:messagebox.showerror("Import Error",str(e))

    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        term=f"%{self.search.get().strip()}%"
        rows=query("""SELECT student_id,name,class_name,section,roll,phone,status,photo_path
        FROM students WHERE student_id LIKE ? OR name LIKE ? OR class_name LIKE ? OR phone LIKE ?
        ORDER BY id DESC""",(term,term,term,term))
        for r in rows:self.tree.insert("", "end",values=(r["student_id"],r["name"],r["class_name"],r["section"],r["roll"],r["phone"],r["status"],"✓" if r["photo_path"] else ""))

    def select(self,_=None):
        item=self.tree.focus()
        if not item:return
        sid=self.tree.item(item)["values"][0]
        rows=query("SELECT * FROM students WHERE student_id=?",(sid,))
        if not rows:return
        r=rows[0]; self.selected_id=r["id"]
        mp={"student_id":"student_id","name":"name","gender":"gender","dob":"date_of_birth","father":"father_name","mother":"mother_name","phone":"phone","address":"address","class_name":"class_name","section":"section","roll":"roll","admission_date":"admission_date","status":"status","photo_path":"photo_path"}
        for k,c in mp.items():self.vars[k].set(r[c] or "")

    def clear(self):
        self.selected_id=None
        for v in self.vars.values():v.set("")
        self.vars["status"].set("Active")
