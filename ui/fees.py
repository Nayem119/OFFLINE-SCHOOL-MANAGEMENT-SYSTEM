import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database.db import query, execute, log_activity
from utils.helpers import today
from utils.pdf_style import draw_brand_header, draw_footer

def money(v):
    return f"{float(v or 0):,.2f}"

class FeesFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, padding=12)
        self.user = user
        self.selected_due=None
        self.build()
        self.refresh_all()

    def build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.collect_tab = ttk.Frame(nb, padding=10)
        self.due_tab = ttk.Frame(nb, padding=10)
        self.history_tab = ttk.Frame(nb, padding=10)
        self.reports_tab = ttk.Frame(nb, padding=10)
        self.settings_tab = ttk.Frame(nb, padding=10)
        nb.add(self.collect_tab, text="💳 Payment / Receipt")
        nb.add(self.due_tab, text="📌 Student Due")
        nb.add(self.history_tab, text="📜 Payment History")
        nb.add(self.reports_tab, text="📊 Collection Reports")
        nb.add(self.settings_tab, text="⚙️ Fee Settings")
        self.build_collect()
        self.build_due()
        self.build_history()
        self.build_reports()
        self.build_settings()

    def build_collect(self):
        box = ttk.LabelFrame(self.collect_tab, text="💰 Fee Collection", padding=10)
        box.pack(fill="x")
        self.student_id = tk.StringVar()
        self.student_name = tk.StringVar()
        self.fee_type = tk.StringVar(value="Monthly Fee")
        self.amount = tk.StringVar()
        self.payment_date = tk.StringVar(value=today())
        self.note = tk.StringVar(); self.discount = tk.StringVar(value="0"); self.payment_method = tk.StringVar(value="Cash")

        labels = [
            ("Student ID", self.student_id), ("Student Name", self.student_name),
            ("Fee Type", self.fee_type), ("Amount", self.amount),
            ("Payment Date", self.payment_date), ("Discount", self.discount), ("Payment Method", self.payment_method), ("Note", self.note)
        ]
        for i, (lab, var) in enumerate(labels):
            r, c = divmod(i, 3)
            ttk.Label(box, text=lab).grid(row=r*2, column=c, sticky="w", padx=5, pady=(2,0))
            if lab == "Fee Type":
                w = ttk.Combobox(box, textvariable=var, state="readonly")
                self.fee_combo = w
            elif lab == "Payment Method":
                w = ttk.Combobox(box, textvariable=var, values=["Cash", "Bank", "bKash", "Nagad", "Card", "Other"], state="readonly")
            else:
                w = ttk.Entry(box, textvariable=var)
            w.grid(row=r*2+1, column=c, sticky="ew", padx=5, pady=(0,6))
        for c in range(3):
            box.columnconfigure(c, weight=1)

        actions = ttk.Frame(self.collect_tab)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="🔎 Find Student", command=self.find_student).pack(side="left", padx=3)
        ttk.Button(actions, text="💾 Collect & Receipt", command=self.collect).pack(side="left", padx=3)
        ttk.Button(actions, text="📕 Export Receipt PDF", command=self.export_receipt_pdf).pack(side="left", padx=3)
        ttk.Button(actions, text="🧹 Clear", command=self.clear_collect).pack(side="left", padx=3)

        self.receipt = tk.Text(self.collect_tab, height=15, font=("Courier New", 10))
        self.receipt.pack(fill="both", expand=True, pady=8)

    def build_due(self):
        top = ttk.Frame(self.due_tab); top.pack(fill="x")
        self.due_search = tk.StringVar()
        ttk.Label(top, text="🔎 Student ID / Name").pack(side="left")
        ttk.Entry(top, textvariable=self.due_search, width=35).pack(side="left", padx=7)
        ttk.Button(top, text="Search", command=self.load_due).pack(side="left")
        ttk.Button(top, text="➕ Add Due", command=self.add_due).pack(side="left", padx=8)
        ttk.Button(top, text="✏️ Edit Selected", command=self.edit_due).pack(side="left", padx=4)
        ttk.Button(top, text="🗑 Remove Selected", command=self.delete_due).pack(side="left", padx=4)
        self.due_tree = ttk.Treeview(
            self.due_tab,
            columns=("id","student","fee","amount","date","status","note"),
            show="headings"
        )
        for c,h in [
            ("id","Student ID"),("student","নাম"),("fee","Fee Type"),
            ("amount","Amount"),("date","Due Date"),("status","Status"),("note","Note")
        ]:
            self.due_tree.heading(c, text=h); self.due_tree.column(c, width=120)
        self.due_tree.column("student", width=180)
        self.due_tree.pack(fill="both", expand=True, pady=8)
        self.due_tree.bind("<<TreeviewSelect>>",lambda _event:self.select_due())

    def build_history(self):
        top = ttk.Frame(self.history_tab); top.pack(fill="x")
        self.history_search = tk.StringVar()
        ttk.Label(top, text="Date YYYY-MM-DD").pack(side="left")
        ttk.Entry(top, textvariable=self.history_search, width=20).pack(side="left", padx=6)
        ttk.Button(top, text="Load", command=self.load_history).pack(side="left")
        self.history_tree = ttk.Treeview(
            self.history_tab,
            columns=("receipt","id","name","date","amount","fee","note"),
            show="headings"
        )
        for c,h in [
            ("receipt","Receipt No"),("id","Student ID"),("name","নাম"),
            ("date","Date"),("amount","Amount"),("fee","Fee Type"),("note","Note")
        ]:
            self.history_tree.heading(c,text=h); self.history_tree.column(c,width=120)
        self.history_tree.column("name",width=180)
        self.history_tree.pack(fill="both", expand=True, pady=8)

    def build_reports(self):
        box = ttk.LabelFrame(self.reports_tab, text="📊 Collection Summary", padding=12)
        box.pack(fill="x")
        self.daily_date = tk.StringVar(value=today())
        self.month = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ttk.Label(box,text="Daily Date").grid(row=0,column=0,padx=5)
        ttk.Entry(box,textvariable=self.daily_date).grid(row=1,column=0,padx=5)
        ttk.Button(box,text="Daily Collection",command=self.daily_report).grid(row=1,column=1,padx=8)
        ttk.Label(box,text="Month YYYY-MM").grid(row=0,column=2,padx=5)
        ttk.Entry(box,textvariable=self.month).grid(row=1,column=2,padx=5)
        ttk.Button(box,text="Monthly Collection",command=self.monthly_report).grid(row=1,column=3,padx=8)
        self.report_text = tk.Text(self.reports_tab, height=18, font=("Courier New", 10))
        self.report_text.pack(fill="both",expand=True,pady=10)

    def build_settings(self):
        form=ttk.LabelFrame(self.settings_tab,text="⚙️ Fee Settings",padding=10);form.pack(fill="x")
        self.fs_name=tk.StringVar();self.fs_amount=tk.StringVar();self.fs_frequency=tk.StringVar(value="Monthly")
        for i,(l,v) in enumerate([("Fee Name",self.fs_name),("Amount",self.fs_amount),("Frequency",self.fs_frequency)]):
            ttk.Label(form,text=l).grid(row=0,column=i,sticky="w",padx=5)
            if l=="Frequency":
                w=ttk.Combobox(form,textvariable=v,values=["Monthly","One Time","Per Exam","Other"],state="readonly")
            else:w=ttk.Entry(form,textvariable=v)
            w.grid(row=1,column=i,sticky="ew",padx=5);form.columnconfigure(i,weight=1)
        a=ttk.Frame(self.settings_tab);a.pack(fill="x",pady=8)
        ttk.Button(a,text="➕ Add Fee Type",command=self.add_fee_setting).pack(side="left",padx=3)
        ttk.Button(a,text="✏️ Update Selected",command=self.update_fee_setting).pack(side="left",padx=3)
        ttk.Button(a,text="🗑 Remove Selected",command=self.delete_fee_setting).pack(side="left",padx=3)
        self.fs_tree=ttk.Treeview(self.settings_tab,columns=("id","name","amount","freq","active"),show="headings")
        for c,h in [("id","ID"),("name","Fee Name"),("amount","Amount"),("freq","Frequency"),("active","Status")]:
            self.fs_tree.heading(c,text=h);self.fs_tree.column(c,width=160)
        self.fs_tree.pack(fill="both",expand=True)
        self.fs_tree.bind("<<TreeviewSelect>>",self.select_fee_setting)

    def refresh_all(self):
        self.load_fee_settings()
        self.load_due()
        self.load_history()

    def load_fee_settings(self):
        rows=query("SELECT * FROM fee_settings ORDER BY id")
        self.fee_combo["values"]=[r["fee_name"] for r in rows if r["active"]]
        for x in self.fs_tree.get_children(): self.fs_tree.delete(x)
        for r in rows:
            self.fs_tree.insert("", "end", values=(r["id"],r["fee_name"],money(r["amount"]),r["frequency"],"Active" if r["active"] else "Inactive"))

    def select_fee_setting(self,_=None):
        item=self.fs_tree.focus()
        if not item:return
        fid=self.fs_tree.item(item)["values"][0]
        r=query("SELECT * FROM fee_settings WHERE id=?",(fid,))[0]
        self.fs_name.set(r["fee_name"]);self.fs_amount.set(str(r["amount"]));self.fs_frequency.set(r["frequency"])

    def add_fee_setting(self):
        try:
            execute("INSERT INTO fee_settings(fee_name,amount,frequency) VALUES(?,?,?)",
                    (self.fs_name.get().strip(),float(self.fs_amount.get() or 0),self.fs_frequency.get()))
            log_activity(self.user["username"],"Added fee setting "+self.fs_name.get().strip())
            self.load_fee_settings()
        except Exception as e:messagebox.showerror("Error",str(e))

    def update_fee_setting(self):
        item=self.fs_tree.focus()
        if not item:return
        fid=self.fs_tree.item(item)["values"][0]
        try:
            execute("UPDATE fee_settings SET fee_name=?,amount=?,frequency=? WHERE id=?",
                    (self.fs_name.get().strip(),float(self.fs_amount.get() or 0),self.fs_frequency.get(),fid))
            log_activity(self.user["username"],"Updated fee setting")
            self.load_fee_settings()
        except Exception as e:messagebox.showerror("Error",str(e))

    def delete_fee_setting(self):
        item=self.fs_tree.focus()
        if not item:return messagebox.showwarning("Select","আগে একটি fee type নির্বাচন করুন।")
        if not messagebox.askyesno("Confirm","এই fee type remove করবেন?"):return
        fid=self.fs_tree.item(item)["values"][0]
        execute("UPDATE fee_settings SET active=0 WHERE id=?",(fid,));log_activity(self.user["username"],f"Removed fee setting {fid}");self.load_fee_settings()

    def find_student(self):
        sid=self.student_id.get().strip()
        rows=query("SELECT name FROM students WHERE student_id=?",(sid,))
        if rows:self.student_name.set(rows[0]["name"])
        else:messagebox.showwarning("Not Found","Student পাওয়া যায়নি।")

    def collect(self):
        sid=self.student_id.get().strip()
        if not self.student_name.get().strip(): self.find_student()
        if not sid or not self.student_name.get().strip():
            messagebox.showwarning("Required","Student ID এবং valid student আবশ্যক.");return
        try:
            amount=float(self.amount.get())
            if amount<=0:raise ValueError("Amount must be greater than zero")
            receipt=f"R-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
            discount=float(self.discount.get() or 0)
            if discount < 0 or discount >= amount:raise ValueError("Discount must be less than the amount")
            net_amount=amount-discount
            execute("""INSERT INTO fee_payments(receipt_no,student_id,student_name,payment_date,amount,discount,fee_type,payment_method,note)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (receipt,sid,self.student_name.get().strip(),self.payment_date.get(),net_amount,discount,self.fee_type.get(),self.payment_method.get(),self.note.get().strip()))
            # Automatically reduce matching due records, oldest first.
            dues=query("""SELECT id,amount FROM student_fees
                          WHERE student_id=? AND fee_name=? AND status='Due'
                          ORDER BY due_date,id""",(sid,self.fee_type.get()))
            remaining=net_amount
            for d in dues:
                if remaining<=0:break
                due=float(d["amount"])
                if remaining>=due:
                    execute("UPDATE student_fees SET status='Paid' WHERE id=?",(d["id"],))
                    remaining-=due
                else:
                    execute("UPDATE student_fees SET amount=? WHERE id=?",(due-remaining,d["id"]))
                    remaining=0
            log_activity(self.user["username"],f"Collected {amount} from {sid}, receipt {receipt}")
            self.show_receipt(receipt,amount,discount,net_amount)
            self.load_due();self.load_history()
        except Exception as e:messagebox.showerror("Error",str(e))

    def show_receipt(self,receipt,amount,discount=0,net_amount=None):
        net_amount=amount-discount if net_amount is None else net_amount
        s=query("SELECT * FROM settings WHERE id=1")[0]
        self.receipt.delete("1.0","end")
        lines=[
            "="*48,s["school_name"],s["school_address"],f"Phone: {s['phone']}",
            "="*48,"MONEY RECEIPT",f"Receipt No : {receipt}",
            f"Date       : {self.payment_date.get()}",f"Student ID : {self.student_id.get()}",
            f"Student    : {self.student_name.get()}",f"Fee Type   : {self.fee_type.get()}",
            f"Amount     : {money(amount)}",f"Discount   : {money(discount)}",f"Net Paid   : {money(net_amount)}",
            f"Method     : {self.payment_method.get()}",f"Note       : {self.note.get()}",
            "-"*48,f"Paid Amount: {money(net_amount)}","Thank you.","="*48
        ]
        self.receipt.insert("1.0","\n".join(lines))

    def clear_collect(self):
        self.student_id.set("");self.student_name.set("");self.amount.set("");self.discount.set("0");self.payment_method.set("Cash");self.note.set("");self.receipt.delete("1.0","end")
        self.payment_date.set(today())

    def export_receipt_pdf(self):
        content=self.receipt.get("1.0","end").strip()
        if not content:return messagebox.showwarning("Empty Receipt","আগে একটি receipt তৈরি করুন।")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            return messagebox.showwarning("PDF Export","Receipt PDF-এর জন্য reportlab install করুন: pip install reportlab")
        path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")],initialfile="money_receipt.pdf")
        if not path:return
        try:
            pdf=canvas.Canvas(path,pagesize=A4);width,height=A4;settings=dict(query("SELECT * FROM settings WHERE id=1")[0]);y=draw_brand_header(pdf,"Money Receipt",settings,width,height);pdf.setFont("Courier",10)
            for line in content.splitlines():
                pdf.drawString(42,y,line[:100]);y-=14
            draw_footer(pdf,width)
            pdf.save();messagebox.showinfo("Export Complete",f"Receipt PDF saved:\n{path}")
        except Exception as e:messagebox.showerror("PDF Error",str(e))

    def add_due(self):
        win=tk.Toplevel(self);win.title("Add Student Due");win.geometry("520x360")
        v={k:tk.StringVar() for k in ["student_id","fee_name","amount","due_date","note"]}
        v["due_date"].set(today())
        for i,(l,k) in enumerate([("Student ID","student_id"),("Fee Type","fee_name"),("Amount","amount"),("Due Date","due_date"),("Note","note")]):
            ttk.Label(win,text=l).grid(row=i,column=0,padx=10,pady=8,sticky="w")
            if k=="fee_name":
                w=ttk.Combobox(win,textvariable=v[k],values=list(self.fee_combo["values"]),state="readonly")
            else:w=ttk.Entry(win,textvariable=v[k])
            w.grid(row=i,column=1,padx=10,pady=8,sticky="ew")
        win.columnconfigure(1,weight=1)
        def save():
            try:
                sid=v["student_id"].get().strip()
                sr=query("SELECT name FROM students WHERE student_id=?",(sid,))
                if not sr:raise ValueError("Student not found")
                execute("INSERT INTO student_fees(student_id,fee_name,amount,due_date,note) VALUES(?,?,?,?,?)",
                        (sid,v["fee_name"].get(),float(v["amount"].get()),v["due_date"].get(),v["note"].get()))
                log_activity(self.user["username"],f"Added due for {sid}")
                win.destroy();self.load_due()
            except Exception as e:messagebox.showerror("Error",str(e),parent=win)
        ttk.Button(win,text="Save Due",command=save).grid(row=5,column=0,columnspan=2,pady=12)

    def select_due(self):
        item=self.due_tree.focus()
        self.selected_due=item or None

    def edit_due(self):
        if not self.selected_due:return messagebox.showwarning("Select","আগে একটি due record নির্বাচন করুন।")
        row=query("SELECT * FROM student_fees WHERE id=?",(self.selected_due,))[0]
        win=tk.Toplevel(self);win.title("Edit Student Due");win.geometry("520x360")
        values={key:tk.StringVar(value=str(row[key] or "")) for key in ["student_id","fee_name","amount","due_date","note"]}
        for i,(label,key) in enumerate([("Student ID","student_id"),("Fee Type","fee_name"),("Amount","amount"),("Due Date","due_date"),("Note","note")]):
            ttk.Label(win,text=label).grid(row=i,column=0,padx=10,pady=8,sticky="w")
            widget=ttk.Combobox(win,textvariable=values[key],values=list(self.fee_combo["values"]),state="readonly") if key=="fee_name" else ttk.Entry(win,textvariable=values[key])
            widget.grid(row=i,column=1,padx=10,pady=8,sticky="ew")
        win.columnconfigure(1,weight=1)
        def save():
            try:
                if not query("SELECT id FROM students WHERE student_id=?",(values["student_id"].get().strip(),)):raise ValueError("Student not found")
                amount=float(values["amount"].get());
                if amount<=0:raise ValueError("Amount must be greater than zero")
                execute("UPDATE student_fees SET student_id=?,fee_name=?,amount=?,due_date=?,note=? WHERE id=?",(values["student_id"].get().strip(),values["fee_name"].get(),amount,values["due_date"].get().strip(),values["note"].get().strip(),self.selected_due))
                log_activity(self.user["username"],f"Updated due {self.selected_due}");win.destroy();self.load_due()
            except Exception as error:messagebox.showerror("Error",str(error),parent=win)
        ttk.Button(win,text="💾 Save Changes",command=save).grid(row=5,column=0,columnspan=2,pady=12)

    def delete_due(self):
        if not self.selected_due:return messagebox.showwarning("Select","আগে একটি due record নির্বাচন করুন।")
        if not messagebox.askyesno("Confirm","এই due record remove করবেন?"):return
        execute("DELETE FROM student_fees WHERE id=?",(self.selected_due,));log_activity(self.user["username"],f"Removed due {self.selected_due}");self.selected_due=None;self.load_due()

    def load_due(self):
        if not hasattr(self,"due_tree"):return
        for x in self.due_tree.get_children():self.due_tree.delete(x)
        term=f"%{self.due_search.get().strip()}%"
        rows=query("""SELECT sf.id AS due_id,sf.student_id,s.name,sf.fee_name,sf.amount,sf.due_date,sf.status,sf.note
                      FROM student_fees sf LEFT JOIN students s ON s.student_id=sf.student_id
                      WHERE (sf.student_id LIKE ? OR s.name LIKE ?) AND sf.status='Due'
                      ORDER BY sf.due_date DESC,sf.id DESC""",(term,term))
        for r in rows:self.due_tree.insert("", "end",iid=str(r["due_id"]),values=(r["student_id"],r["name"] or "",r["fee_name"],money(r["amount"]),r["due_date"],r["status"],r["note"]))

    def load_history(self):
        if not hasattr(self,"history_tree"):return
        for x in self.history_tree.get_children():self.history_tree.delete(x)
        d=self.history_search.get().strip()
        rows=query("SELECT * FROM fee_payments WHERE payment_date=? ORDER BY id DESC",(d,)) if d else query("SELECT * FROM fee_payments ORDER BY id DESC LIMIT 300")
        for r in rows:self.history_tree.insert("", "end",values=(r["receipt_no"],r["student_id"],r["student_name"],r["payment_date"],money(r["amount"]),r["fee_type"],r["note"]))

    def daily_report(self):
        d=self.daily_date.get().strip()
        rows=query("SELECT fee_type,COUNT(*) c,SUM(amount) total FROM fee_payments WHERE payment_date=? GROUP BY fee_type",(d,))
        total=sum(float(r["total"] or 0) for r in rows)
        self.report_text.delete("1.0","end")
        self.report_text.insert("1.0",f"DAILY COLLECTION REPORT\nDate: {d}\n"+"-"*50+"\n")
        for r in rows:self.report_text.insert("end",f"{r['fee_type']:<25} {money(r['total']):>15}\n")
        self.report_text.insert("end","-"*50+f"\nTOTAL: {money(total)}")

    def monthly_report(self):
        m=self.month.get().strip()
        rows=query("SELECT fee_type,COUNT(*) c,SUM(amount) total FROM fee_payments WHERE substr(payment_date,1,7)=? GROUP BY fee_type",(m,))
        total=sum(float(r["total"] or 0) for r in rows)
        self.report_text.delete("1.0","end")
        self.report_text.insert("1.0",f"MONTHLY COLLECTION REPORT\nMonth: {m}\n"+"-"*50+"\n")
        for r in rows:self.report_text.insert("end",f"{r['fee_type']:<25} {money(r['total']):>15}\n")
        self.report_text.insert("end","-"*50+f"\nTOTAL: {money(total)}")
