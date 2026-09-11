import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, execute, log_activity

class ClassesFrame(ttk.Frame):
    def __init__(self,master,user):
        super().__init__(master,padding=12);self.user=user
        self.selected_class=None;self.selected_subject=None
        self.name=tk.StringVar();self.section=tk.StringVar(value="A");self.teacher=tk.StringVar()
        self.build();self.load()
    def build(self):
        nb=ttk.Notebook(self);nb.pack(fill="both",expand=True)
        class_tab=ttk.Frame(nb,padding=8);subject_tab=ttk.Frame(nb,padding=8)
        nb.add(class_tab,text="📚 Classes & Sections");nb.add(subject_tab,text="📖 Class Subjects")
        b=ttk.LabelFrame(class_tab,text="📚 Class & Section",padding=10);b.pack(fill="x")
        for i,(l,v) in enumerate([("Class Name",self.name),("Section",self.section),("Class Teacher",self.teacher)]):
            ttk.Label(b,text=l).grid(row=0,column=i,sticky="w",padx=5);ttk.Entry(b,textvariable=v).grid(row=1,column=i,sticky="ew",padx=5);b.columnconfigure(i,weight=1)
        a=ttk.Frame(class_tab);a.pack(fill="x",pady=8)
        ttk.Button(a,text="➕ Add",command=self.add).pack(side="left",padx=3);ttk.Button(a,text="✏️ Update",command=self.update).pack(side="left",padx=3);ttk.Button(a,text="🗑 Remove",command=self.delete).pack(side="left",padx=3);ttk.Button(a,text="🧹 Clear",command=self.clear).pack(side="left",padx=3)
        self.tree=ttk.Treeview(class_tab,columns=("id","class","section","teacher"),show="headings")
        for c,h in [("id","ID"),("class","Class"),("section","Section"),("teacher","Class Teacher")]:self.tree.heading(c,text=h);self.tree.column(c,width=180)
        self.tree.pack(fill="both",expand=True)
        self.tree.bind("<<TreeviewSelect>>",self.select_class)

        subject_form=ttk.LabelFrame(subject_tab,text="📖 Add Subject to Class",padding=10);subject_form.pack(fill="x")
        self.subject_vars={key:tk.StringVar() for key in ["code","name","full","pass","class_name","section"]}
        self.subject_vars["full"].set("100");self.subject_vars["pass"].set("33")
        subject_fields=[("Subject Code","code"),("Subject Name","name"),("Full Marks","full"),("Pass Marks","pass"),("Class","class_name"),("Section","section")]
        for i,(label,key) in enumerate(subject_fields):
            ttk.Label(subject_form,text=label).grid(row=0,column=i,padx=4,sticky="w")
            if key=="class_name":widget=ttk.Combobox(subject_form,textvariable=self.subject_vars[key],state="readonly")
            else:widget=ttk.Entry(subject_form,textvariable=self.subject_vars[key])
            widget.grid(row=1,column=i,padx=4,sticky="ew");subject_form.columnconfigure(i,weight=1)
            if key=="class_name":self.subject_class_combo=widget
        ttk.Button(subject_form,text="➕ Add Subject",command=self.add_subject).grid(row=1,column=6,padx=8)
        ttk.Button(subject_form,text="✏️ Update",command=self.update_subject).grid(row=1,column=7,padx=4)
        ttk.Button(subject_form,text="🗑 Remove",command=self.delete_subject).grid(row=1,column=8,padx=4)
        self.subject_tree=ttk.Treeview(subject_tab,columns=("id","code","name","class","section","full","pass"),show="headings")
        for column,title in [("id","ID"),("code","Code"),("name","Subject"),("class","Class"),("section","Section"),("full","Full Marks"),("pass","Pass Marks")]:
            self.subject_tree.heading(column,text=title);self.subject_tree.column(column,width=120)
        self.subject_tree.column("name",width=180);self.subject_tree.pack(fill="both",expand=True,pady=8)
        self.subject_tree.bind("<<TreeviewSelect>>",self.select_subject)
        self.load_subjects()
    def add(self):
        if not self.name.get().strip():messagebox.showwarning("Required","Class Name আবশ্যক।");return
        try:
            execute("INSERT INTO classes(class_name,section,class_teacher) VALUES(?,?,?)",(self.name.get().strip(),self.section.get().strip() or "A",self.teacher.get().strip()))
            log_activity(self.user["username"],"Added class "+self.name.get().strip());self.clear();self.load()
        except Exception as e:messagebox.showerror("Error",str(e))
    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        for r in query("SELECT id,class_name,section,class_teacher FROM classes ORDER BY class_name,section"):self.tree.insert("", "end",values=tuple(r))
        if hasattr(self,"subject_class_combo"):
            self.subject_class_combo["values"]=[f"{r['class_name']} | {r['section']}" for r in query("SELECT class_name,section FROM classes ORDER BY class_name,section")]

    def select_class(self,_=None):
        item=self.tree.focus()
        if not item:return
        values=self.tree.item(item)["values"];self.selected_class=values[0];self.name.set(values[1]);self.section.set(values[2]);self.teacher.set(values[3])

    def update(self):
        if not self.selected_class:return messagebox.showwarning("Select","আগে একটি class নির্বাচন করুন।")
        if not self.name.get().strip():return messagebox.showwarning("Required","Class Name আবশ্যক।")
        try:
            execute("UPDATE classes SET class_name=?,section=?,class_teacher=? WHERE id=?",(self.name.get().strip(),self.section.get().strip() or "A",self.teacher.get().strip(),self.selected_class));log_activity(self.user["username"],"Updated class "+self.name.get().strip());self.clear();self.load()
        except Exception as e:messagebox.showerror("Error",str(e))

    def delete(self):
        if not self.selected_class:return messagebox.showwarning("Select","আগে একটি class নির্বাচন করুন।")
        if not messagebox.askyesno("Confirm","এই class remove করবেন?"):return
        execute("DELETE FROM classes WHERE id=?",(self.selected_class,));log_activity(self.user["username"],"Removed class");self.clear();self.load()

    def add_subject(self):
        values={key:var.get().strip() for key,var in self.subject_vars.items()}
        if not values["code"] or not values["name"] or not values["class_name"]:
            return messagebox.showwarning("Required","Subject code, name এবং class আবশ্যক।")
        try:
            full=float(values["full"]);passed=float(values["pass"])
            if full<=0 or passed<0 or passed>full:raise ValueError("Pass marks must be between 0 and full marks")
            class_name,section=[part.strip() for part in values["class_name"].split("|",1)]
            execute("INSERT INTO subjects(subject_code,subject_name,full_marks,pass_marks,class_name,section) VALUES(?,?,?,?,?,?)",(values["code"],values["name"],full,passed,class_name,values["section"] or section))
            log_activity(self.user["username"],f"Added subject {values['name']} to {class_name}");self.load_subjects();self.clear_subject()
        except Exception as e:messagebox.showerror("Error",str(e))

    def load_subjects(self):
        if not hasattr(self,"subject_tree"):return
        for item in self.subject_tree.get_children():self.subject_tree.delete(item)
        for row in query("SELECT id,subject_code,subject_name,class_name,section,full_marks,pass_marks FROM subjects ORDER BY class_name,section,subject_name"):
            self.subject_tree.insert("","end",values=tuple(row))

    def select_subject(self,_=None):
        item=self.subject_tree.focus()
        if not item:return
        values=self.subject_tree.item(item)["values"];self.selected_subject=values[0]
        for key,value in zip(["code","name","class_name","section","full","pass"],[values[1],values[2],f"{values[3]} | {values[4]}",values[4],values[5],values[6]]):self.subject_vars[key].set(value)

    def update_subject(self):
        if not self.selected_subject:return messagebox.showwarning("Select","আগে একটি subject নির্বাচন করুন।")
        values={key:var.get().strip() for key,var in self.subject_vars.items()}
        try:
            full=float(values["full"]);passed=float(values["pass"]);class_name,section=[part.strip() for part in values["class_name"].split("|",1)]
            if full<=0 or passed<0 or passed>full:raise ValueError("Pass marks must be between 0 and full marks")
            execute("UPDATE subjects SET subject_code=?,subject_name=?,full_marks=?,pass_marks=?,class_name=?,section=? WHERE id=?",(values["code"],values["name"],full,passed,class_name,values["section"] or section,self.selected_subject));log_activity(self.user["username"],"Updated subject "+values["name"]);self.clear_subject();self.load_subjects()
        except Exception as e:messagebox.showerror("Error",str(e))

    def delete_subject(self):
        if not self.selected_subject:return messagebox.showwarning("Select","আগে একটি subject নির্বাচন করুন।")
        if not messagebox.askyesno("Confirm","এই subject remove করবেন?"):return
        execute("DELETE FROM subjects WHERE id=?",(self.selected_subject,));log_activity(self.user["username"],"Removed subject");self.clear_subject();self.load_subjects()

    def clear_subject(self):
        self.selected_subject=None
        self.subject_vars["code"].set("");self.subject_vars["name"].set("");self.subject_vars["full"].set("100");self.subject_vars["pass"].set("33");self.subject_vars["section"].set("")
    def clear(self):self.selected_class=None;self.name.set("");self.section.set("A");self.teacher.set("")
