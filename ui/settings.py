import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.db import query, execute, log_activity
from utils.helpers import backup_database
from utils.auth import verify_password, hash_password

class SettingsFrame(ttk.Frame):
    def __init__(self,master,user,on_theme_change=None):
        super().__init__(master,padding=20);self.user=user;self.on_theme_change=on_theme_change
        self.vars={k:tk.StringVar() for k in ["school_name","address","phone","email","logo_path","signature_path","academic_year","language","theme"]}
        self.build();self.load()
    def build(self):
        b=ttk.LabelFrame(self,text="⚙️ School Settings",padding=15);b.pack(fill="x")
        fields=[("School Name","school_name"),("Address","address"),("Phone","phone"),("Email","email"),("Logo","logo_path"),("Principal Signature","signature_path"),("Academic Year","academic_year"),("Language","language"),("Theme","theme")]
        for i,(l,k) in enumerate(fields):
            ttk.Label(b,text=l).grid(row=i,column=0,sticky="w",padx=5,pady=5)
            entry=ttk.Combobox(b,textvariable=self.vars[k],values=["Light","Dark"],state="readonly") if k=="theme" else ttk.Entry(b,textvariable=self.vars[k]);entry.grid(row=i,column=1,sticky="ew",padx=5,pady=5)
            if k in ("logo_path","signature_path"):
                ttk.Button(b,text="Browse",command=lambda key=k:self.choose_file(key)).grid(row=i,column=2,padx=5)
        b.columnconfigure(1,weight=1)
        ttk.Button(self,text="💾 Save Settings",command=self.save).pack(anchor="w",pady=10)
        ttk.Button(self,text="💾 Backup Database",command=self.backup).pack(anchor="w")
        password_box=ttk.LabelFrame(self,text="🔐 Change Password",padding=12);password_box.pack(fill="x",pady=(18,0))
        self.old_password=tk.StringVar();self.new_password=tk.StringVar();self.confirm_password=tk.StringVar()
        for row,(label,var) in enumerate([("Current Password",self.old_password),("New Password",self.new_password),("Confirm Password",self.confirm_password)]):
            ttk.Label(password_box,text=label).grid(row=row,column=0,sticky="w",padx=5,pady=5)
            ttk.Entry(password_box,textvariable=var,show="•").grid(row=row,column=1,sticky="ew",padx=5,pady=5)
        password_box.columnconfigure(1,weight=1)
        ttk.Button(password_box,text="Update Password",command=self.change_password).grid(row=3,column=0,columnspan=2,pady=8)
    def load(self):
        r=query("SELECT * FROM settings WHERE id=1")[0]
        for k,c in [("school_name","school_name"),("address","school_address"),("phone","phone"),("email","email"),("logo_path","logo_path"),("signature_path","signature_path"),("academic_year","academic_year"),("language","language"),("theme","theme")]:self.vars[k].set(r[c] or "")
    def save(self):
        v=self.vars
        execute("UPDATE settings SET school_name=?,school_address=?,phone=?,email=?,logo_path=?,signature_path=?,academic_year=?,language=?,theme=? WHERE id=1",(v["school_name"].get(),v["address"].get(),v["phone"].get(),v["email"].get(),v["logo_path"].get(),v["signature_path"].get(),v["academic_year"].get(),v["language"].get(),v["theme"].get() or "Light"))
        log_activity(self.user["username"],"Updated school settings");messagebox.showinfo("Saved","Settings সংরক্ষণ হয়েছে।")
        if self.on_theme_change:self.on_theme_change(v["theme"].get() or "Light")
    def choose_file(self,key):
        path=filedialog.askopenfilename(filetypes=[("Image files","*.png *.jpg *.jpeg")])
        if path:self.vars[key].set(path)
    def change_password(self):
        if not self.old_password.get() or not self.new_password.get():return messagebox.showwarning("Required","Current এবং new password আবশ্যক।")
        if len(self.new_password.get())<6:return messagebox.showwarning("Weak Password","New password কমপক্ষে 6 characters হতে হবে।")
        if self.new_password.get()!=self.confirm_password.get():return messagebox.showwarning("Mismatch","New password এবং confirmation একই নয়।")
        row=query("SELECT id,password FROM users WHERE username=?",(self.user["username"],))[0]
        if not verify_password(self.old_password.get(),row["password"]):return messagebox.showerror("Password Error","Current password সঠিক নয়।")
        execute("UPDATE users SET password=? WHERE id=?",(hash_password(self.new_password.get()),row["id"]))
        log_activity(self.user["username"],"Changed account password")
        self.old_password.set("");self.new_password.set("");self.confirm_password.set("");messagebox.showinfo("Updated","Password successfully changed.")
    def backup(self):
        p=backup_database()
        if p:log_activity(self.user["username"],"Created database backup");messagebox.showinfo("Backup",f"Backup তৈরি হয়েছে:\n{p}")
