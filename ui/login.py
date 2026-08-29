import tkinter as tk
from tkinter import ttk, messagebox
from database.db import query, log_activity
from config import APP_NAME, APP_VERSION
from utils.auth import verify_password, hash_password

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=30)
        self.on_success = on_success
        self.username = tk.StringVar(value="admin")
        self.password = tk.StringVar()
        self.show_password = tk.BooleanVar(value=False)
        self.status = tk.StringVar()
        self.configure(style="Login.TFrame")
        ttk.Style(self).configure("Login.TFrame", background="#edf3f5")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        ttk.Label(self, text="🏫", font=("Segoe UI Emoji", 42), background="#edf3f5").grid(row=1,column=0,pady=(0,4))
        ttk.Label(self, text=APP_NAME, font=("TkDefaultFont", 22, "bold"), background="#edf3f5", foreground="#17324d").grid(row=2,column=0)
        ttk.Label(self, text=f"Secure offline access  •  v{APP_VERSION}", background="#edf3f5", foreground="#5d7180").grid(row=3,column=0,pady=(4,18))

        box = ttk.LabelFrame(self, text="🔐  Sign in to continue", padding=24)
        box.grid(row=4,column=0,padx=60,sticky="ew")
        box.columnconfigure(1,weight=1)
        ttk.Label(box,text="Username").grid(row=0,column=0,padx=5,pady=(2,8),sticky="w")
        user_entry=ttk.Entry(box,textvariable=self.username)
        user_entry.grid(row=0,column=1,padx=5,pady=(2,8),sticky="ew")
        ttk.Label(box,text="Password").grid(row=1,column=0,padx=5,pady=8,sticky="w")
        ent=ttk.Entry(box,textvariable=self.password,show="•")
        ent.grid(row=1,column=1,padx=5,pady=8,sticky="ew")
        ttk.Checkbutton(box,text="Show password",variable=self.show_password,command=lambda:self.toggle_password(ent)).grid(row=2,column=1,sticky="w",padx=5,pady=(0,8))
        ttk.Button(box,text="Login",command=self.login).grid(row=3,column=0,columnspan=2,pady=(8,5),sticky="ew")
        ttk.Label(self,textvariable=self.status,foreground="#b23a48",background="#edf3f5").grid(row=5,column=0,pady=(12,0))
        user_entry.focus_set()
        ent.bind("<Return>", lambda e:self.login())

    def toggle_password(self, entry):
        entry.configure(show="" if self.show_password.get() else "•")

    def login(self):
        rows=query("SELECT * FROM users WHERE username=? AND active=1",(self.username.get().strip(),))
        if rows and verify_password(self.password.get(), rows[0]["password"]):
            user=dict(rows[0])
            if not rows[0]["password"].startswith("pbkdf2_sha256$"):
                from database.db import execute
                execute("UPDATE users SET password=? WHERE id=?", (hash_password(self.password.get()), user["id"]))
            log_activity(user["username"],"Logged in")
            self.on_success(user)
        else:
            log_activity(self.username.get().strip() or "unknown", "Failed login attempt")
            self.status.set("Login failed. Check username and password.")
            messagebox.showerror("Login Failed","Username অথবা Password ভুল/Inactive user.")
