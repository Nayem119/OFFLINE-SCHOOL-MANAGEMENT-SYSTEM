import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, execute, log_activity
from datetime import datetime
from utils.permissions import require_admin
from utils.popup import PopupForm
from utils.profiles import open_profile

class PersonFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master,padding=12)
        self.user=user; self.selected_id=None
        self.fields=[('Teacher ID', 'teacher_id'), ('নাম', 'name'), ('Subject', 'subject'), ('Phone', 'phone'), ('Email', 'email'), ('Address', 'address'), ('Joining Date', 'joining_date'), ('Designation', 'designation'), ('Salary', 'salary'), ('Status', 'status')]
        self.vars={k:tk.StringVar() for _,k in self.fields}
        self.vars["status"].set("Active")
        self.build(); self.load()

    def build(self):
        box=ttk.LabelFrame(self,text="👨‍🏫 Teacher Management",padding=10); box.pack(fill="x")
        for i,(lab,key) in enumerate(self.fields):
            r,c=divmod(i,3)
            ttk.Label(box,text=lab).grid(row=r*2,column=c,sticky="w",padx=4,pady=(2,0))
            widget=ttk.Combobox(box,textvariable=self.vars[key],values=["Active","Inactive","On Leave","Retired"],state="readonly") if key=="status" else ttk.Entry(box,textvariable=self.vars[key])
            widget.grid(row=r*2+1,column=c,sticky="ew",padx=4,pady=(0,5))
        for c in range(3):box.columnconfigure(c,weight=1)
        box.pack_forget()
        a=ttk.Frame(self);a.pack(fill="x",pady=8)
        ttk.Button(a,text="➕ Add Teacher",command=self.popup_add).pack(side="left",padx=3)
        ttk.Button(a,text="✏️ Edit Teacher",command=self.popup_edit).pack(side="left",padx=3)
        ttk.Button(a,text="🗑 Delete",command=self.delete).pack(side="left",padx=3)
        ttk.Button(a,text="👁 Profile / PDF",command=self.show_profile).pack(side="left",padx=3)
        ttk.Button(a,text="🧹 Clear",command=self.clear).pack(side="left",padx=3)
        s=ttk.Frame(self);s.pack(fill="x")
        self.search=tk.StringVar()
        ttk.Label(s,text="🔎 Search").pack(side="left")
        search_entry=ttk.Entry(s,textvariable=self.search,width=35);search_entry.pack(side="left",padx=6);search_entry.bind("<Return>",lambda _event:self.load())
        ttk.Button(s,text="Search",command=self.load).pack(side="left")
        self.tree=ttk.Treeview(self,columns=('id', 'name', 'subject', 'phone', 'designation', 'salary', 'status'),show="headings")
        for c,h in zip(('id', 'name', 'subject', 'phone', 'designation', 'salary', 'status'),('ID', 'নাম', 'Subject', 'Phone', 'Designation', 'Salary', 'Status')):
            self.tree.heading(c,text=h);self.tree.column(c,width=120)
        self.tree.column("name",width=180)
        self.tree.pack(fill="both",expand=True,pady=8)
        self.tree.bind("<<TreeviewSelect>>",self.select)

    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        term=f"%{self.search.get().strip()}%"
        rows=query("SELECT * FROM teachers WHERE name LIKE ? OR phone LIKE ? OR teacher_id LIKE ? ORDER BY id DESC",(term,term,term))
        for r in rows:
            self.tree.insert("", "end",values=tuple(r[c] for c in ('id', 'name', 'subject', 'phone', 'designation', 'salary', 'status')))

    def popup_add(self):PopupForm(self,"Add Teacher",[(label,key,["Active","Inactive","On Leave","Retired"] if key=="status" else None) for label,key in self.fields],on_save=lambda values:self.popup_save(values,False))
    def popup_edit(self):
        if not self.selected_id:return messagebox.showwarning("Select","আগে একটি record নির্বাচন করুন।")
        PopupForm(self,"Edit Teacher",[(label,key,["Active","Inactive","On Leave","Retired"] if key=="status" else None) for label,key in self.fields],self.values(),on_save=lambda values:self.popup_save(values,True))
    def values(self):return {key:variable.get().strip() for key,variable in self.vars.items()}
    def popup_save(self,values,editing):
        for key,value in values.items():self.vars[key].set(value)
        if editing:self.update()
        else:self.add()
        return True

    def add(self):
        v={k:x.get().strip() for k,x in self.vars.items()}
        ident=v["teacher_id" if "teachers"=="teachers" else "staff_id"]
        if not ident or not v["name"]:
            messagebox.showwarning("Required","ID এবং নাম আবশ্যক।");return
        if not self.valid_values(v):return
        try:
            cols=[x[1] for x in self.fields]
            vals=[v[x] for x in cols]
            placeholders=",".join("?"*len(cols))
            execute("INSERT INTO teachers ("+",".join(cols)+") VALUES ("+placeholders+")",vals)
            log_activity(self.user["username"],"Added Teacher "+ident)
            messagebox.showinfo("Success","Teacher যোগ হয়েছে।");self.clear();self.load()
        except Exception as e:messagebox.showerror("Error",str(e))

    def select(self,_=None):
        item=self.tree.focus()
        if not item:return
        ident=self.tree.item(item)["values"][0]
        key="teacher_id" if "teachers"=="teachers" else "staff_id"
        rows=query("SELECT * FROM teachers WHERE "+key+"=?",(ident,))
        if rows:
            r=rows[0];self.selected_id=r["id"]
            for k in self.vars:self.vars[k].set(r[k] if k in r.keys() and r[k] is not None else "")

    def show_profile(self):
        if not self.selected_id:return messagebox.showwarning("Select","আগে একজন teacher নির্বাচন করুন।")
        record=dict(query("SELECT * FROM teachers WHERE id=?",(self.selected_id,))[0])
        fields=[("Teacher ID","teacher_id"),("Name","name"),("Subject","subject"),("Phone","phone"),("Email","email"),("Address","address"),("Joining Date","joining_date"),("Designation","designation"),("Salary","salary"),("Status","status")]
        open_profile(self,"Teacher Profile - "+record["name"],record,fields)

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Select","আগে একটি record নির্বাচন করুন।");return
        v={k:x.get().strip() for k,x in self.vars.items()}
        if not self.valid_values(v):return
        try:
            sets=",".join(k+"=?" for k in self.vars)
            execute("UPDATE teachers SET "+sets+" WHERE id=?",list(v.values())+[self.selected_id])
            log_activity(self.user["username"],"Updated Teacher "+v["name"])
            messagebox.showinfo("Success","তথ্য আপডেট হয়েছে।");self.load()
        except Exception as e:messagebox.showerror("Error",str(e))

    @staticmethod
    def valid_values(values):
        try:
            if float(values["salary"] or 0)<0:raise ValueError
            if values["joining_date"]:datetime.strptime(values["joining_date"],"%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Data","Salary বা joining date সঠিক নয়।");return False
        return True

    def delete(self):
        if not self.selected_id:return
        if not require_admin(self.user, messagebox, "শিক্ষক delete"):return
        if not messagebox.askyesno("Confirm","এই record Delete করবেন?"):return
        execute("DELETE FROM teachers WHERE id=?",(self.selected_id,))
        log_activity(self.user["username"],"Deleted Teacher")
        self.clear();self.load()

    def clear(self):
        self.selected_id=None
        for v in self.vars.values():v.set("")
        self.vars["status"].set("Active")
