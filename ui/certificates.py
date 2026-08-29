import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from database.db import query
from utils.pdf_style import draw_brand_header, draw_footer, draw_photo

class CertificatesFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master,padding=12); self.build()
    def build(self):
        f=ttk.LabelFrame(self,text="🎓 Certificate / Testimonial",padding=10);f.pack(fill="x")
        self.sid=tk.StringVar(); self.ctype=tk.StringVar(value="Character Certificate")
        ttk.Label(f,text="Student ID").grid(row=0,column=0);ttk.Entry(f,textvariable=self.sid).grid(row=1,column=0,padx=5)
        ttk.Label(f,text="Certificate Type").grid(row=0,column=1)
        ttk.Combobox(f,textvariable=self.ctype,state="readonly",
                     values=["Character Certificate","Transfer Certificate","Testimonial","Academic Certificate"]).grid(row=1,column=1,padx=5)
        ttk.Button(f,text="Generate",command=self.generate).grid(row=1,column=2,padx=8)
        ttk.Button(f,text="📕 Export PDF",command=self.export_pdf).grid(row=1,column=3,padx=8)
        self.text=tk.Text(self,font=("Times New Roman",12));self.text.pack(fill="both",expand=True,pady=10)
    def generate(self):
        rows=query("SELECT * FROM students WHERE student_id=?",(self.sid.get().strip(),))
        if not rows:return messagebox.showwarning("Not Found","Student পাওয়া যায়নি।")
        s=rows[0];settings=query("SELECT school_name,school_address,phone FROM settings WHERE id=1")[0]
        title=self.ctype.get().upper()
        body=f"""{"="*72}
                         {settings['school_name'].upper()}
{"="*72}

                         {title}

This is to certify that Mr./Ms. {s['name']} (Student ID: {s['student_id']})
is a student of this institution, Class {s['class_name']}, Section {s['section']}.

This certificate is issued upon request for official purposes.

Date: {datetime.now():%d %B %Y}


_________________________                 _________________________
Class Teacher                              Head Teacher / Principal
{"="*72}"""
        self.text.delete("1.0","end");self.text.insert("1.0",body)

    def export_pdf(self):
        content=self.text.get("1.0","end").strip()
        if not content:return messagebox.showwarning("Empty","আগে certificate generate করুন।")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            return messagebox.showwarning("PDF Export","Certificate PDF-এর জন্য reportlab install করুন: pip install reportlab")
        path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")],initialfile="student_certificate.pdf")
        if not path:return
        try:
            pdf=canvas.Canvas(path,pagesize=A4);width,height=A4;settings=dict(query("SELECT * FROM settings WHERE id=1")[0]);y=draw_brand_header(pdf,"Certificate / Testimonial",settings,width,height);pdf.setFont("Courier",10)
            for line in content.splitlines():
                if y<70:draw_footer(pdf,width);pdf.showPage();y=draw_brand_header(pdf,"Certificate / Testimonial",settings,width,height);pdf.setFont("Courier",10)
                pdf.drawCentredString(width/2,y,line[:100]);y-=15
            signature=settings.get("signature_path")
            if signature:draw_photo(pdf,signature,width-180,55,110)
            draw_footer(pdf,width)
            pdf.save();messagebox.showinfo("Export Complete",f"Certificate PDF saved:\n{path}")
        except Exception as e:messagebox.showerror("PDF Error",str(e))
