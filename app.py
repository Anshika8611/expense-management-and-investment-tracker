import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import hashlib
import os
from datetime import datetime, date
import json

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expense_tracker.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        investment_password_hash TEXT,
        nominee_passkey_hash TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS nominees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        relation TEXT,
        contact TEXT,
        id_type TEXT,
        id_number TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        amount REAL NOT NULL,
        description TEXT,
        payment_mode TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        current_value REAL,
        return_rate REAL,
        maturity_date TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        purchase_date TEXT,
        purchase_value REAL,
        current_value REAL,
        location TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lending (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        borrower_name TEXT NOT NULL,
        contact TEXT,
        amount REAL NOT NULL,
        due_date TEXT,
        interest_rate REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── STYLES ───────────────────────────────────────────────────────────────────

BG        = "#0F1117"
BG2       = "#1A1D27"
BG3       = "#22263A"
ACCENT    = "#6C63FF"
ACCENT2   = "#00D4AA"
DANGER    = "#FF4757"
WARNING   = "#FFA502"
TEXT      = "#E8E8F0"
TEXT_DIM  = "#7F84A0"
CARD      = "#1E2235"
BORDER    = "#2E3250"

FONT_H1   = ("Georgia", 24, "bold")
FONT_H2   = ("Georgia", 18, "bold")
FONT_H3   = ("Courier New", 13, "bold")
FONT_BODY = ("Courier New", 11)
FONT_SM   = ("Courier New", 10)
FONT_BTN  = ("Courier New", 11, "bold")

EXPENSE_CATEGORIES = {
    "🍔 Food & Dining": ["Groceries", "Restaurant", "Fast Food", "Beverages", "Snacks", "Other"],
    "🚗 Transport": ["Fuel", "Public Transport", "Cab/Taxi", "Vehicle Maintenance", "Parking", "Other"],
    "🏠 Housing": ["Rent", "Electricity", "Water", "Internet", "Gas", "Maintenance", "Other"],
    "🛍️ Shopping": ["Clothing", "Electronics", "Household", "Accessories", "Online Shopping", "Other"],
    "🏥 Health": ["Medicine", "Doctor", "Hospital", "Insurance", "Fitness", "Other"],
    "🎓 Education": ["Tuition", "Books", "Courses", "Stationery", "Other"],
    "🎉 Entertainment": ["Movies", "Events", "Subscriptions", "Hobbies", "Travel", "Other"],
    "💳 Finance": ["EMI", "Loan Payment", "Insurance Premium", "Investment", "Other"],
    "👨‍👩‍👧 Family": ["Kids Education", "Gifts", "Family Events", "Other"],
    "📦 Other": ["Miscellaneous", "Charity", "Emergency", "Other"],
}

INVESTMENT_TYPES = ["Mutual Fund", "Stocks/Equity", "Fixed Deposit", "PPF", "Gold", "Real Estate", "Crypto", "Bonds", "NPS", "Other"]
ASSET_TYPES      = ["Real Estate", "Vehicle", "Gold/Jewelry", "Electronics", "Furniture", "Land", "Other"]
PAYMENT_MODES    = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Cheque", "Other"]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def styled_button(parent, text, command, color=ACCENT, fg=TEXT, width=None, pady=8):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, font=FONT_BTN,
                    relief="flat", cursor="hand2",
                    pady=pady, padx=16,
                    activebackground=color, activeforeground=fg)
    if width:
        btn.config(width=width)
    def on_enter(e): btn.config(bg=_lighten(color))
    def on_leave(e): btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def _lighten(hex_color):
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color

def label_entry(parent, label_text, row, col=0, show=None, width=28):
    tk.Label(parent, text=label_text, bg=BG2, fg=TEXT_DIM, font=FONT_SM).grid(row=row, column=col, sticky="w", padx=8, pady=(8,0))
    entry = tk.Entry(parent, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT,
                     relief="flat", bd=6, width=width)
    if show:
        entry.config(show=show)
    entry.grid(row=row+1, column=col, padx=8, pady=(0,4), sticky="ew")
    return entry

def section_title(parent, text, bg=BG):
    f = tk.Frame(parent, bg=bg)
    f.pack(fill="x", pady=(18, 4))
    tk.Label(f, text=text, bg=bg, fg=ACCENT, font=FONT_H3).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=8)
    return f

def card_frame(parent, **kwargs):
    return tk.Frame(parent, bg=CARD, bd=0, relief="flat", **kwargs)

def scrollable_frame(parent, bg=BG):
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return container, inner

# ─── AUTH WINDOW ──────────────────────────────────────────────────────────────

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ExpenseIQ — Login")
        self.geometry("480x600")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.logged_in_user = None
        self._build()

    def _build(self):
        self.frames = {}
        for F in (LoginFrame, SignupFrame):
            frame = F(self, self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)
        self.show_frame(LoginFrame)

    def show_frame(self, cls):
        self.frames[cls].tkraise()

    def on_login(self, user_id, username, full_name):
        self.logged_in_user = {"id": user_id, "username": username, "full_name": full_name}
        self.destroy()

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="💰", bg=BG, font=("Arial", 48)).pack(pady=(50,4))
        tk.Label(self, text="ExpenseIQ", bg=BG, fg=ACCENT, font=FONT_H1).pack()
        tk.Label(self, text="Smart Money. Clear Mind.", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(pady=(2, 30))

        card = card_frame(self)
        card.pack(padx=50, pady=10, fill="x")

        inner = tk.Frame(card, bg=CARD)
        inner.pack(padx=24, pady=24, fill="x")

        tk.Label(inner, text="USERNAME", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.user_entry = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.user_entry.pack(fill="x", pady=(2,12))

        tk.Label(inner, text="PASSWORD", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.pass_entry = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, show="●")
        self.pass_entry.pack(fill="x", pady=(2,20))
        self.pass_entry.bind("<Return>", lambda e: self.login())

        styled_button(inner, "SIGN IN →", self.login, width=30).pack(fill="x")

        tk.Label(self, text="Don't have an account?", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(pady=(16,2))
        tk.Label(self, text="Create Account", bg=BG, fg=ACCENT, font=(FONT_SM[0], FONT_SM[1], "underline"),
                 cursor="hand2").pack()
        self.winfo_children()[-1].bind("<Button-1>", lambda e: self.controller.show_frame(SignupFrame))

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.", parent=self)
            return
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, full_name FROM users WHERE username=? AND password_hash=?",
                  (username, hash_password(password)))
        row = c.fetchone()
        conn.close()
        if row:
            self.controller.on_login(row[0], row[1], row[2] or row[1])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)

class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="Create Account", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(36, 4))
        tk.Label(self, text="Join ExpenseIQ today", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(pady=(0,16))

        card = card_frame(self)
        card.pack(padx=40, pady=8, fill="x")
        inner = tk.Frame(card, bg=CARD)
        inner.pack(padx=24, pady=24, fill="x")

        fields = [("FULL NAME", False), ("USERNAME", False), ("EMAIL", False),
                  ("PASSWORD", True), ("CONFIRM PASSWORD", True)]
        self.entries = []
        for label, is_pass in fields:
            tk.Label(inner, text=label, bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
            e = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT,
                         relief="flat", bd=6, show="●" if is_pass else "")
            e.pack(fill="x", pady=(2, 10))
            self.entries.append(e)

        styled_button(inner, "CREATE ACCOUNT →", self.signup, color=ACCENT2, width=30).pack(fill="x")

        tk.Label(self, text="Already have an account?", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(pady=(12,2))
        lbl = tk.Label(self, text="Sign In", bg=BG, fg=ACCENT, font=(FONT_SM[0], FONT_SM[1], "underline"), cursor="hand2")
        lbl.pack()
        lbl.bind("<Button-1>", lambda e: self.controller.show_frame(LoginFrame))

    def signup(self):
        vals = [e.get().strip() for e in self.entries]
        full_name, username, email, password, confirm = vals
        if not all([username, password]):
            messagebox.showerror("Error", "Username and password are required.", parent=self); return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.", parent=self); return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.", parent=self); return
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password_hash, full_name, email) VALUES (?,?,?,?)",
                      (username, hash_password(password), full_name, email))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please sign in.", parent=self)
            self.controller.show_frame(LoginFrame)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.", parent=self)
        finally:
            conn.close()

# ─── MAIN APP ─────────────────────────────────────────────────────────────────

class MainApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"ExpenseIQ — {user['full_name']}")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg=BG)
        self._build()

    def _build(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=BG2, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="💰 ExpenseIQ", bg=BG2, fg=ACCENT, font=("Georgia", 15, "bold")).pack(pady=(24,4))
        tk.Label(sidebar, text=self.user['full_name'], bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(pady=(0,24))
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        pages_map = [
            ("🏠  Dashboard",    DashboardPage),
            ("💸  Expenses",     ExpensePage),
            ("📈  Investments",  InvestmentPage),
            ("🏦  Assets",       AssetPage),
            ("🤝  Money Lending",LendingPage),
            ("👤  Nominee",      NomineePage),
            ("📋  All Records",  RecordsPage),
        ]

        for label, PageClass in pages_map:
            page = PageClass(self.content, self.user)
            page.place(relwidth=1, relheight=1)
            self.pages[label] = page

            btn = tk.Button(sidebar, text=label, bg=BG2, fg=TEXT_DIM,
                            font=FONT_BTN, relief="flat", anchor="w",
                            padx=18, pady=12, cursor="hand2",
                            activebackground=BG3, activeforeground=ACCENT,
                            command=lambda l=label: self.show_page(l))
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=ACCENT, bg=BG3))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=TEXT_DIM, bg=BG2) if b != getattr(self,'_active_btn',None) else None)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16)
        styled_button(sidebar, "⚙  Settings", self.open_settings, color=BG3, pady=8).pack(fill="x", padx=12)
        styled_button(sidebar, "🔒  Logout", self.logout, color=DANGER, pady=8).pack(fill="x", padx=12, pady=6)

        self.show_page("🏠  Dashboard")

    def show_page(self, label):
        self.pages[label].tkraise()
        if hasattr(self.pages[label], 'refresh'):
            self.pages[label].refresh()

    def open_settings(self):
        SettingsWindow(self, self.user)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            launch()

# ─── DASHBOARD PAGE ───────────────────────────────────────────────────────────

class DashboardPage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        now = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(top, text=f"Welcome back, {self.user['full_name']} 👋", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        tk.Label(top, text=now, bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(side="right", pady=(8,0))

        self.cards_frame = tk.Frame(self, bg=BG)
        self.cards_frame.pack(fill="x", padx=24, pady=8)

        self.chart_frame = tk.Frame(self, bg=BG)
        self.chart_frame.pack(fill="both", expand=True, padx=24, pady=8)

        self.refresh()

    def refresh(self):
        for w in self.cards_frame.winfo_children(): w.destroy()
        for w in self.chart_frame.winfo_children(): w.destroy()
        self._draw_stats()
        self._draw_recent()

    def _get_stats(self):
        conn = get_connection()
        c = conn.cursor()
        uid = self.user['id']
        month = datetime.now().strftime("%Y-%m")

        c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=? AND date LIKE ?", (uid, f"{month}%"))
        monthly_exp = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(amount),0) FROM investments WHERE user_id=?", (uid,))
        total_inv = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(current_value),0) FROM assets WHERE user_id=?", (uid,))
        total_assets = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM lending WHERE user_id=? AND status='Pending'", (uid,))
        pending_loans = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(amount),0) FROM lending WHERE user_id=? AND status='Pending'", (uid,))
        pending_amt = c.fetchone()[0]

        conn.close()
        return monthly_exp, total_inv, total_assets, pending_loans, pending_amt

    def _draw_stats(self):
        me, ti, ta, pl, pa = self._get_stats()
        stats = [
            ("This Month\nExpenses", f"₹{me:,.0f}", DANGER),
            ("Total\nInvestments", f"₹{ti:,.0f}", ACCENT),
            ("Asset\nValue", f"₹{ta:,.0f}", ACCENT2),
            ("Pending\nLoans", f"{pl} (₹{pa:,.0f})", WARNING),
        ]
        for i, (label, val, color) in enumerate(stats):
            c = tk.Frame(self.cards_frame, bg=CARD, bd=0)
            c.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            self.cards_frame.columnconfigure(i, weight=1)
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            tk.Label(c, text=val, bg=CARD, fg=color, font=("Courier New", 18, "bold")).pack(pady=(14,2))
            tk.Label(c, text=label, bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(pady=(0,14))

    def _draw_recent(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT date, category, amount, description FROM expenses WHERE user_id=? ORDER BY created_at DESC LIMIT 8", (self.user['id'],))
        rows = c.fetchall()
        conn.close()

        left = tk.Frame(self.chart_frame, bg=CARD)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        tk.Label(left, text="📋 Recent Expenses", bg=CARD, fg=TEXT, font=FONT_H3).pack(anchor="w", padx=16, pady=(14,8))

        cols = ("Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(left, columns=cols, show="headings", height=8)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD,
                        font=FONT_SM, rowheight=28)
        style.configure("Treeview.Heading", background=BG3, foreground=ACCENT, font=FONT_H3)
        style.map("Treeview", background=[("selected", ACCENT)])

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130 if col != "Description" else 200)

        for row in rows:
            tree.insert("", "end", values=(row[0], row[1], f"₹{row[2]:,.2f}", row[3] or "—"))

        tree.pack(fill="both", expand=True, padx=16, pady=(0,16))

        # Category mini summary
        right = tk.Frame(self.chart_frame, bg=CARD, width=240)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="📊 This Month", bg=CARD, fg=TEXT, font=FONT_H3).pack(anchor="w", padx=16, pady=(14,8))

        conn = get_connection()
        c = conn.cursor()
        month = datetime.now().strftime("%Y-%m")
        c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? AND date LIKE ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 6",
                  (self.user['id'], f"{month}%"))
        cat_rows = c.fetchall()
        conn.close()

        if cat_rows:
            total = sum(r[1] for r in cat_rows)
            colors = [ACCENT, ACCENT2, WARNING, DANGER, "#FF6B81", "#A29BFE"]
            for i, (cat, amt) in enumerate(cat_rows):
                pct = amt / total if total else 0
                row_f = tk.Frame(right, bg=CARD)
                row_f.pack(fill="x", padx=16, pady=3)
                color = colors[i % len(colors)]
                tk.Label(row_f, text=cat[:20], bg=CARD, fg=TEXT, font=FONT_SM, width=16, anchor="w").pack(side="left")
                tk.Label(row_f, text=f"₹{amt:,.0f}", bg=CARD, fg=color, font=FONT_SM).pack(side="right")
                bar_f = tk.Frame(right, bg=BG3, height=4)
                bar_f.pack(fill="x", padx=16, pady=(0,2))
                tk.Frame(bar_f, bg=color, height=4, width=int(180*pct)).pack(side="left")
        else:
            tk.Label(right, text="No expenses\nthis month", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(pady=40)

# ─── EXPENSE PAGE ─────────────────────────────────────────────────────────────

class ExpensePage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        tk.Label(top, text="💸 Expense Tracker", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        styled_button(top, "+ Add Expense", self._show_add_form).pack(side="right")

        # Filter bar
        fb = tk.Frame(self, bg=BG2)
        fb.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(fb, text="Month:", bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(side="left", padx=(16,4), pady=8)
        self.month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        me = tk.Entry(fb, textvariable=self.month_var, font=FONT_BODY, bg=BG3, fg=TEXT,
                      insertbackground=TEXT, relief="flat", bd=4, width=10)
        me.pack(side="left", padx=4, pady=8)
        styled_button(fb, "Filter", self.refresh, color=BG3, pady=4).pack(side="left", padx=8)
        styled_button(fb, "Clear", lambda: [self.month_var.set(""), self.refresh()], color=BG3, pady=4).pack(side="left")

        self.total_lbl = tk.Label(fb, text="", bg=BG2, fg=ACCENT2, font=FONT_H3)
        self.total_lbl.pack(side="right", padx=16)

        # Table
        tcols = ("Date", "Category", "Sub-Category", "Amount", "Payment", "Description")
        self.tree = self._make_tree(tcols)
        self.tree.pack(fill="both", expand=True, padx=24, pady=8)
        self.tree.bind("<Delete>", self._delete_selected)

        styled_button(self, "🗑 Delete Selected", self._delete_selected, color=DANGER, pady=6).pack(anchor="e", padx=24, pady=8)
        self.refresh()

    def _make_tree(self, cols):
        frame = tk.Frame(self, bg=BG)
        style = ttk.Style()
        style.configure("Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, font=FONT_SM, rowheight=30)
        style.configure("Treeview.Heading", background=BG3, foreground=ACCENT, font=FONT_H3)
        style.map("Treeview", background=[("selected", ACCENT)])
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        widths = {"Date":90,"Category":160,"Sub-Category":120,"Amount":90,"Payment":110,"Description":250}
        for col in cols:
            tree.heading(col, text=col, command=lambda c=col: None)
            tree.column(col, width=widths.get(col, 100), anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree._parent_frame = frame
        return frame

    def refresh(self):
        for w in self.tree.winfo_children():
            if isinstance(w, ttk.Treeview):
                for i in w.get_children(): w.delete(i)

        conn = get_connection()
        c = conn.cursor()
        month = self.month_var.get().strip()
        if month:
            c.execute("SELECT id,date,category,sub_category,amount,payment_mode,description FROM expenses WHERE user_id=? AND date LIKE ? ORDER BY date DESC",
                      (self.user['id'], f"{month}%"))
        else:
            c.execute("SELECT id,date,category,sub_category,amount,payment_mode,description FROM expenses WHERE user_id=? ORDER BY date DESC",
                      (self.user['id'],))
        rows = c.fetchall()
        conn.close()

        total = 0
        for w in self.tree.winfo_children():
            if isinstance(w, ttk.Treeview):
                for row in rows:
                    w.insert("", "end", iid=row[0], values=(row[1],row[2],row[3] or "",f"₹{row[4]:,.2f}",row[5] or "",row[6] or ""))
                    total += row[4]
        self.total_lbl.config(text=f"Total: ₹{total:,.2f}")

    def _delete_selected(self, event=None):
        for w in self.tree.winfo_children():
            if isinstance(w, ttk.Treeview):
                sel = w.selection()
                if not sel: messagebox.showwarning("Select", "Select a row to delete."); return
                if messagebox.askyesno("Confirm", "Delete selected expense?"):
                    conn = get_connection()
                    conn.execute("DELETE FROM expenses WHERE id=?", (sel[0],))
                    conn.commit(); conn.close()
                    self.refresh()

    def _show_add_form(self):
        AddExpenseWindow(self, self.user, self.refresh)

class AddExpenseWindow(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.title("Add Expense")
        self.geometry("460x560")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self, text="Add New Expense", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(24,16))
        form = tk.Frame(self, bg=BG)
        form.pack(padx=32, fill="x")

        # Date
        tk.Label(form, text="DATE", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.date_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.date_e.insert(0, date.today().isoformat())
        self.date_e.pack(fill="x", pady=(2,10))

        # Category dropdown
        tk.Label(form, text="CATEGORY", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.cat_var = tk.StringVar(value=list(EXPENSE_CATEGORIES.keys())[0])
        cat_menu = ttk.Combobox(form, textvariable=self.cat_var, values=list(EXPENSE_CATEGORIES.keys()),
                                 font=FONT_BODY, state="readonly")
        cat_menu.pack(fill="x", pady=(2,10))
        cat_menu.bind("<<ComboboxSelected>>", self._update_subcats)

        # Sub-category
        tk.Label(form, text="SUB-CATEGORY", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.subcat_var = tk.StringVar()
        self.subcat_menu = ttk.Combobox(form, textvariable=self.subcat_var, font=FONT_BODY, state="readonly")
        self.subcat_menu.pack(fill="x", pady=(2,10))
        self._update_subcats()

        # Amount
        tk.Label(form, text="AMOUNT (₹)", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.amt_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.amt_e.pack(fill="x", pady=(2,10))

        # Payment mode
        tk.Label(form, text="PAYMENT MODE", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.pay_var = tk.StringVar(value=PAYMENT_MODES[0])
        ttk.Combobox(form, textvariable=self.pay_var, values=PAYMENT_MODES, font=FONT_BODY, state="readonly").pack(fill="x", pady=(2,10))

        # Description
        tk.Label(form, text="DESCRIPTION (optional)", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.desc_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.desc_e.pack(fill="x", pady=(2,16))

        styled_button(self, "💾  Save Expense", self._save, color=ACCENT2).pack(pady=8)

    def _update_subcats(self, event=None):
        cat = self.cat_var.get()
        subs = EXPENSE_CATEGORIES.get(cat, ["Other"])
        self.subcat_menu.config(values=subs)
        self.subcat_var.set(subs[0])

    def _save(self):
        try:
            amt = float(self.amt_e.get())
        except:
            messagebox.showerror("Error", "Enter a valid amount.", parent=self); return
        dt = self.date_e.get().strip()
        if not dt:
            messagebox.showerror("Error", "Enter a date.", parent=self); return
        conn = get_connection()
        conn.execute("INSERT INTO expenses (user_id,date,category,sub_category,amount,payment_mode,description) VALUES (?,?,?,?,?,?,?)",
                     (self.user['id'], dt, self.cat_var.get(), self.subcat_var.get(), amt, self.pay_var.get(), self.desc_e.get().strip()))
        conn.commit(); conn.close()
        self.on_save()
        self.destroy()
        messagebox.showinfo("Saved", "Expense added successfully!")

# ─── INVESTMENT PAGE ──────────────────────────────────────────────────────────

class InvestmentPage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self.unlocked = False
        self._build()

    def _build(self):
        self.lock_frame = tk.Frame(self, bg=BG)
        self.lock_frame.place(relwidth=1, relheight=1)
        tk.Label(self.lock_frame, text="🔒", bg=BG, font=("Arial", 64)).pack(pady=(120,8))
        tk.Label(self.lock_frame, text="Investments are password-protected", bg=BG, fg=TEXT_DIM, font=FONT_H3).pack()
        styled_button(self.lock_frame, "Unlock Investments", self._unlock, color=ACCENT).pack(pady=24)

        self.main_frame = tk.Frame(self, bg=BG)

        top = tk.Frame(self.main_frame, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        tk.Label(top, text="📈 Investment Records", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        styled_button(top, "+ Add Investment", self._add).pack(side="right")

        self.total_lbl = tk.Label(self.main_frame, text="", bg=BG, fg=ACCENT2, font=FONT_H3)
        self.total_lbl.pack(anchor="e", padx=30)

        cols = ("Date", "Type", "Name", "Invested", "Current Value", "Return%", "Maturity", "Notes")
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        styled_button(self.main_frame, "🗑 Delete Selected", self._delete, color=DANGER, pady=6).pack(anchor="e", padx=24, pady=4)

    def _unlock(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT investment_password_hash FROM users WHERE id=?", (self.user['id'],))
        row = c.fetchone()
        conn.close()
        if not row[0]:
            pw = simpledialog.askstring("Set Password", "Set an investment password:", show="●", parent=self)
            if pw:
                conn = get_connection()
                conn.execute("UPDATE users SET investment_password_hash=? WHERE id=?", (hash_password(pw), self.user['id']))
                conn.commit(); conn.close()
                self.unlocked = True
                self._show_main()
        else:
            pw = simpledialog.askstring("Investment Password", "Enter investment password:", show="●", parent=self)
            if pw and hash_password(pw) == row[0]:
                self.unlocked = True
                self._show_main()
            elif pw:
                messagebox.showerror("Wrong Password", "Incorrect investment password.", parent=self)

    def _show_main(self):
        self.lock_frame.lower()
        self.main_frame.place(relwidth=1, relheight=1)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id,date,type,name,amount,current_value,return_rate,maturity_date,notes FROM investments WHERE user_id=? ORDER BY date DESC", (self.user['id'],))
        rows = c.fetchall()
        conn.close()
        total = 0
        for row in rows:
            cv = row[5] or row[4]
            self.tree.insert("", "end", iid=row[0], values=(row[1],row[2],row[3],f"₹{row[4]:,.0f}",f"₹{cv:,.0f}",f"{row[6] or 0:.1f}%",row[7] or "—",row[8] or ""))
            total += row[4]
        self.total_lbl.config(text=f"Total Invested: ₹{total:,.2f}")

    def _add(self):
        AddInvestmentWindow(self, self.user, self.refresh)

    def _delete(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select", "Select a row to delete."); return
        if messagebox.askyesno("Confirm", "Delete selected investment?"):
            conn = get_connection()
            conn.execute("DELETE FROM investments WHERE id=?", (sel[0],))
            conn.commit(); conn.close()
            self.refresh()

class AddInvestmentWindow(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.title("Add Investment")
        self.geometry("440x560")
        self.configure(bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="Add Investment", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(20,12))
        form = tk.Frame(self, bg=BG)
        form.pack(padx=30, fill="x")

        fields = [("DATE", False, date.today().isoformat()), ("NAME", False, ""), ("MATURITY DATE (optional)", False, ""), ("NOTES", False, "")]
        self.entries = {}
        for label, _, default in fields:
            tk.Label(form, text=label, bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
            e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
            e.insert(0, default)
            e.pack(fill="x", pady=(2,10))
            self.entries[label] = e

        tk.Label(form, text="TYPE", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.type_var = tk.StringVar(value=INVESTMENT_TYPES[0])
        ttk.Combobox(form, textvariable=self.type_var, values=INVESTMENT_TYPES, font=FONT_BODY, state="readonly").pack(fill="x", pady=(2,10))

        for lbl in ["AMOUNT INVESTED (₹)", "CURRENT VALUE (₹)", "RETURN RATE (%)"]:
            tk.Label(form, text=lbl, bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
            e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
            e.pack(fill="x", pady=(2,10))
            self.entries[lbl] = e

        styled_button(self, "💾  Save", self._save, color=ACCENT2).pack(pady=8)

    def _save(self):
        try:
            amt = float(self.entries["AMOUNT INVESTED (₹)"].get())
            cv_str = self.entries["CURRENT VALUE (₹)"].get().strip()
            cv = float(cv_str) if cv_str else amt
            rr_str = self.entries["RETURN RATE (%)"].get().strip()
            rr = float(rr_str) if rr_str else 0
        except:
            messagebox.showerror("Error", "Enter valid numbers.", parent=self); return

        conn = get_connection()
        conn.execute("INSERT INTO investments (user_id,date,type,name,amount,current_value,return_rate,maturity_date,notes) VALUES (?,?,?,?,?,?,?,?,?)",
                     (self.user['id'], self.entries["DATE"].get(), self.type_var.get(),
                      self.entries["NAME"].get(), amt, cv, rr,
                      self.entries["MATURITY DATE (optional)"].get(),
                      self.entries["NOTES"].get()))
        conn.commit(); conn.close()
        self.on_save()
        self.destroy()

# ─── ASSET PAGE ───────────────────────────────────────────────────────────────

class AssetPage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        tk.Label(top, text="🏦 Assets", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        styled_button(top, "+ Add Asset", self._add).pack(side="right")

        cols = ("Name", "Type", "Purchase Date", "Purchase Value", "Current Value", "Location", "Notes")
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.total_lbl = tk.Label(self, text="", bg=BG, fg=ACCENT2, font=FONT_H3)
        self.total_lbl.pack(anchor="e", padx=30, pady=4)
        styled_button(self, "🗑 Delete Selected", self._delete, color=DANGER, pady=6).pack(anchor="e", padx=24)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id,name,type,purchase_date,purchase_value,current_value,location,notes FROM assets WHERE user_id=? ORDER BY created_at DESC", (self.user['id'],))
        rows = c.fetchall()
        conn.close()
        total = 0
        for row in rows:
            self.tree.insert("", "end", iid=row[0], values=(row[1],row[2],row[3] or "",f"₹{row[4] or 0:,.0f}",f"₹{row[5] or 0:,.0f}",row[6] or "",row[7] or ""))
            total += row[5] or 0
        self.total_lbl.config(text=f"Total Asset Value: ₹{total:,.2f}")

    def _add(self):
        AddAssetWindow(self, self.user, self.refresh)

    def _delete(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete selected asset?"):
            conn = get_connection()
            conn.execute("DELETE FROM assets WHERE id=?", (sel[0],))
            conn.commit(); conn.close()
            self.refresh()

class AddAssetWindow(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.title("Add Asset")
        self.geometry("420x520")
        self.configure(bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="Add Asset", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(20,12))
        form = tk.Frame(self, bg=BG)
        form.pack(padx=30, fill="x")

        tk.Label(form, text="ASSET TYPE", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.type_var = tk.StringVar(value=ASSET_TYPES[0])
        ttk.Combobox(form, textvariable=self.type_var, values=ASSET_TYPES, font=FONT_BODY, state="readonly").pack(fill="x", pady=(2,10))

        fields = ["NAME", "PURCHASE DATE", "PURCHASE VALUE (₹)", "CURRENT VALUE (₹)", "LOCATION", "NOTES"]
        self.entries = {}
        for f in fields:
            tk.Label(form, text=f, bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
            e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
            e.pack(fill="x", pady=(2,8))
            self.entries[f] = e

        styled_button(self, "💾  Save", self._save, color=ACCENT2).pack(pady=10)

    def _save(self):
        name = self.entries["NAME"].get().strip()
        if not name: messagebox.showerror("Error", "Name is required.", parent=self); return
        try:
            pv = float(self.entries["PURCHASE VALUE (₹)"].get() or 0)
            cv = float(self.entries["CURRENT VALUE (₹)"].get() or 0)
        except:
            messagebox.showerror("Error", "Enter valid values.", parent=self); return
        conn = get_connection()
        conn.execute("INSERT INTO assets (user_id,name,type,purchase_date,purchase_value,current_value,location,notes) VALUES (?,?,?,?,?,?,?,?)",
                     (self.user['id'], name, self.type_var.get(), self.entries["PURCHASE DATE"].get(),
                      pv, cv, self.entries["LOCATION"].get(), self.entries["NOTES"].get()))
        conn.commit(); conn.close()
        self.on_save()
        self.destroy()

# ─── LENDING PAGE ─────────────────────────────────────────────────────────────

class LendingPage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        tk.Label(top, text="🤝 Money Lending Records", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        styled_button(top, "+ Add Record", self._add).pack(side="right")

        # Status filter
        fb = tk.Frame(self, bg=BG2)
        fb.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(fb, text="Status:", bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(side="left", padx=12, pady=8)
        self.status_var = tk.StringVar(value="All")
        for s in ["All", "Pending", "Returned", "Partial"]:
            tk.Radiobutton(fb, text=s, variable=self.status_var, value=s,
                           bg=BG2, fg=TEXT, selectcolor=BG3, activebackground=BG2,
                           font=FONT_SM, command=self.refresh).pack(side="left", padx=8)

        self.summary_lbl = tk.Label(fb, text="", bg=BG2, fg=DANGER, font=FONT_H3)
        self.summary_lbl.pack(side="right", padx=16)

        cols = ("Date", "Borrower", "Contact", "Amount", "Due Date", "Interest%", "Status", "Notes")
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.tag_configure("pending", foreground=WARNING)
        self.tree.tag_configure("returned", foreground=ACCENT2)
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        btnf = tk.Frame(self, bg=BG)
        btnf.pack(anchor="e", padx=24, pady=8)
        styled_button(btnf, "✅ Mark Returned", self._mark_returned, color=ACCENT2, pady=6).pack(side="left", padx=4)
        styled_button(btnf, "🗑 Delete", self._delete, color=DANGER, pady=6).pack(side="left", padx=4)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_connection()
        c = conn.cursor()
        status = self.status_var.get()
        if status == "All":
            c.execute("SELECT id,date,borrower_name,contact,amount,due_date,interest_rate,status,notes FROM lending WHERE user_id=? ORDER BY date DESC", (self.user['id'],))
        else:
            c.execute("SELECT id,date,borrower_name,contact,amount,due_date,interest_rate,status,notes FROM lending WHERE user_id=? AND status=? ORDER BY date DESC", (self.user['id'], status))
        rows = c.fetchall()
        conn.close()
        total_pending = 0
        for row in rows:
            tag = "pending" if row[7] == "Pending" else "returned" if row[7] == "Returned" else ""
            self.tree.insert("", "end", iid=row[0], tags=(tag,),
                             values=(row[1],row[2],row[3] or "",f"₹{row[4]:,.0f}",row[5] or "—",f"{row[6]:.1f}%",row[7],row[8] or ""))
            if row[7] == "Pending": total_pending += row[4]
        self.summary_lbl.config(text=f"Pending: ₹{total_pending:,.0f}")

    def _add(self):
        AddLendingWindow(self, self.user, self.refresh)

    def _mark_returned(self):
        sel = self.tree.selection()
        if not sel: return
        conn = get_connection()
        conn.execute("UPDATE lending SET status='Returned' WHERE id=?", (sel[0],))
        conn.commit(); conn.close()
        self.refresh()

    def _delete(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete selected record?"):
            conn = get_connection()
            conn.execute("DELETE FROM lending WHERE id=?", (sel[0],))
            conn.commit(); conn.close()
            self.refresh()

class AddLendingWindow(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.title("Add Lending Record")
        self.geometry("420x500")
        self.configure(bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="Money Lending Record", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(20,12))
        form = tk.Frame(self, bg=BG)
        form.pack(padx=30, fill="x")

        fields = ["DATE", "BORROWER NAME", "CONTACT", "AMOUNT (₹)", "DUE DATE (optional)", "INTEREST RATE (%) optional", "NOTES"]
        self.entries = {}
        defaults = {"DATE": date.today().isoformat()}
        for f in fields:
            tk.Label(form, text=f, bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
            e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
            if f in defaults: e.insert(0, defaults[f])
            e.pack(fill="x", pady=(2,8))
            self.entries[f] = e

        styled_button(self, "💾  Save", self._save, color=ACCENT2).pack(pady=10)

    def _save(self):
        name = self.entries["BORROWER NAME"].get().strip()
        if not name: messagebox.showerror("Error", "Borrower name required.", parent=self); return
        try:
            amt = float(self.entries["AMOUNT (₹)"].get())
            ir_str = self.entries["INTEREST RATE (%) optional"].get().strip()
            ir = float(ir_str) if ir_str else 0
        except:
            messagebox.showerror("Error", "Enter valid amount.", parent=self); return
        conn = get_connection()
        conn.execute("INSERT INTO lending (user_id,date,borrower_name,contact,amount,due_date,interest_rate,notes) VALUES (?,?,?,?,?,?,?,?)",
                     (self.user['id'], self.entries["DATE"].get(), name,
                      self.entries["CONTACT"].get(), amt,
                      self.entries["DUE DATE (optional)"].get() or None, ir,
                      self.entries["NOTES"].get()))
        conn.commit(); conn.close()
        self.on_save()
        self.destroy()

# ─── NOMINEE PAGE ─────────────────────────────────────────────────────────────

class NomineePage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self.unlocked = False
        self._build()

    def _build(self):
        self.lock_frame = tk.Frame(self, bg=BG)
        self.lock_frame.place(relwidth=1, relheight=1)
        tk.Label(self.lock_frame, text="🛡️", bg=BG, font=("Arial", 64)).pack(pady=(100,8))
        tk.Label(self.lock_frame, text="Nominee Info — Passkey Protected", bg=BG, fg=TEXT_DIM, font=FONT_H3).pack()
        tk.Label(self.lock_frame, text="Only you and your nominee can access this.", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(pady=4)
        styled_button(self.lock_frame, "Enter Passkey", self._unlock, color=ACCENT).pack(pady=24)

        self.main_frame = tk.Frame(self, bg=BG)
        top = tk.Frame(self.main_frame, bg=BG)
        top.pack(fill="x", padx=30, pady=(24,8))
        tk.Label(top, text="👤 Nominee Details", bg=BG, fg=TEXT, font=FONT_H2).pack(side="left")
        styled_button(top, "+ Add Nominee", self._add).pack(side="right")

        cols = ("Name", "Relation", "Contact", "ID Type", "ID Number", "Notes")
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        styled_button(self.main_frame, "🗑 Delete Selected", self._delete, color=DANGER, pady=6).pack(anchor="e", padx=24, pady=8)

    def _unlock(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT nominee_passkey_hash FROM users WHERE id=?", (self.user['id'],))
        row = c.fetchone()
        conn.close()
        if not row[0]:
            pw = simpledialog.askstring("Set Nominee Passkey", "Create a passkey for nominee access:", show="●", parent=self)
            if pw:
                conn = get_connection()
                conn.execute("UPDATE users SET nominee_passkey_hash=? WHERE id=?", (hash_password(pw), self.user['id']))
                conn.commit(); conn.close()
                self.unlocked = True
                self._show_main()
        else:
            pw = simpledialog.askstring("Nominee Passkey", "Enter nominee passkey:", show="●", parent=self)
            if pw and hash_password(pw) == row[0]:
                self.unlocked = True
                self._show_main()
            elif pw:
                messagebox.showerror("Wrong Passkey", "Incorrect passkey.", parent=self)

    def _show_main(self):
        self.lock_frame.lower()
        self.main_frame.place(relwidth=1, relheight=1)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id,name,relation,contact,id_type,id_number,notes FROM nominees WHERE user_id=?", (self.user['id'],))
        for row in c.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row[1:])
        conn.close()

    def _add(self):
        AddNomineeWindow(self, self.user, self.refresh)

    def _delete(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete nominee?"):
            conn = get_connection()
            conn.execute("DELETE FROM nominees WHERE id=?", (sel[0],))
            conn.commit(); conn.close()
            self.refresh()

class AddNomineeWindow(tk.Toplevel):
    def __init__(self, parent, user, on_save):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.title("Add Nominee")
        self.geometry("420x460")
        self.configure(bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="Add Nominee", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(20,12))
        form = tk.Frame(self, bg=BG)
        form.pack(padx=30, fill="x")

        id_types = ["Aadhaar Card", "PAN Card", "Passport", "Voter ID", "Driving License", "Other"]
        tk.Label(form, text="FULL NAME", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.name_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.name_e.pack(fill="x", pady=(2,10))

        tk.Label(form, text="RELATION", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.rel_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.rel_e.pack(fill="x", pady=(2,10))

        tk.Label(form, text="CONTACT", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.cont_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.cont_e.pack(fill="x", pady=(2,10))

        tk.Label(form, text="ID TYPE", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.idtype_var = tk.StringVar(value=id_types[0])
        ttk.Combobox(form, textvariable=self.idtype_var, values=id_types, font=FONT_BODY, state="readonly").pack(fill="x", pady=(2,10))

        tk.Label(form, text="ID NUMBER", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.idnum_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.idnum_e.pack(fill="x", pady=(2,10))

        tk.Label(form, text="NOTES", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.notes_e = tk.Entry(form, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6)
        self.notes_e.pack(fill="x", pady=(2,12))

        styled_button(self, "💾  Save Nominee", self._save, color=ACCENT2).pack(pady=8)

    def _save(self):
        name = self.name_e.get().strip()
        if not name: messagebox.showerror("Error", "Name required.", parent=self); return
        conn = get_connection()
        conn.execute("INSERT INTO nominees (user_id,name,relation,contact,id_type,id_number,notes) VALUES (?,?,?,?,?,?,?)",
                     (self.user['id'], name, self.rel_e.get(), self.cont_e.get(),
                      self.idtype_var.get(), self.idnum_e.get(), self.notes_e.get()))
        conn.commit(); conn.close()
        self.on_save()
        self.destroy()

# ─── RECORDS PAGE ─────────────────────────────────────────────────────────────

class RecordsPage(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        tk.Label(self, text="📋 All Records & History", bg=BG, fg=TEXT, font=FONT_H2).pack(padx=30, pady=(24,4), anchor="w")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=8)

        self.exp_tab = tk.Frame(nb, bg=BG)
        self.inv_tab = tk.Frame(nb, bg=BG)
        self.asset_tab = tk.Frame(nb, bg=BG)
        self.lend_tab = tk.Frame(nb, bg=BG)

        nb.add(self.exp_tab, text="💸 Expenses")
        nb.add(self.inv_tab, text="📈 Investments")
        nb.add(self.asset_tab, text="🏦 Assets")
        nb.add(self.lend_tab, text="🤝 Lending")

        self.refresh()

    def refresh(self):
        self._load_expenses()
        self._load_investments()
        self._load_assets()
        self._load_lending()

    def _make_tree(self, parent, cols, widths=None):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            w = (widths or {}).get(col, 110)
            tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        return tree

    def _load_expenses(self):
        for w in self.exp_tab.winfo_children(): w.destroy()
        tree = self._make_tree(self.exp_tab, ("Date","Category","Sub-Cat","Amount","Payment","Description"))
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT date,category,sub_category,amount,payment_mode,description FROM expenses WHERE user_id=? ORDER BY date DESC", (self.user['id'],))
        for row in c.fetchall():
            tree.insert("", "end", values=(row[0],row[1],row[2] or "",f"₹{row[3]:,.2f}",row[4] or "",row[5] or ""))
        conn.close()

    def _load_investments(self):
        for w in self.inv_tab.winfo_children(): w.destroy()
        tree = self._make_tree(self.inv_tab, ("Date","Type","Name","Invested","Current","Return%","Maturity"))
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT date,type,name,amount,current_value,return_rate,maturity_date FROM investments WHERE user_id=? ORDER BY date DESC", (self.user['id'],))
        for row in c.fetchall():
            tree.insert("", "end", values=(row[0],row[1],row[2],f"₹{row[3]:,.0f}",f"₹{row[4] or 0:,.0f}",f"{row[5] or 0:.1f}%",row[6] or ""))
        conn.close()

    def _load_assets(self):
        for w in self.asset_tab.winfo_children(): w.destroy()
        tree = self._make_tree(self.asset_tab, ("Name","Type","Purchase Date","Purchase Value","Current Value","Location"))
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name,type,purchase_date,purchase_value,current_value,location FROM assets WHERE user_id=? ORDER BY created_at DESC", (self.user['id'],))
        for row in c.fetchall():
            tree.insert("", "end", values=(row[0],row[1],row[2] or "",f"₹{row[3] or 0:,.0f}",f"₹{row[4] or 0:,.0f}",row[5] or ""))
        conn.close()

    def _load_lending(self):
        for w in self.lend_tab.winfo_children(): w.destroy()
        tree = self._make_tree(self.lend_tab, ("Date","Borrower","Contact","Amount","Due Date","Interest%","Status"))
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT date,borrower_name,contact,amount,due_date,interest_rate,status FROM lending WHERE user_id=? ORDER BY date DESC", (self.user['id'],))
        for row in c.fetchall():
            tree.insert("", "end", values=(row[0],row[1],row[2] or "",f"₹{row[3]:,.0f}",row[4] or "—",f"{row[5]:.1f}%",row[6]))
        conn.close()

# ─── SETTINGS WINDOW ──────────────────────────────────────────────────────────

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.title("Settings")
        self.geometry("400x480")
        self.configure(bg=BG)
        self._build()

    def _build(self):
        tk.Label(self, text="⚙ Settings", bg=BG, fg=ACCENT, font=FONT_H2).pack(pady=(24,16))

        card = card_frame(self)
        card.pack(padx=30, fill="x", pady=8)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(padx=20, pady=20, fill="x")

        tk.Label(inner, text="CHANGE PASSWORD", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.old_pw = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, show="●")
        self.old_pw.pack(fill="x", pady=(2,8))
        self.new_pw = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, show="●")
        self.new_pw.pack(fill="x", pady=(2,8))
        tk.Label(inner, text="(new password)", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        styled_button(inner, "Update Password", self._change_password, color=ACCENT, pady=6).pack(fill="x", pady=8)

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=8)
        tk.Label(inner, text="RESET INVESTMENT PASSWORD", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.inv_pw = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, show="●")
        self.inv_pw.pack(fill="x", pady=(2,8))
        styled_button(inner, "Set Investment Password", self._set_inv_pw, color=WARNING, pady=6).pack(fill="x", pady=4)

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=8)
        tk.Label(inner, text="RESET NOMINEE PASSKEY", bg=CARD, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w")
        self.nom_pw = tk.Entry(inner, font=FONT_BODY, bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, show="●")
        self.nom_pw.pack(fill="x", pady=(2,8))
        styled_button(inner, "Set Nominee Passkey", self._set_nom_pw, color=WARNING, pady=6).pack(fill="x", pady=4)

    def _change_password(self):
        old = self.old_pw.get()
        new = self.new_pw.get()
        if not old or not new: messagebox.showerror("Error", "Fill both fields.", parent=self); return
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE id=? AND password_hash=?", (self.user['id'], hash_password(old)))
        if not c.fetchone():
            conn.close(); messagebox.showerror("Error", "Old password incorrect.", parent=self); return
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new), self.user['id']))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Password updated!", parent=self)

    def _set_inv_pw(self):
        pw = self.inv_pw.get()
        if not pw: return
        conn = get_connection()
        conn.execute("UPDATE users SET investment_password_hash=? WHERE id=?", (hash_password(pw), self.user['id']))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Investment password set!", parent=self)

    def _set_nom_pw(self):
        pw = self.nom_pw.get()
        if not pw: return
        conn = get_connection()
        conn.execute("UPDATE users SET nominee_passkey_hash=? WHERE id=?", (hash_password(pw), self.user['id']))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Nominee passkey set!", parent=self)

# ─── LAUNCH ───────────────────────────────────────────────────────────────────

def launch():
    init_db()
    auth = AuthWindow()
    auth.mainloop()
    if auth.logged_in_user:
        app = MainApp(auth.logged_in_user)
        app.mainloop()

if __name__ == "__main__":
    launch()
