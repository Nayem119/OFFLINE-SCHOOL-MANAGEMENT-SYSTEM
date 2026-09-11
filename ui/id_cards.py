import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.db import query
from config import DEVELOPER
from pathlib import Path
from utils.pdf_style import draw_photo

class IDCardFrame(ttk.Frame):
    def __init__(self,m,u):
        super().__init__(m,padding=12);self.user=u
        ttk.Label(self,text="🪪 Student ID Card",font=("TkDefaultFont",18,"bold")).pack(anchor="w")
        bar=ttk.Frame(self);bar.pack(fill="x",pady=8)
        self.search=tk.StringVar();ttk.Label(bar,text="Student ID(s), comma separated").pack(side="left")
        ttk.Entry(bar,textvariable=self.search,width=45).pack(side="left",padx=6)
        ttk.Button(bar,text="Preview",command=self.preview).pack(side="left",padx=3)
        ttk.Button(bar,text="Export / Print",command=self.export).pack(side="left",padx=3)
        ttk.Label(self,text="Card includes School Logo, Student Photo (when available), ID, Roll/Class/Section, Guardian Phone, Blood Group and QR Code.").pack(anchor="w",pady=8)
        self.preview_box=ttk.LabelFrame(self,text="Preview",padding=15);self.preview_box.pack(fill="both",expand=True)
    def get_students(self):
        ids=[x.strip() for x in self.search.get().split(",") if x.strip()]
        if not ids:return []
        marks=",".join("?" for _ in ids)
        return query(f"SELECT * FROM students WHERE student_id IN ({marks}) ORDER BY name",ids)
    def preview(self):
        for w in self.preview_box.winfo_children():w.destroy()
        rows=self.get_students()
        if not rows:ttk.Label(self.preview_box,text="No student found.").pack();return
        for s in rows:
            card=ttk.LabelFrame(self.preview_box,text=f"{s['name']} • {s['student_id']}",padding=12);card.pack(fill="x",pady=5)
            ttk.Label(card,text=f"🏫 School\n{s['name']}\nID: {s['student_id']}   Roll: {s['roll']}\nClass: {s['class_name']}   Section: {s['section']}\nGuardian Phone: {s['guardian_phone'] or s['phone']}\nBlood Group: {s['blood_group'] or 'N/A'}\nQR: {s['student_id']}").pack(anchor="w")
    def export(self):
        rows=self.get_students()
        if not rows:messagebox.showwarning("No data","Enter at least one valid Student ID.");return
        path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")],initialfile="student_id_cards.pdf")
        if not path:return
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            c=canvas.Canvas(path,pagesize=A4); w,h=A4; y=h-60; settings=dict(query("SELECT * FROM settings WHERE id=1")[0])
            for i,s in enumerate(rows):
                if y<170:c.showPage();y=h-60
                c.rect(45,y-120,w-90,115)
                c.setFont("Helvetica-Bold",13);c.drawString(60,y-25,(settings["school_name"] or "SCHOOL MANAGEMENT SYSTEM")[:45])
                draw_photo(c,s["photo_path"],w-135,y-105,60)
                c.setFont("Helvetica",9);c.drawString(60,y-45,f"Student: {s['name']}")
                c.drawString(60,y-62,f"ID: {s['student_id']}   Roll: {s['roll']}   Class: {s['class_name']} / {s['section']}")
                c.drawString(60,y-79,f"Guardian: {s['guardian_phone'] or s['phone']}   Blood: {s['blood_group'] or 'N/A'}")
                c.drawString(60,y-98,f"{settings.get('phone') or ''}  |  {DEVELOPER}")
                try:
                    import qrcode
                    img=qrcode.make(s["student_id"]);tmp=Path(path).with_suffix(f".qr{i}.png");img.save(tmp);c.drawImage(str(tmp),w-145,y-108,70,70);tmp.unlink(missing_ok=True)
                except Exception: c.drawString(w-140,y-85,"QR: "+s["student_id"])
                y-=145
            c.save();messagebox.showinfo("Success",f"PDF created:\n{path}")
        except ImportError:messagebox.showerror("Missing package","Install reportlab (and optionally qrcode) to export printable PDF cards.")
        except Exception as e:messagebox.showerror("Error",str(e))
