import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.db import init_db, log_activity, query
from utils.helpers import backup_database
from config import APP_NAME, APP_VERSION, DEVELOPER
from ui.login import LoginFrame
from ui.dashboard import DashboardFrame
from ui.students import StudentFrame
from ui.teachers import PersonFrame as TeacherFrame
from ui.staff import PersonFrame as StaffFrame
from ui.classes import ClassesFrame
from ui.attendance import AttendanceFrame
from ui.users import UsersFrame
from ui.settings import SettingsFrame
from ui.fees import FeesFrame
from ui.exams import ExamsFrame
from ui.reports import ReportsFrame
from ui.certificates import CertificatesFrame
from ui.id_cards import IDCardFrame
from ui.phase6 import PermissionsFrame, LogsFrame

class SchoolManagementApp:
    def __init__(self):
        init_db()
        backup_database()
        self.root=tk.Tk()
        self.theme=query("SELECT theme FROM settings WHERE id=1")[0]["theme"]
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1250x760");self.root.minsize(1050,650)
        self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.style();self.user=None;self.show_login()
    def style(self):
        s=ttk.Style(self.root)
        try:s.theme_use("clam")
        except tk.TclError:pass
        colors=("#ffffff","#263238","#f4f7f9") if self.theme=="Light" else ("#263238","#f2f6f8","#1d252b")
        panel="#ffffff" if self.theme=="Light" else "#263238"
        border="#dce5ea" if self.theme=="Light" else "#46565f"
        muted="#5d7180" if self.theme=="Light" else "#b8c6cc"
        s.configure(".",font=("TkDefaultFont",10))
        s.configure("Treeview",rowheight=32,background=colors[0],fieldbackground=colors[0],foreground=colors[1],borderwidth=0,relief="flat")
        s.map("Treeview",background=[("selected","#2a9d8f")],foreground=[("selected","#ffffff")])
        s.configure("Treeview.Heading",font=("TkDefaultFont",10,"bold"),background="#e8eef2" if self.theme=="Light" else "#34434a",foreground="#263238" if self.theme=="Light" else "#f2f6f8",padding=(8,7),relief="flat")
        s.configure("TButton",padding=(12,7),font=("TkDefaultFont",10),background=panel,foreground=colors[1],bordercolor=border)
        s.map("TButton",background=[("active","#dcefeb" if self.theme=="Light" else "#34515d")])
        s.configure("TEntry",padding=(7,6),fieldbackground=panel,foreground=colors[1],bordercolor=border)
        s.configure("TCombobox",padding=(7,5),fieldbackground=panel,foreground=colors[1],bordercolor=border)
        s.configure("TLabelframe",background=colors[2],bordercolor=border,relief="solid",borderwidth=1)
        s.configure("TLabelframe.Label",background=colors[2],foreground=colors[1],font=("TkDefaultFont",10,"bold"))
        s.configure("TNotebook",background=colors[2],borderwidth=0,tabmargins=(4,4,4,0))
        s.configure("TNotebook.Tab",padding=(14,8),background="#e8eef2" if self.theme=="Light" else "#34434a",foreground=muted)
        s.map("TNotebook.Tab",background=[("selected","#2a9d8f")],foreground=[("selected","#ffffff")])
        s.configure("TCheckbutton",background=colors[2],foreground=colors[1])
        s.configure("TLabel",background=colors[2],foreground=colors[1])
        s.configure("Nav.TButton",padding=(12,9),anchor="w",background="#17324d",foreground="#dce8f0",borderwidth=0)
        s.map("Nav.TButton",background=[("active","#244b6d")],foreground=[("active","#ffffff")])
        s.configure("Active.Nav.TButton",padding=(12,9),anchor="w",background="#2a9d8f",foreground="#ffffff",borderwidth=0)
        s.configure("Dashboard.TFrame",background=colors[2])
        s.configure("Dashboard.TLabel",background=colors[2],foreground=colors[1])
    def clear(self):
        for w in self.root.winfo_children():w.destroy()
    def show_login(self):
        self.root.unbind("<Control-k>")
        for index in range(1,10):self.root.unbind(f"<Control-Key-{index}>")
        for sequence in ("<Control-b>","<Alt-Up>","<Alt-Down>","<Alt-Return>","<Control-r>","<F5>"):self.root.unbind(sequence)
        self.clear();LoginFrame(self.root,self.login_success).pack(fill="both",expand=True)
    def login_success(self,user):
        self.user=user;self.show_main()
    def show_main(self):
        self.clear()
        dark=self.theme=="Dark"; shell_bg="#1d252b" if dark else "#f4f7f9"; side_bg="#111f2b" if dark else "#17324d"; side_accent="#203b4e" if dark else "#244b6d"
        main=tk.Frame(self.root,bg=shell_bg);main.pack(fill="both",expand=True)
        side_shell=tk.Frame(main,width=252,bg=side_bg);side_shell.pack(side="left",fill="y");side_shell.pack_propagate(False)
        side_canvas=tk.Canvas(side_shell,bg=side_bg,highlightthickness=0,borderwidth=0)
        side_scroll=ttk.Scrollbar(side_shell,orient="vertical",command=side_canvas.yview)
        side_canvas.configure(yscrollcommand=side_scroll.set)
        side_canvas.pack(side="left",fill="both",expand=True);side_scroll.pack(side="right",fill="y")
        side=tk.Frame(side_canvas,padx=12,pady=14,bg=side_bg)
        side_window=side_canvas.create_window((0,0),window=side,anchor="nw")
        side.bind("<Configure>",lambda _event:side_canvas.configure(scrollregion=side_canvas.bbox("all")))
        side_canvas.bind("<Configure>",lambda event:side_canvas.itemconfigure(side_window,width=event.width))
        side_canvas.bind("<Enter>",lambda _event:side_canvas.bind_all("<MouseWheel>",lambda event:side_canvas.yview_scroll(int(-event.delta/120),"units")))
        side_canvas.bind("<Leave>",lambda _event:side_canvas.unbind_all("<MouseWheel>"))
        content_shell=tk.Frame(main,bg=shell_bg);content_shell.pack(side="right",fill="both",expand=True)
        topbar=tk.Frame(content_shell,bg="#ffffff" if not dark else "#263238",height=58,padx=22);topbar.pack(fill="x");topbar.pack_propagate(False)
        self.side_shell=side_shell;self.content_shell=content_shell;self.sidebar_collapsed=False
        tk.Button(topbar,text="☰",command=self.toggle_sidebar,font=("Segoe UI Symbol",16),relief="flat",bg=topbar["bg"],fg="#2a9d8f",activebackground=topbar["bg"],cursor="hand2").pack(side="left",padx=(0,12))
        self.page_title=tk.Label(topbar,text="Dashboard",font=("TkDefaultFont",15,"bold"),bg=topbar["bg"],fg="#17324d" if not dark else "#f2f6f8");self.page_title.pack(side="left",pady=16)
        tk.Label(topbar,text=f"{self.user['full_name']}  •  {self.user['role']}",font=("TkDefaultFont",9),bg=topbar["bg"],fg="#5d7180" if not dark else "#b8c6cc").pack(side="right",pady=18)
        self.content=ttk.Frame(content_shell,style="Dashboard.TFrame");self.content.pack(fill="both",expand=True)
        statusbar=tk.Frame(content_shell,bg="#ffffff" if not dark else "#263238",height=28,padx=22);statusbar.pack(fill="x");statusbar.pack_propagate(False)
        tk.Label(statusbar,text="●  OFFLINE MODE",font=("TkDefaultFont",8,"bold"),bg=statusbar["bg"],fg="#2a9d8f").pack(side="left",pady=6)
        tk.Label(statusbar,text="Local database active",font=("TkDefaultFont",8),bg=statusbar["bg"],fg="#5d7180" if not dark else "#b8c6cc").pack(side="left",padx=(14,0),pady=6)
        self.clock_label=tk.Label(statusbar,font=("TkDefaultFont",8),bg=statusbar["bg"],fg="#5d7180" if not dark else "#b8c6cc");self.clock_label.pack(side="right",pady=6)
        self.update_clock()
        tk.Label(side,text="🏫",font=("Segoe UI Emoji",30),bg=side_bg,fg="#ffffff").pack()
        tk.Label(side,text="School Manager",font=("TkDefaultFont",15,"bold"),bg=side_bg,fg="#ffffff").pack(pady=(0,18))
        tk.Label(side,text=f"OFFLINE EDITION  •  v{APP_VERSION}",font=("TkDefaultFont",8,"bold"),bg=side_bg,fg="#79c7bd").pack(pady=(0,12))
        search_box=tk.Frame(side,bg=side_accent,padx=7,pady=7);search_box.pack(fill="x",pady=(0,12))
        self.global_search=tk.StringVar()
        search_entry=tk.Entry(search_box,textvariable=self.global_search,relief="flat",bg="#ffffff",fg="#263238")
        search_entry.pack(side="left",fill="x",expand=True);search_entry.bind("<Return>",lambda _event:self.search_everywhere())
        tk.Button(search_box,text="🔎",command=self.search_everywhere,relief="flat",bg="#2a9d8f",fg="#ffffff",activebackground="#238276").pack(side="right",padx=(5,0))
        self.root.bind("<Control-k>",lambda _event:(search_entry.focus_set(),"break")[1])
        all_items=[("📊 Dashboard","Dashboard",self.dashboard),("👨‍🎓 শিক্ষার্থী","Students",self.students),("👨‍🏫 শিক্ষক","Teachers",self.teachers),
             ("👨‍💼 Staff","Staff",self.staff),("📅 Attendance","Attendance",self.attendance),("📚 Class","Classes",self.classes),
             ("💰 Fees & Payment","Fees",self.fees),("📝 Exams & Results","Exams",self.exams),("📊 Reports & Backup","Reports",self.reports),("🎓 Certificates","Certificates",self.certificates),("🪪 ID Cards","IDCards",self.id_cards),
              ("👤 Users","Users",self.users),("🔐 Permissions","Permissions",self.permissions),("🧾 Activity Logs","Logs",self.logs),("⚙️ Settings","Settings",self.settings)]
        items=[(label,callback) for label,module,callback in all_items if self.can_view(module)]
        self.nav_buttons=[]
        for t,c in items:
            button=ttk.Button(side,text=t,style="Nav.TButton",command=lambda callback=c: self.navigate(callback))
            button.pack(fill="x",pady=2);button.configure(cursor="hand2");self.nav_buttons.append((button,c))
        if self.nav_buttons:self.nav_buttons[0][0].configure(style="Active.Nav.TButton")
        shortcuts=[self.dashboard,self.students,self.teachers,self.staff,self.attendance,self.classes,self.fees,self.exams,self.reports]
        for index,callback in enumerate(shortcuts,1):self.root.bind(f"<Control-Key-{index}>",lambda _event,target=callback:self.navigate(target))
        self.nav_index=0
        self.root.bind("<Control-b>",lambda _event:(self.toggle_sidebar(),"break")[1])
        self.root.bind("<Alt-Up>",lambda _event:(self.move_nav(-1),"break")[1])
        self.root.bind("<Alt-Down>",lambda _event:(self.move_nav(1),"break")[1])
        self.root.bind("<Alt-Return>",lambda _event:(self.activate_nav(),"break")[1])
        self.root.bind("<Control-r>",lambda _event:(self.refresh_current(),"break")[1])
        self.root.bind("<F5>",lambda _event:(self.refresh_current(),"break")[1])
        ttk.Separator(side).pack(fill="x",pady=14)
        ttk.Button(side,text="🚪 Logout",style="Nav.TButton",command=self.logout).pack(fill="x")
        tk.Label(side,text=f"{self.user['full_name']}\n{self.user['role']}\n\nDeveloped by\n{DEVELOPER}",font=("TkDefaultFont",9),bg=side_bg,fg="#a9bfce",justify="left").pack(side="bottom",anchor="w")
        self.dashboard()
    def update_clock(self):
        if hasattr(self,"clock_label") and self.clock_label.winfo_exists():
            self.clock_label.configure(text=datetime.now().strftime("%d %b %Y  •  %I:%M:%S %p"))
            self.root.after(1000,self.update_clock)
    def navigate(self, callback):
        for button, target in self.nav_buttons:
            button.configure(style="Active.Nav.TButton" if target == callback else "Nav.TButton")
        for index,(_,target) in enumerate(self.nav_buttons):
            if target==callback:self.nav_index=index;break
        self.page_title.configure(text=callback.__name__.replace("_", " ").title())
        callback()
    def refresh_current(self):
        if hasattr(self,"current_refresh"):self.current_refresh()
    def toggle_sidebar(self):
        if self.sidebar_collapsed:
            self.side_shell.pack(side="left",fill="y",before=self.content_shell)
            self.sidebar_collapsed=False
        else:
            self.side_shell.pack_forget();self.sidebar_collapsed=True
    def move_nav(self, step):
        if not self.nav_buttons:return
        self.nav_index=(self.nav_index+step)%len(self.nav_buttons)
        self.nav_buttons[self.nav_index][0].focus_set()
    def activate_nav(self):
        if self.nav_buttons:self.nav_buttons[self.nav_index][0].invoke()
    def can_view(self, module):
        if self.user.get("role")=="Admin":return True
        rows=query("SELECT can_view FROM permissions WHERE role=? AND module=?",(self.user.get("role"),module))
        return bool(rows and rows[0]["can_view"])
    def search_everywhere(self):
        term=self.global_search.get().strip()
        if not term:return
        from database.db import query
        like=f"%{term}%"
        results=[]
        for row in query("SELECT student_id AS code,name,class_name AS detail,phone FROM students WHERE student_id LIKE ? OR name LIKE ? OR phone LIKE ? OR class_name LIKE ? ORDER BY name",(like,like,like,like)):
            results.append(("Student",row["code"],row["name"],row["detail"] or "",row["phone"] or ""))
        for row in query("SELECT teacher_id AS code,name,subject AS detail,phone FROM teachers WHERE teacher_id LIKE ? OR name LIKE ? OR phone LIKE ? OR subject LIKE ? ORDER BY name",(like,like,like,like)):
            results.append(("Teacher",row["code"],row["name"],row["detail"] or "",row["phone"] or ""))
        for row in query("SELECT staff_id AS code,name,designation AS detail,phone FROM staff WHERE staff_id LIKE ? OR name LIKE ? OR phone LIKE ? OR designation LIKE ? ORDER BY name",(like,like,like,like)):
            results.append(("Staff",row["code"],row["name"],row["detail"] or "",row["phone"] or ""))
        for row in query("SELECT receipt_no AS code,student_name AS name,fee_type AS detail,payment_date AS phone FROM fee_payments WHERE receipt_no LIKE ? OR student_name LIKE ? OR fee_type LIKE ? ORDER BY id DESC",(like,like,like)):
            results.append(("Payment",row["code"],row["name"],row["detail"] or "",row["phone"] or ""))
        win=tk.Toplevel(self.root);win.title(f"Search results: {term}");win.geometry("760x420");win.transient(self.root)
        win.bind("<Escape>",lambda _event:win.destroy())
        ttk.Label(win,text=f"{len(results)} result(s) found",font=("TkDefaultFont",11,"bold")).pack(anchor="w",padx=12,pady=(12,6))
        tree=ttk.Treeview(win,columns=("type","code","name","detail","contact"),show="headings")
        for column,title,width in [("type","Type",100),("code","ID / Receipt",140),("name","Name",200),("detail","Class / Subject / Fee",170),("contact","Phone / Date",130)]:
            tree.heading(column,text=title);tree.column(column,width=width)
        tree.pack(fill="both",expand=True,padx=12,pady=(0,12))
        for result in results:tree.insert("","end",values=result)
    def show(self,cls,*args):
        self.unbind_page_scroll()
        self.current_refresh=lambda:self.show(cls,*args)
        for w in self.content.winfo_children():w.destroy()
        if cls is DashboardFrame:
            viewport=ttk.Frame(self.content,style="Dashboard.TFrame");viewport.pack(fill="both",expand=True)
            canvas=tk.Canvas(viewport,background="#1d252b" if self.theme=="Dark" else "#f4f7f9",highlightthickness=0,borderwidth=0)
            scrollbar=ttk.Scrollbar(viewport,orient="vertical",command=canvas.yview);canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left",fill="both",expand=True);scrollbar.pack(side="right",fill="y")
            page=ttk.Frame(canvas,style="Dashboard.TFrame");window_id=canvas.create_window((0,0),window=page,anchor="nw")
            page.bind("<Configure>",lambda _event:canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>",lambda event:canvas.itemconfigure(window_id,width=event.width))
            canvas.bind("<Enter>",lambda _event:self.bind_page_scroll(canvas))
            canvas.bind("<Leave>",lambda _event:self.unbind_page_scroll())
            view=cls(page,*args);view.pack(fill="both",expand=True)
            self.enhance_tables(view)
            return
        titles={
            StudentFrame:("Students","Manage student profiles, academic details and records"),
            TeacherFrame:("Teachers","Manage teaching staff and contact information"),
            StaffFrame:("Staff","Manage administrative staff and records"),
            AttendanceFrame:("Attendance","Record and review daily attendance"),
            ClassesFrame:("Classes & Subjects","Organize classes, sections and subjects"),
            FeesFrame:("Fees & Payments","Collect payments and manage student dues"),
            ExamsFrame:("Exams & Results","Manage exams, marks and academic performance"),
            ReportsFrame:("Reports & Backup","Generate reports and protect local data"),
            CertificatesFrame:("Certificates","Create student certificates and testimonials"),
            IDCardFrame:("ID Cards","Preview and export student identification cards"),
            UsersFrame:("Users & Access","Manage accounts, roles and access status"),
            PermissionsFrame:("Permissions","Configure offline role-based access"),
            LogsFrame:("Activity Logs","Review local user actions and security events"),
            SettingsFrame:("Settings","Configure school identity and application preferences"),
        }
        icons={StudentFrame:"👨‍🎓",TeacherFrame:"👨‍🏫",StaffFrame:"👨‍💼",AttendanceFrame:"📅",ClassesFrame:"📚",FeesFrame:"💰",ExamsFrame:"📝",ReportsFrame:"📊",CertificatesFrame:"🎓",IDCardFrame:"🪪",UsersFrame:"👤",SettingsFrame:"⚙️"}
        title,subtitle=titles.get(cls,(cls.__name__.replace("Frame", ""),"Manage school information"))
        viewport=ttk.Frame(self.content,style="Dashboard.TFrame");viewport.pack(fill="both",expand=True)
        canvas=tk.Canvas(viewport,background="#1d252b" if self.theme=="Dark" else "#f4f7f9",highlightthickness=0,borderwidth=0)
        scrollbar=ttk.Scrollbar(viewport,orient="vertical",command=canvas.yview);canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left",fill="both",expand=True);scrollbar.pack(side="right",fill="y")
        page=ttk.Frame(canvas,style="Dashboard.TFrame");window_id=canvas.create_window((0,0),window=page,anchor="nw")
        page.bind("<Configure>",lambda _event:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda event:canvas.itemconfigure(window_id,width=event.width))
        canvas.bind("<Enter>",lambda _event:self.bind_page_scroll(canvas))
        canvas.bind("<Leave>",lambda _event:self.unbind_page_scroll())
        header=ttk.Frame(page,style="Dashboard.TFrame");header.pack(fill="x",padx=24,pady=(18,0))
        toolbar=ttk.Frame(header,style="Dashboard.TFrame");toolbar.pack(fill="x")
        ttk.Label(toolbar,text=f"{icons.get(cls,'•')}  {title}",font=("TkDefaultFont",18,"bold"),style="Dashboard.TLabel").pack(side="left")
        ttk.Button(toolbar,text="↻ Refresh",command=lambda:self.show(cls,*args)).pack(side="right",padx=(6,0))
        ttk.Button(toolbar,text="⌂ Home",command=self.dashboard).pack(side="right")
        ttk.Label(header,text=subtitle,foreground="#5d7180",style="Dashboard.TLabel").pack(anchor="w",pady=(2,10))
        ttk.Separator(page).pack(fill="x",padx=24)
        view=cls(page,*args);view.pack(fill="both",expand=True,padx=12,pady=(4,0))
        self.enhance_tables(view)

    def bind_page_scroll(self, canvas):
        self.unbind_page_scroll()
        self.page_scroll_canvas=canvas
        self.root.bind_all("<MouseWheel>",lambda event:canvas.yview_scroll(int(-event.delta/120),"units"),add="+")

    def unbind_page_scroll(self):
        if hasattr(self,"page_scroll_canvas"):
            self.root.unbind_all("<MouseWheel>")
            del self.page_scroll_canvas

    def enhance_tables(self, widget):
        for child in widget.winfo_children():
            if isinstance(child,ttk.Treeview):self.make_sortable(child)
            self.enhance_tables(child)

    @staticmethod
    def make_sortable(tree):
        directions={}
        for column in tree["columns"]:
            tree.heading(column,command=lambda column=column: SchoolManagementApp.sort_table(tree,column,directions))

    @staticmethod
    def sort_table(tree,column,directions):
        rows=[(tree.set(item,column),item) for item in tree.get_children("")]
        reverse=directions.get(column,False)
        def sort_key(pair):
            value=pair[0].strip()
            try:return (0,float(value.replace(",","").replace("৳ ","")))
            except ValueError:return (1,value.casefold())
        rows.sort(key=sort_key,reverse=reverse)
        for index,(_,item) in enumerate(rows):tree.move(item,"",index)
        directions[column]=not reverse
    def dashboard(self):
        if hasattr(self,"page_title"):self.page_title.configure(text="Dashboard")
        self.show(DashboardFrame,{"students":self.students,"attendance":self.attendance,"fees":self.fees,"refresh":self.dashboard})
    def students(self):self.show(StudentFrame,self.user,self.dashboard)
    def teachers(self):self.show(TeacherFrame,self.user)
    def staff(self):self.show(StaffFrame,self.user)
    def attendance(self):self.show(AttendanceFrame,self.user)
    def classes(self):self.show(ClassesFrame,self.user)
    def fees(self):self.show(FeesFrame,self.user)
    def exams(self):self.show(ExamsFrame,self.user)
    def reports(self):self.show(ReportsFrame,self.user)
    def certificates(self):self.show(CertificatesFrame,self.user)
    def id_cards(self):self.show(IDCardFrame,self.user)
    def users(self):self.show(UsersFrame,self.user)
    def permissions(self):self.show(PermissionsFrame,self.user)
    def logs(self):self.show(LogsFrame,self.user)
    def settings(self):self.show(SettingsFrame,self.user,self.apply_theme)
    def apply_theme(self, theme):
        self.theme=theme;self.style();self.show_main()
    def logout(self):
        if messagebox.askyesno("Logout","আপনি কি Logout করতে চান?"):
            log_activity(self.user["username"],"Logged out");self.user=None;self.show_login()
    def close(self):self.root.destroy()
    def run(self):self.root.mainloop()
