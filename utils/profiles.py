import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from database.db import query
from utils.pdf_style import draw_brand_header, draw_footer, draw_photo


def open_profile(parent, title, record, fields):
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry("640x560")
    window.transient(parent.winfo_toplevel())
    window.columnconfigure(0, weight=1)
    ttk.Label(window, text=title, font=("TkDefaultFont", 19, "bold")).pack(anchor="w", padx=20, pady=(18, 2))
    ttk.Label(window, text="Offline profile view", foreground="#5d7180").pack(anchor="w", padx=20)
    body = ttk.Frame(window, padding=20)
    body.pack(fill="both", expand=True)
    for label, key in fields:
        ttk.Label(body, text=f"{label}: {record.get(key) or '-'}").pack(anchor="w", pady=4)
    ttk.Button(window, text="Export PDF", command=lambda: export_pdf(title, record, fields)).pack(pady=(0, 16))
    return window


def export_pdf(title, record, fields):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return messagebox.showwarning("PDF Export", "PDF export-এর জন্য reportlab install করুন: pip install reportlab")
    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="profile.pdf")
    if not path:
        return
    try:
        pdf = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        settings = dict(query("SELECT * FROM settings WHERE id=1")[0])
        y = draw_brand_header(pdf, title, settings, width, height)
        draw_photo(pdf, record.get("photo_path"), width - 120, height - 205, 78)
        pdf.setFont("Helvetica", 10)
        for label, key in fields:
            pdf.setFillColorRGB(0.15, 0.2, 0.23)
            pdf.drawString(48, y, f"{label}: {record.get(key) or '-'}")
            y -= 18
            if y < 40:
                draw_footer(pdf, width)
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = draw_brand_header(pdf, title, settings, width, height)
        draw_footer(pdf, width)
        pdf.save()
        messagebox.showinfo("Export Complete", f"Profile PDF saved:\n{path}")
    except Exception as error:
        messagebox.showerror("PDF Error", str(error))
