import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime


class PopupForm(tk.Toplevel):
    def __init__(self, parent, title, fields, values=None, on_save=None, on_change=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("560x520")
        self.minsize(480, 360)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.on_save = on_save
        self.on_change = on_change
        self.variables = {}
        values = values or {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        viewport = ttk.Frame(self)
        viewport.grid(row=0, column=0, sticky="nsew")
        viewport.rowconfigure(0, weight=1)
        viewport.columnconfigure(0, weight=1)
        canvas = tk.Canvas(viewport, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        form = ttk.Frame(canvas, padding=20)
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(form_window, width=event.width))
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units")))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        form.columnconfigure(1, weight=1)
        for row, field in enumerate(fields):
            label, key, choices = field[:3]
            field_type = field[3] if len(field) > 3 else ""
            self.variables[key] = tk.StringVar(value=str(values.get(key, "") or ""))
            if self.on_change:self.variables[key].trace_add("write",lambda *_args:self.on_change(self.variables))
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=6)
            if field_type == "date":
                date_frame = ttk.Frame(form)
                date_frame.grid(row=row, column=1, sticky="ew", padx=6, pady=6)
                date_frame.columnconfigure(0, weight=1)
                widget = ttk.Entry(date_frame, textvariable=self.variables[key])
                widget.grid(row=0, column=0, sticky="ew")
                ttk.Button(date_frame, text="Calendar", command=lambda variable=self.variables[key]: self.open_calendar(variable)).grid(row=0, column=1, padx=(5, 0))
                continue
            if choices:
                widget = ttk.Combobox(form, textvariable=self.variables[key], values=choices, state="readonly")
            else:
                widget = ttk.Entry(form, textvariable=self.variables[key])
            widget.grid(row=row, column=1, sticky="ew", padx=6, pady=6)
        actions = ttk.Frame(form)
        actions.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(18, 0))
        ttk.Button(actions, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(actions, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Return>", lambda _event: self.save())

    def save(self):
        values = {key: variable.get().strip() for key, variable in self.variables.items()}
        if self.on_save and self.on_save(values) is not False:
            self.destroy()

    def open_calendar(self, variable):
        window = tk.Toplevel(self)
        window.title("Select Date")
        window.transient(self)
        window.grab_set()
        now = datetime.now()
        month = tk.IntVar(value=now.month)
        year = tk.IntVar(value=now.year)
        header = ttk.Frame(window, padding=8); header.pack(fill="x")
        ttk.Button(header, text="‹", width=3, command=lambda: change_month(-1)).pack(side="left")
        month_select = ttk.Combobox(header, values=list(range(1, 13)), textvariable=month, state="readonly", width=4)
        month_select.pack(side="left", padx=4)
        year_select = ttk.Spinbox(header, from_=1900, to=2200, textvariable=year, width=6, command=lambda: render())
        year_select.pack(side="left", padx=4)
        ttk.Button(header, text="›", width=3, command=lambda: change_month(1)).pack(side="right")
        days = ttk.Frame(window, padding=(8, 0, 8, 8)); days.pack()

        def choose(day):
            variable.set(f"{year.get():04d}-{month.get():02d}-{day:02d}")
            window.destroy()

        def render():
            for child in days.winfo_children(): child.destroy()
            month_select.set(month.get()); year_select.set(year.get())
            for column, name in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
                ttk.Label(days, text=name, width=4, anchor="center").grid(row=0, column=column)
            for index, day in enumerate(calendar.monthcalendar(year.get(), month.get())):
                for column, value in enumerate(day):
                    if value: ttk.Button(days, text=str(value), width=4, command=lambda value=value: choose(value)).grid(row=index + 1, column=column, padx=1, pady=1)

        def change_month(step):
            value = month.get() + step
            if value == 0: month.set(12); year.set(year.get() - 1)
            elif value == 13: month.set(1); year.set(year.get() + 1)
            else: month.set(value)
            render()

        render()
        month_select.bind("<<ComboboxSelected>>", lambda _event: render())
        ttk.Button(window, text="Today", command=lambda: (variable.set(now.strftime("%Y-%m-%d")), window.destroy())).pack(side="left", padx=8, pady=(0, 8))
        ttk.Button(window, text="Clear", command=lambda: (variable.set(""), window.destroy())).pack(side="right", padx=8, pady=(0, 8))
