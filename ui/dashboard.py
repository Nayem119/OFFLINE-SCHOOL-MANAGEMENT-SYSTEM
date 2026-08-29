import tkinter as tk
from tkinter import ttk
from datetime import datetime
from database.db import query

class DashboardFrame(ttk.Frame):
    def __init__(self, master, actions=None):
        super().__init__(master,padding=28,style="Dashboard.TFrame")
        self.actions=actions or {}
        self.build()

    def build(self):
        dark=getattr(self.winfo_toplevel(),"theme","Light")=="Dark"
        canvas_bg="#263238" if dark else "#ffffff"; card_bg="#34434a" if dark else "#ffffff"; text_fg="#f2f6f8" if dark else "#17324d"; muted_fg="#b8c6cc" if dark else "#5d7180"
        school=query("SELECT school_name FROM settings WHERE id=1")
        name=school[0]["school_name"] if school else "আমাদের স্কুল"
        counts=[
            ("👨‍🎓 শিক্ষার্থী",query("SELECT COUNT(*) c FROM students")[0]["c"]),
            ("👨‍🏫 শিক্ষক",query("SELECT COUNT(*) c FROM teachers")[0]["c"]),
            ("👨‍💼 Staff",query("SELECT COUNT(*) c FROM staff")[0]["c"]),
            ("📚 Class",query("SELECT COUNT(*) c FROM classes")[0]["c"]),
            ("👤 Users",query("SELECT COUNT(*) c FROM users WHERE active=1")[0]["c"]),
            ("💰 Collection",query("SELECT COALESCE(SUM(amount),0) c FROM fee_payments")[0]["c"])
        ]
        ttk.Label(self,text=f"স্বাগতম, {name}",font=("TkDefaultFont",22,"bold"),style="Dashboard.TLabel").pack(anchor="w")
        ttk.Label(self,text="আজকের স্কুল অপারেশন এক নজরে",foreground="#5d7180",style="Dashboard.TLabel").pack(anchor="w",pady=(2,20))
        quick=tk.Frame(self,bg="#17324d",padx=14,pady=10);quick.pack(fill="x",pady=(0,14))
        tk.Label(quick,text="Quick Actions",font=("TkDefaultFont",10,"bold"),bg="#17324d",fg="#ffffff").pack(side="left",padx=(0,14))
        for label,key in [("＋ Add Student","students"),("✓ Mark Attendance","attendance"),("৳ Collect Fee","fees")]:
            if key in self.actions:tk.Button(quick,text=label,command=self.actions[key],relief="flat",bg="#2a9d8f",fg="#ffffff",activebackground="#238276",padx=10,pady=5).pack(side="left",padx=4)
        if "refresh" in self.actions:tk.Button(quick,text="↻ Refresh",command=self.actions["refresh"],relief="flat",bg="#506b78",fg="#ffffff",activebackground="#405965",padx=10,pady=5).pack(side="right",padx=4)
        ttk.Label(self,text=f"Last refreshed: {datetime.now():%d %b %Y, %I:%M %p}",foreground="#5d7180",style="Dashboard.TLabel").pack(anchor="e",pady=(0,4))
        cards=ttk.Frame(self,style="Dashboard.TFrame");cards.pack(fill="x")
        for i,(t,v) in enumerate(counts):
            row,column=divmod(i,3);cards.columnconfigure(column,weight=1)
            box=tk.Frame(cards,bg=card_bg,highlightbackground="#50616a" if dark else "#dce5ea",highlightthickness=1,padx=16,pady=13)
            box.grid(row=row,column=column,sticky="nsew",padx=5,pady=5)
            tk.Label(box,text=t,font=("TkDefaultFont",10),bg=card_bg,fg=muted_fg).pack(anchor="w")
            display=f"৳ {v:,.0f}" if t.startswith("💰") else f"{v:,}"
            tk.Label(box,text=display,font=("TkDefaultFont",22,"bold"),bg=card_bg,fg=text_fg).pack(anchor="w",pady=(4,0))
        lower=ttk.Frame(self,style="Dashboard.TFrame");lower.pack(fill="both",expand=True,pady=(22,0));lower.columnconfigure(0,weight=1);lower.columnconfigure(1,weight=1);lower.columnconfigure(2,weight=1);lower.rowconfigure(0,weight=1)
        today=query("SELECT COUNT(*) c FROM attendance WHERE attendance_date=date('now','localtime') AND status='Present'")[0]["c"]
        attendance_total=query("SELECT COUNT(*) c FROM attendance WHERE attendance_date=date('now','localtime')")[0]["c"]
        attendance_box=ttk.LabelFrame(lower,text="আজকের উপস্থিতি",padding=18);attendance_box.grid(row=0,column=0,sticky="nsew",padx=(0,7))
        ttk.Label(attendance_box,text=f"{today} জন উপস্থিত",font=("TkDefaultFont",18,"bold"),foreground="#2a9d8f").pack(anchor="w")
        ttk.Label(attendance_box,text=f"আজ মোট রেকর্ড: {attendance_total}",foreground="#5d7180").pack(anchor="w",pady=(5,0))
        activity_box=ttk.LabelFrame(lower,text="সাম্প্রতিক কার্যক্রম",padding=12);activity_box.grid(row=0,column=1,sticky="nsew",padx=(7,0))
        logs=query("SELECT username, action, created_at FROM activity_logs ORDER BY id DESC LIMIT 5")
        if logs:
            for log in logs:
                ttk.Label(activity_box,text=f"{log['action']}  •  {log['username'] or 'system'}",foreground="#263238").pack(anchor="w",pady=3)
        else:
            ttk.Label(activity_box,text="এখনও কোনো activity log নেই",foreground="#5d7180").pack(anchor="w")
        reminder_box=ttk.LabelFrame(lower,text="Local Reminders",padding=12);reminder_box.grid(row=0,column=2,sticky="nsew",padx=(7,0))
        due_rows=query("""SELECT student_id,fee_name,amount,due_date FROM student_fees
                         WHERE status='Due' ORDER BY due_date LIMIT 4""")
        exam_rows=query("SELECT exam_name,class_name,section,exam_date FROM exams WHERE exam_date>=date('now','localtime') ORDER BY exam_date LIMIT 4")
        if due_rows:
            ttk.Label(reminder_box,text="Fee Due",font=("TkDefaultFont",10,"bold"),foreground="#b23a48").pack(anchor="w")
            for row in due_rows:ttk.Label(reminder_box,text=f"{row['student_id']} • ৳ {float(row['amount']):,.0f} • {row['due_date']}").pack(anchor="w",pady=2)
        if exam_rows:
            ttk.Label(reminder_box,text="Upcoming Exams",font=("TkDefaultFont",10,"bold"),foreground="#17324d").pack(anchor="w",pady=(10,2))
            for row in exam_rows:ttk.Label(reminder_box,text=f"{row['exam_name']} • {row['exam_date']}").pack(anchor="w",pady=2)
        if not due_rows and not exam_rows:ttk.Label(reminder_box,text="কোনো reminder নেই",foreground="#5d7180").pack(anchor="w")
        chart_box=ttk.LabelFrame(self,text="গত ৬ মাসের collection",padding=10);chart_box.pack(fill="x",pady=(18,0))
        chart=tk.Canvas(chart_box,height=130,bg=canvas_bg,highlightthickness=0);chart.pack(fill="x")
        monthly=query("""SELECT substr(payment_date,1,7) month,COALESCE(SUM(amount),0) total
                        FROM fee_payments GROUP BY substr(payment_date,1,7) ORDER BY month DESC LIMIT 6""")
        monthly=list(reversed(monthly));max_total=max([float(row["total"]) for row in monthly],default=1)
        chart.update_idletasks();chart_width=max(chart.winfo_width(),500);bar_width=max(24,(chart_width-50)//max(len(monthly),1)-12)
        for i,row in enumerate(monthly):
            x=35+i*(bar_width+12);bar_height=int(float(row["total"])/max_total*82);chart.create_rectangle(x,100-bar_height,x+bar_width,100,fill="#2a9d8f",outline="")
            chart.create_text(x+bar_width/2,114,text=row["month"],fill="#5d7180",font=("TkDefaultFont",8));chart.create_text(x+bar_width/2,94-bar_height,text=f"{float(row['total']):.0f}",fill="#17324d",font=("TkDefaultFont",8))
