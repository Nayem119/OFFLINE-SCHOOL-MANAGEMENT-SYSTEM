import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, execute, log_activity
from utils.auth import hash_password

class UsersFrame(ttk.Frame):
    def __init__(self,master,user):
        super().__init__(master,padding=12);self.user=user;self.selected=None
        self.vars={k:tk.StringVar() for k in ["username","password","full_name","role","active"]}
        self.vars["role"].set("Staff");self.vars["active"].set("Active")
        self.build();self.load()
    def build(self):
        box=ttk.LabelFrame(self,text="👤 User Management",padding=10);box.pack(fill="x")
        fields=[("Username","username"),("Password","password"),("Full Name","full_name"),("Role","role"),("Status","active")]
        for i,(l,k) in enumerate(fields):
            ttk.Label(box,text=l).grid(row=0,column=i,padx=4); 
            if k=="role":w=ttk.Combobox(box,textvariable=self.vars[k],values=["Admin","Staff"],state="readonly")
            elif k=="active":w=ttk.Combobox(box,textvariable=self.vars[k],values=["Active","Inactive"],state="readonly")
            else:w=ttk.Entry(box,textvariable=self.vars[k],show="•" if k=="password" else "")
            w.grid(row=1,column=i,padx=4,sticky="ew")
            box.columnconfigure(i,weight=1)
        a=ttk.Frame(self);a.pack(fill="x",pady=8)
        ttk.Button(a,text="➕ Add",command=self.add).pack(side="left",padx=3);ttk.Button(a,text="✏️ Update",command=self.update).pack(side="left",padx=3)
        ttk.Button(a,text="🔒 Toggle Active",command=self.toggle).pack(side="left",padx=3);ttk.Button(a,text="🧹 Clear",command=self.clear).pack(side="left",padx=3)
        self.tree=ttk.Treeview(self,columns=("id","username","name","role","active","created"),show="headings")
        for c,h in [("id","ID"),("username","Username"),("name","Full Name"),("role","Role"),("active","Status"),("created","Created")]:
            self.tree.heading(c,text=h);self.tree.column(c,width=150)
        self.tree.pack(fill="both",expand=True);self.tree.bind("<<TreeviewSelect>>",self.select)
    def load(self):
        for x in self.tree.get_children():self.tree.delete(x)
        for r in query("SELECT id,username,full_name,role,active,created_at FROM users ORDER BY id"):
            self.tree.insert("", "end",values=(r["id"],r["username"],r["full_name"],r["role"],"Active" if r["active"] else "Inactive",r["created_at"]))
    def select(self,_=None):
        item=self.tree.focus()
        if not item:return
        self.selected=self.tree.item(item)["values"][0]
        r=query("SELECT * FROM users WHERE id=?",(self.selected,))[0]
        for k in ["username","full_name","role"]:self.vars[k].set(r[k])
        self.vars["password"].set("");self.vars["active"].set("Active" if r["active"] else "Inactive")
    def add(self):
        v={k:x.get().strip() for k,x in self.vars.items()}
        if not v["username"] or not v["password"] or not v["full_name"]:messagebox.showwarning("Required","Username, Password ও Full Name আবশ্যক।");return
        try:
            execute("INSERT INTO users(username,password,full_name,role,active) VALUES(?,?,?,?,?)",(v["username"],hash_password(v["password"]),v["full_name"],v["role"],1 if v["active"]=="Active" else 0))
            log_activity(self.user["username"],"Created user "+v["username"]);self.clear();self.load()
        except Exception as e:messagebox.showerror("Error",str(e))
    def update(self):
        if not self.selected:return
        v={k:x.get().strip() for k,x in self.vars.items()}
        try:
            if v["password"]:
                execute("UPDATE users SET username=?,password=?,full_name=?,role=?,active=? WHERE id=?",(v["username"],hash_password(v["password"]),v["full_name"],v["role"],1 if v["active"]=="Active" else 0,self.selected))
            else:
                execute("UPDATE users SET username=?,full_name=?,role=?,active=? WHERE id=?",(v["username"],v["full_name"],v["role"],1 if v["active"]=="Active" else 0,self.selected))
            log_activity(self.user["username"],"Updated user "+v["username"]);self.load()
        except Exception as e:messagebox.showerror("Error",str(e))
    def toggle(self):
        if not self.selected:return
        r=query("SELECT username,active FROM users WHERE id=?",(self.selected,))[0]
        if r["username"]==self.user["username"] and r["active"]:
            messagebox.showwarning("Not allowed","নিজের বর্তমান account Inactive করা যাবে না.");return
        execute("UPDATE users SET active=? WHERE id=?",(0 if r["active"] else 1,self.selected))
        log_activity(self.user["username"],"Toggled user "+r["username"]);self.load()
    def clear(self):
        self.selected=None
        for v in self.vars.values():v.set("")
        self.vars["role"].set("Staff");self.vars["active"].set("Active")
