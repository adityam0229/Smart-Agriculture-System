
# ================================================================
# SMART AGRICULTURE ASSISTANT
# Complete Python + MySQL + Tkinter Project
# No API required
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector
from mysql.connector import Error
import math

# Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Machine Learning
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


# ================================================================
# MYSQL CONFIGURATION
# ================================================================

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""       # <-- PUT YOUR MYSQL PASSWORD HERE
DATABASE = "smart_agriculture"


# ================================================================
# COLORS
# ================================================================

BG = "#F4F7F6"
SIDEBAR = "#1B5E20"
SIDEBAR_DARK = "#124116"
GREEN = "#2E7D32"
LIGHT_GREEN = "#E8F5E9"
WHITE = "#FFFFFF"
TEXT = "#263238"
GRAY = "#607D8B"
RED = "#C62828"
ORANGE = "#EF6C00"
BLUE = "#1565C0"


# ================================================================
# DATABASE SETUP
# ================================================================

def create_database():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )

        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE}"
        )

        cursor.close()
        conn.close()

    except Error as e:
        messagebox.showerror(
            "MySQL Error",
            "Could not create database.\n\n"
            + str(e)
        )
        return False

    return True


def get_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE
    )


def setup_tables():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # FARMERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(30),
            village VARCHAR(100),
            district VARCHAR(100),
            created_at DATE
        )
        """)

        # FARMS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS farms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
            land_area DECIMAL(10,2),
            soil_type VARCHAR(50),
            irrigation_type VARCHAR(50),
            location VARCHAR(150),
            current_crop VARCHAR(100),
            FOREIGN KEY (farmer_id)
            REFERENCES farmers(id)
            ON DELETE CASCADE
        )
        """)

        # RECOMMENDATIONS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
            nitrogen DECIMAL(10,2),
            phosphorus DECIMAL(10,2),
            potassium DECIMAL(10,2),
            temperature DECIMAL(10,2),
            humidity DECIMAL(10,2),
            rainfall DECIMAL(10,2),
            ph DECIMAL(10,2),
            recommended_crop VARCHAR(100),
            created_at DATE,
            FOREIGN KEY (farmer_id)
            REFERENCES farmers(id)
            ON DELETE CASCADE
        )
        """)

        # IRRIGATION
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS irrigation (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
            crop VARCHAR(100),
            moisture DECIMAL(10,2),
            recommendation VARCHAR(255),
            created_at DATE,
            FOREIGN KEY (farmer_id)
            REFERENCES farmers(id)
            ON DELETE CASCADE
        )
        """)

        # EXPENSES
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
            category VARCHAR(100),
            amount DECIMAL(12,2),
            description VARCHAR(255),
            expense_date DATE,
            FOREIGN KEY (farmer_id)
            REFERENCES farmers(id)
            ON DELETE CASCADE
        )
        """)

        # REVENUE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
            amount DECIMAL(12,2),
            description VARCHAR(255),
            revenue_date DATE,
            FOREIGN KEY (farmer_id)
            REFERENCES farmers(id)
            ON DELETE CASCADE
        )
        """)

        conn.commit()

        cursor.close()
        conn.close()

    except Error as e:
        messagebox.showerror("Database Error", str(e))
        return False

    return True


# ================================================================
# MACHINE LEARNING DATA
# ================================================================

# Sample agricultural dataset.
# This is intentionally kept inside the program so that no
# internet or API is required.

CROP_DATA = [

    # Rice
    [90, 42, 43, 20.9, 82, 202, 6.5, "Rice"],
    [85, 40, 40, 22.0, 80, 220, 6.4, "Rice"],
    [95, 45, 45, 24.0, 85, 210, 6.7, "Rice"],
    [80, 38, 42, 21.5, 78, 190, 6.3, "Rice"],

    # Maize
    [70, 35, 40, 24.5, 65, 85, 6.5, "Maize"],
    [75, 38, 42, 25.5, 68, 90, 6.7, "Maize"],
    [65, 32, 38, 23.5, 60, 80, 6.2, "Maize"],
    [72, 36, 39, 26.0, 70, 95, 6.6, "Maize"],

    # Wheat
    [70, 45, 40, 18.5, 60, 75, 6.5, "Wheat"],
    [68, 43, 38, 20.0, 58, 70, 6.7, "Wheat"],
    [75, 48, 42, 17.5, 62, 80, 6.4, "Wheat"],
    [65, 40, 36, 19.0, 55, 65, 6.3, "Wheat"],

    # Cotton
    [120, 50, 45, 27.0, 65, 75, 6.8, "Cotton"],
    [115, 48, 43, 28.0, 70, 80, 7.0, "Cotton"],
    [125, 52, 48, 29.0, 68, 85, 6.9, "Cotton"],
    [110, 45, 42, 26.0, 62, 70, 6.7, "Cotton"],

    # Potato
    [60, 55, 50, 19.0, 70, 110, 5.8, "Potato"],
    [65, 58, 52, 18.0, 72, 115, 5.9, "Potato"],
    [55, 52, 48, 20.0, 68, 105, 5.7, "Potato"],
    [62, 54, 51, 21.0, 75, 120, 6.0, "Potato"],

    # Tomato
    [55, 45, 50, 23.0, 70, 100, 6.2, "Tomato"],
    [60, 48, 52, 24.0, 72, 105, 6.4, "Tomato"],
    [50, 42, 48, 22.0, 68, 95, 6.1, "Tomato"],
    [58, 46, 51, 25.0, 75, 110, 6.3, "Tomato"],

    # Chickpea
    [40, 60, 75, 20.0, 55, 65, 6.5, "Chickpea"],
    [42, 62, 78, 21.0, 58, 70, 6.7, "Chickpea"],
    [38, 58, 72, 19.0, 52, 60, 6.3, "Chickpea"],
    [45, 65, 80, 22.0, 60, 75, 6.6, "Chickpea"],

    # Sugarcane
    [100, 45, 50, 27.0, 80, 150, 6.8, "Sugarcane"],
    [105, 48, 52, 28.0, 82, 160, 7.0, "Sugarcane"],
    [95, 42, 48, 26.0, 78, 145, 6.7, "Sugarcane"],
    [110, 50, 55, 29.0, 85, 170, 6.9, "Sugarcane"],

    # Groundnut
    [35, 50, 45, 25.0, 65, 90, 6.4, "Groundnut"],
    [38, 52, 47, 26.0, 68, 95, 6.5, "Groundnut"],
    [32, 48, 42, 24.0, 62, 85, 6.3, "Groundnut"],
    [40, 55, 50, 27.0, 70, 100, 6.6, "Groundnut"],
]


def train_crop_model():

    X = []
    y = []

    for row in CROP_DATA:
        X.append(row[:7])
        y.append(row[7])

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )

    model.fit(X, y)

    return model


crop_model = train_crop_model()


# ================================================================
# MAIN APPLICATION
# ================================================================

class AgricultureApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Smart Agriculture Assistant")
        self.root.geometry("1250x750")
        self.root.minsize(1050, 650)
        self.root.configure(bg=BG)

        self.current_page = None

        self.build_layout()
        self.show_dashboard()

    # ============================================================
    # LAYOUT
    # ============================================================

    def build_layout(self):

        # SIDEBAR
        self.sidebar = tk.Frame(
            self.root,
            bg=SIDEBAR,
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        title = tk.Label(
            self.sidebar,
            text="🌱 Smart\nAgriculture",
            font=("Arial", 21, "bold"),
            fg=WHITE,
            bg=SIDEBAR,
            pady=25
        )
        title.pack()

        subtitle = tk.Label(
            self.sidebar,
            text="FARM MANAGEMENT SYSTEM",
            font=("Arial", 8, "bold"),
            fg="#C8E6C9",
            bg=SIDEBAR
        )
        subtitle.pack(pady=(0, 20))

        self.create_menu_button(
            "🏠  Dashboard",
            self.show_dashboard
        )

        self.create_menu_button(
            "👨‍🌾  Farmers",
            self.show_farmers
        )

        self.create_menu_button(
            "🏞️  Farms",
            self.show_farms
        )

        self.create_menu_button(
            "🌾  Crop Recommendation",
            self.show_crop_recommendation
        )

        self.create_menu_button(
            "💧  Irrigation",
            self.show_irrigation
        )

        self.create_menu_button(
            "🌿  Crop Health",
            self.show_crop_health
        )

        self.create_menu_button(
            "📅  Farming Calendar",
            self.show_calendar
        )

        self.create_menu_button(
            "💰  Expenses",
            self.show_expenses
        )

        self.create_menu_button(
            "📊  Reports",
            self.show_reports
        )

        bottom = tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        )
        bottom.pack(side="bottom", pady=15)

        tk.Label(
            bottom,
            text="Python + MySQL\nOffline ML System",
            font=("Arial", 9),
            fg="#C8E6C9",
            bg=SIDEBAR
        ).pack()

        # MAIN AREA
        self.main = tk.Frame(
            self.root,
            bg=BG
        )
        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

    def create_menu_button(self, text, command):

        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            anchor="w",
            padx=22,
            pady=11,
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=SIDEBAR,
            activebackground=SIDEBAR_DARK,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        btn.pack(fill="x", padx=8, pady=2)

    # ============================================================
    # COMMON FUNCTIONS
    # ============================================================

    def clear_main(self):

        for widget in self.main.winfo_children():
            widget.destroy()

    def page_title(self, title, description=""):

        top = tk.Frame(
            self.main,
            bg=BG
        )
        top.pack(fill="x", padx=30, pady=(25, 15))

        tk.Label(
            top,
            text=title,
            font=("Arial", 24, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        if description:
            tk.Label(
                top,
                text=description,
                font=("Arial", 10),
                fg=GRAY,
                bg=BG
            ).pack(anchor="w", pady=(5, 0))

    def card(self, parent):

        frame = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground="#DDE5DF",
            highlightthickness=1
        )

        return frame

    def entry(self, parent, width=25):

        return tk.Entry(
            parent,
            width=width,
            font=("Arial", 10),
            relief="solid",
            bd=1
        )

    def styled_button(
        self,
        parent,
        text,
        command,
        bg=GREEN
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg=bg,
            fg=WHITE,
            activebackground=bg,
            activeforeground=WHITE,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )

    def get_farmer_list(self):

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name FROM farmers ORDER BY name"
            )

            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            return rows

        except Error:
            return []

    # ============================================================
    # DASHBOARD
    # ============================================================

    def show_dashboard(self):

        self.clear_main()

        self.page_title(
            "Dashboard",
            "Smart Agriculture Assistant — Farm overview"
        )

        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", padx=30)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM farmers")
            farmers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM farms")
            farms = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COALESCE(SUM(land_area),0) FROM farms"
            )
            land = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COALESCE(SUM(amount),0) FROM expenses"
            )
            expenses = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COALESCE(SUM(amount),0) FROM revenue"
            )
            revenue = cursor.fetchone()[0]

            cursor.close()
            conn.close()

        except Error:
            farmers = farms = land = expenses = revenue = 0

        self.stat_card(
            stats,
            "👨‍🌾",
            "Farmers",
            str(farmers)
        )

        self.stat_card(
            stats,
            "🏞️",
            "Farms",
            str(farms)
        )

        self.stat_card(
            stats,
            "🌱",
            "Total Land",
            f"{land} acres"
        )

        self.stat_card(
            stats,
            "💰",
            "Expenses",
            f"₹{expenses:,.2f}"
        )

        self.stat_card(
            stats,
            "📈",
            "Revenue",
            f"₹{revenue:,.2f}"
        )

        lower = tk.Frame(self.main, bg=BG)
        lower.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # Expense chart
        chart_card = self.card(lower)
        chart_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            chart_card,
            text="Expense by Category",
            font=("Arial", 14, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=20, pady=15)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT category, SUM(amount)
                FROM expenses
                GROUP BY category
            """)

            data = cursor.fetchall()

            cursor.close()
            conn.close()

            if data:

                fig = Figure(
                    figsize=(5, 3.2),
                    dpi=90
                )

                ax = fig.add_subplot(111)

                categories = [x[0] for x in data]
                amounts = [float(x[1]) for x in data]

                ax.bar(categories, amounts)
                ax.set_ylabel("Amount (₹)")
                ax.tick_params(axis="x", rotation=25)

                fig.tight_layout()

                canvas = FigureCanvasTkAgg(
                    fig,
                    master=chart_card
                )

                canvas.draw()
                canvas.get_tk_widget().pack(
                    fill="both",
                    expand=True,
                    padx=10,
                    pady=5
                )

            else:
                tk.Label(
                    chart_card,
                    text="No expense data available yet.",
                    font=("Arial", 11),
                    fg=GRAY,
                    bg=WHITE
                ).pack(pady=80)

        except Error:
            pass

        # Quick actions
        quick = self.card(lower)
        quick.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        tk.Label(
            quick,
            text="Quick Actions",
            font=("Arial", 14, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=20, pady=15)

        actions = [
            ("👨‍🌾 Add Farmer", self.show_farmers),
            ("🏞️ Add Farm", self.show_farms),
            ("🌾 Crop Recommendation",
             self.show_crop_recommendation),
            ("💧 Check Irrigation", self.show_irrigation),
            ("💰 Add Expense", self.show_expenses),
        ]

        for text, command in actions:

            self.styled_button(
                quick,
                text,
                command
            ).pack(
                fill="x",
                padx=25,
                pady=7
            )

    def stat_card(self, parent, icon, title, value):

        frame = self.card(parent)

        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            frame,
            text=icon,
            font=("Arial", 25),
            bg=WHITE
        ).pack(pady=(15, 3))

        tk.Label(
            frame,
            text=value,
            font=("Arial", 17, "bold"),
            fg=GREEN,
            bg=WHITE
        ).pack()

        tk.Label(
            frame,
            text=title,
            font=("Arial", 9),
            fg=GRAY,
            bg=WHITE
        ).pack(pady=(3, 15))

    # ============================================================
    # FARMERS
    # ============================================================

    def show_farmers(self):

        self.clear_main()

        self.page_title(
            "Farmer Management",
            "Add and manage farmer information"
        )

        form = self.card(self.main)
        form.pack(fill="x", padx=30, pady=5)

        fields = [
            ("Name", 0),
            ("Phone", 1),
            ("Village", 2),
            ("District", 3)
        ]

        entries = {}

        for label, row in fields:

            tk.Label(
                form,
                text=label,
                bg=WHITE,
                fg=TEXT,
                font=("Arial", 10, "bold")
            ).grid(
                row=row,
                column=0,
                padx=20,
                pady=8,
                sticky="w"
            )

            e = self.entry(form, 35)
            e.grid(
                row=row,
                column=1,
                padx=10,
                pady=8,
                sticky="w"
            )

            entries[label] = e

        def add_farmer():

            name = entries["Name"].get().strip()

            if not name:
                messagebox.showwarning(
                    "Validation",
                    "Farmer name is required."
                )
                return

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO farmers
                    (name, phone, village, district, created_at)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    name,
                    entries["Phone"].get(),
                    entries["Village"].get(),
                    entries["District"].get(),
                    date.today()
                ))

                conn.commit()

                cursor.close()
                conn.close()

                messagebox.showinfo(
                    "Success",
                    "Farmer added successfully."
                )

                for e in entries.values():
                    e.delete(0, tk.END)

                load_data()

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        self.styled_button(
            form,
            "➕ Add Farmer",
            add_farmer
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            padx=20
        )

        # TABLE
        table_card = self.card(self.main)
        table_card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        columns = (
            "ID",
            "Name",
            "Phone",
            "Village",
            "District",
            "Created"
        )

        tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        def load_data():

            for item in tree.get_children():
                tree.delete(item)

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, phone, village,
                           district, created_at
                    FROM farmers
                    ORDER BY id DESC
                """)

                rows = cursor.fetchall()

                cursor.close()
                conn.close()

                for row in rows:
                    tree.insert("", "end", values=row)

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        def delete_farmer():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Farmer",
                    "Please select a farmer first."
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            if not messagebox.askyesno(
                "Confirm",
                "Delete selected farmer?"
            ):
                return

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM farmers WHERE id=%s",
                    (values[0],)
                )

                conn.commit()

                cursor.close()
                conn.close()

                load_data()

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        self.styled_button(
            table_card,
            "🗑 Delete Selected",
            delete_farmer,
            RED
        ).pack(
            side="bottom",
            padx=15,
            pady=(0, 15),
            anchor="e"
        )

        load_data()

    # ============================================================
    # FARMS
    # ============================================================

    def show_farms(self):

        self.clear_main()

        self.page_title(
            "Farm Management",
            "Store farm, soil and crop information"
        )

        form = self.card(self.main)
        form.pack(
            fill="x",
            padx=30,
            pady=5
        )

        farmers = self.get_farmer_list()

        farmer_map = {
            f"{x[0]} - {x[1]}": x[0]
            for x in farmers
        }

        labels = [
            "Farmer",
            "Land Area (acres)",
            "Soil Type",
            "Irrigation Type",
            "Location",
            "Current Crop"
        ]

        widgets = {}

        for i, label in enumerate(labels):

            tk.Label(
                form,
                text=label,
                bg=WHITE,
                fg=TEXT,
                font=("Arial", 10, "bold")
            ).grid(
                row=i // 2,
                column=(i % 2) * 2,
                padx=15,
                pady=8,
                sticky="w"
            )

            if label == "Farmer":

                w = ttk.Combobox(
                    form,
                    values=list(farmer_map.keys()),
                    width=30,
                    state="readonly"
                )

            elif label == "Soil Type":

                w = ttk.Combobox(
                    form,
                    values=[
                        "Alluvial",
                        "Black",
                        "Red",
                        "Loamy",
                        "Sandy",
                        "Clay",
                        "Laterite"
                    ],
                    width=30
                )

            elif label == "Irrigation Type":

                w = ttk.Combobox(
                    form,
                    values=[
                        "Rainfed",
                        "Drip",
                        "Sprinkler",
                        "Canal",
                        "Tube Well",
                        "Other"
                    ],
                    width=30
                )

            else:
                w = self.entry(form, 33)

            w.grid(
                row=i // 2,
                column=(i % 2) * 2 + 1,
                padx=10,
                pady=8,
                sticky="w"
            )

            widgets[label] = w

        def add_farm():

            farmer_text = widgets["Farmer"].get()

            if not farmer_text:
                messagebox.showwarning(
                    "Validation",
                    "Select a farmer."
                )
                return

            try:

                farmer_id = farmer_map[farmer_text]
                land = float(
                    widgets["Land Area (acres)"].get()
                )

                if land <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showwarning(
                    "Validation",
                    "Enter a valid land area."
                )
                return

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO farms
                    (farmer_id, land_area, soil_type,
                     irrigation_type, location, current_crop)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    farmer_id,
                    land,
                    widgets["Soil Type"].get(),
                    widgets["Irrigation Type"].get(),
                    widgets["Location"].get(),
                    widgets["Current Crop"].get()
                ))

                conn.commit()

                cursor.close()
                conn.close()

                messagebox.showinfo(
                    "Success",
                    "Farm added successfully."
                )

                load_data()

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        self.styled_button(
            form,
            "➕ Add Farm",
            add_farm
        ).grid(
            row=3,
            column=1,
            padx=10,
            pady=15,
            sticky="w"
        )

        # TABLE

        table_card = self.card(self.main)
        table_card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        columns = (
            "ID",
            "Farmer",
            "Area",
            "Soil",
            "Irrigation",
            "Location",
            "Crop"
        )

        tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=115)

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        def load_data():

            for item in tree.get_children():
                tree.delete(item)

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT farms.id,
                           farmers.name,
                           farms.land_area,
                           farms.soil_type,
                           farms.irrigation_type,
                           farms.location,
                           farms.current_crop
                    FROM farms
                    JOIN farmers
                    ON farms.farmer_id = farmers.id
                    ORDER BY farms.id DESC
                """)

                rows = cursor.fetchall()

                cursor.close()
                conn.close()

                for row in rows:
                    tree.insert("", "end", values=row)

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        load_data()

    # ============================================================
    # CROP RECOMMENDATION
    # ============================================================

    def show_crop_recommendation(self):

        self.clear_main()

        self.page_title(
            "🌾 Crop Recommendation",
            "Offline machine-learning based crop recommendation"
        )

        container = tk.Frame(
            self.main,
            bg=BG
        )
        container.pack(
            fill="both",
            expand=True,
            padx=30
        )

        form = self.card(container)
        form.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        result = self.card(container)
        result.pack(
            side="left",
            fill="both",
            expand=True
        )

        farmers = self.get_farmer_list()

        farmer_map = {
            f"{x[0]} - {x[1]}": x[0]
            for x in farmers
        }

        tk.Label(
            form,
            text="Farm Information",
            font=("Arial", 15, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=20
        )

        farmer_var = tk.StringVar()

        ttk.Combobox(
            form,
            textvariable=farmer_var,
            values=list(farmer_map.keys()),
            width=30,
            state="readonly"
        ).pack(
            padx=20,
            pady=5
        )

        fields = [
            "Nitrogen (N)",
            "Phosphorus (P)",
            "Potassium (K)",
            "Temperature °C",
            "Humidity %",
            "Rainfall mm",
            "pH"
        ]

        entries = {}

        for field in fields:

            tk.Label(
                form,
                text=field,
                font=("Arial", 9, "bold"),
                fg=TEXT,
                bg=WHITE
            ).pack(
                anchor="w",
                padx=20,
                pady=(8, 2)
            )

            e = self.entry(form, 32)
            e.pack(
                padx=20,
                pady=2
            )

            entries[field] = e

        recommendation_label = tk.Label(
            result,
            text="🌱\n\nEnter farm values\nand click\n"
                 "'Recommend Crop'",
            font=("Arial", 18, "bold"),
            fg=GREEN,
            bg=WHITE,
            justify="center"
        )

        recommendation_label.pack(
            expand=True
        )

        def recommend():

            try:

                values = [
                    float(entries[x].get())
                    for x in fields
                ]

            except ValueError:

                messagebox.showwarning(
                    "Invalid Input",
                    "Please enter valid numbers in all fields."
                )
                return

            crop = crop_model.predict([values])[0]

            probabilities = crop_model.predict_proba(
                [values]
            )[0]

            confidence = max(probabilities) * 100

            recommendation_label.config(
                text=(
                    "🌾 RECOMMENDED CROP\n\n"
                    f"{crop}\n\n"
                    f"Model confidence: {confidence:.1f}%\n\n"
                    "This is a machine-learning recommendation.\n"
                    "Consider local agricultural conditions before\n"
                    "making actual farming decisions."
                ),
                fg=GREEN
            )

            # Save recommendation if farmer selected

            farmer_text = farmer_var.get()

            if farmer_text:

                try:

                    farmer_id = farmer_map[farmer_text]

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO recommendations
                        (farmer_id, nitrogen, phosphorus,
                         potassium, temperature, humidity,
                         rainfall, ph, recommended_crop,
                         created_at)
                        VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        farmer_id,
                        values[0],
                        values[1],
                        values[2],
                        values[3],
                        values[4],
                        values[5],
                        values[6],
                        crop,
                        date.today()
                    ))

                    conn.commit()

                    cursor.close()
                    conn.close()

                except Error as e:
                    messagebox.showerror(
                        "Database Error",
                        str(e)
                    )

        self.styled_button(
            form,
            "🌾 Recommend Crop",
            recommend
        ).pack(
            padx=20,
            pady=20,
            fill="x"
        )

    # ============================================================
    # IRRIGATION
    # ============================================================

    def show_irrigation(self):

        self.clear_main()

        self.page_title(
            "💧 Irrigation Assistant",
            "Evaluate soil moisture and irrigation needs"
        )

        card = self.card(self.main)
        card.pack(
            padx=30,
            pady=10,
            fill="x"
        )

        farmers = self.get_farmer_list()

        farmer_map = {
            f"{x[0]} - {x[1]}": x[0]
            for x in farmers
        }

        tk.Label(
            card,
            text="Farmer",
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=15
        )

        farmer_box = ttk.Combobox(
            card,
            values=list(farmer_map.keys()),
            width=30,
            state="readonly"
        )

        farmer_box.grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Label(
            card,
            text="Crop",
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=2,
            padx=20
        )

        crop_entry = self.entry(card, 25)
        crop_entry.grid(
            row=0,
            column=3
        )

        tk.Label(
            card,
            text="Soil Moisture %",
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 10, "bold")
        ).grid(
            row=1,
            column=0,
            padx=20,
            pady=15
        )

        moisture_entry = self.entry(card, 20)
        moisture_entry.grid(
            row=1,
            column=1
        )

        result = tk.Label(
            self.main,
            text="Enter soil moisture to get guidance.",
            font=("Arial", 17, "bold"),
            fg=GREEN,
            bg=LIGHT_GREEN,
            padx=30,
            pady=30
        )

        result.pack(
            padx=30,
            pady=20,
            fill="x"
        )

        def check():

            try:
                moisture = float(
                    moisture_entry.get()
                )

                if moisture < 0 or moisture > 100:
                    raise ValueError

            except ValueError:

                messagebox.showwarning(
                    "Invalid Input",
                    "Moisture must be between 0 and 100."
                )
                return

            if moisture < 30:
                recommendation = (
                    "Soil moisture is low. "
                    "Check irrigation requirements and "
                    "consider watering if appropriate for the crop."
                )

            elif moisture < 50:
                recommendation = (
                    "Soil moisture is moderate. "
                    "Monitor the soil and crop before irrigating."
                )

            elif moisture <= 80:
                recommendation = (
                    "Soil moisture is in a relatively adequate range. "
                    "Avoid unnecessary irrigation."
                )

            else:
                recommendation = (
                    "Soil moisture is high. "
                    "Check drainage and avoid over-irrigation."
                )

            result.config(
                text=f"💧 {recommendation}"
            )

            farmer_text = farmer_box.get()

            if farmer_text:

                try:

                    farmer_id = farmer_map[farmer_text]

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO irrigation
                        (farmer_id, crop, moisture,
                         recommendation, created_at)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (
                        farmer_id,
                        crop_entry.get(),
                        moisture,
                        recommendation,
                        date.today()
                    ))

                    conn.commit()

                    cursor.close()
                    conn.close()

                except Error as e:
                    messagebox.showerror(
                        "Database Error",
                        str(e)
                    )

        self.styled_button(
            card,
            "💧 Check",
            check
        ).grid(
            row=1,
            column=3,
            padx=15
        )

    # ============================================================
    # CROP HEALTH
    # ============================================================

    def show_crop_health(self):

        self.clear_main()

        self.page_title(
            "🌿 Crop Health Assistant",
            "General guidance based on observed symptoms"
        )

        card = self.card(self.main)
        card.pack(
            padx=30,
            pady=10,
            fill="x"
        )

        tk.Label(
            card,
            text="Select observed symptom:",
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 8)
        )

        symptom_box = ttk.Combobox(
            card,
            values=[
                "Yellow leaves",
                "Brown leaf edges",
                "White powder on leaves",
                "Dark spots on leaves",
                "Wilting",
                "Slow growth",
                "Holes in leaves",
                "Leaf curling"
            ],
            width=45,
            state="readonly"
        )

        symptom_box.pack(
            padx=20,
            pady=5,
            anchor="w"
        )

        result = tk.Label(
            card,
            text="Select a symptom.",
            font=("Arial", 12),
            bg=WHITE,
            fg=TEXT,
            justify="left",
            wraplength=850
        )

        result.pack(
            anchor="w",
            padx=20,
            pady=20
        )

        health_data = {

            "Yellow leaves":
                "Possible causes include nutrient imbalance, "
                "water stress or natural leaf aging. Check soil "
                "conditions and irrigation.",

            "Brown leaf edges":
                "Possible causes include water stress, heat stress "
                "or excess fertilizer. Check moisture and fertilizer "
                "application.",

            "White powder on leaves":
                "May be associated with fungal growth such as "
                "powdery mildew. Improve airflow and seek local "
                "agricultural guidance if it spreads.",

            "Dark spots on leaves":
                "May indicate a fungal or bacterial problem. "
                "Inspect affected leaves and avoid excessive "
                "leaf wetness.",

            "Wilting":
                "Check soil moisture, root conditions, temperature "
                "and possible pest or disease stress.",

            "Slow growth":
                "Possible factors include poor nutrients, unsuitable "
                "temperature, insufficient light or water stress.",

            "Holes in leaves":
                "Could indicate insect or other pest activity. "
                "Inspect leaves carefully for visible pests.",

            "Leaf curling":
                "Possible causes include heat, water stress, insects "
                "or disease. Inspect the underside of leaves."
        }

        def check_health():

            symptom = symptom_box.get()

            if not symptom:
                messagebox.showwarning(
                    "Select Symptom",
                    "Please select a symptom."
                )
                return

            result.config(
                text=(
                    f"🌿 Observed: {symptom}\n\n"
                    f"General guidance:\n"
                    f"{health_data[symptom]}\n\n"
                    "Note: This is not a professional plant-disease "
                    "diagnosis. For serious crop damage, consult a "
                    "qualified agricultural expert."
                )
            )

        self.styled_button(
            card,
            "🔍 Analyze Symptom",
            check_health
        ).pack(
            padx=20,
            pady=(0, 20),
            anchor="w"
        )

    # ============================================================
    # FARMING CALENDAR
    # ============================================================

    def show_calendar(self):

        self.clear_main()

        self.page_title(
            "📅 Farming Calendar",
            "General crop activity reference"
        )

        card = self.card(self.main)
        card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "Crop",
            "Sowing",
            "Growth",
            "Irrigation",
            "Fertilization",
            "Harvest"
        )

        tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings"
        )

        for col in columns:

            tree.heading(
                col,
                text=col
            )

            tree.column(
                col,
                width=150
            )

        calendar_data = [

            ("Rice",
             "June–July",
             "3–5 months",
             "Regular",
             "As required",
             "Oct–Nov"),

            ("Wheat",
             "Oct–Dec",
             "4–5 months",
             "Moderate",
             "As required",
             "Mar–Apr"),

            ("Maize",
             "Jun–Jul",
             "3–4 months",
             "Moderate",
             "As required",
             "Sep–Oct"),

            ("Cotton",
             "Apr–Jun",
             "5–7 months",
             "Moderate",
             "As required",
             "Oct–Dec"),

            ("Potato",
             "Oct–Nov",
             "3–4 months",
             "Regular",
             "As required",
             "Jan–Feb"),

            ("Tomato",
             "Season dependent",
             "3–4 months",
             "Regular",
             "As required",
             "Season dependent"),

            ("Chickpea",
             "Oct–Nov",
             "4–5 months",
             "Low–Moderate",
             "As required",
             "Feb–Mar"),

            ("Sugarcane",
             "Feb–Mar / Oct",
             "10–18 months",
             "Regular",
             "As required",
             "Season dependent"),

            ("Groundnut",
             "Jun–Jul",
             "3–5 months",
             "Moderate",
             "As required",
             "Sep–Oct")
        ]

        for row in calendar_data:
            tree.insert(
                "",
                "end",
                values=row
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        tk.Label(
            card,
            text=(
                "Note: Calendar information is general. "
                "Actual crop timing depends on region, variety, "
                "climate and local agricultural practices."
            ),
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 9)
        ).pack(
            pady=(0, 15)
        )

    # ============================================================
    # EXPENSES
    # ============================================================

    def show_expenses(self):

        self.clear_main()

        self.page_title(
            "💰 Farm Expenses & Revenue",
            "Track farm financial activity"
        )

        form = self.card(self.main)
        form.pack(
            fill="x",
            padx=30,
            pady=5
        )

        farmers = self.get_farmer_list()

        farmer_map = {
            f"{x[0]} - {x[1]}": x[0]
            for x in farmers
        }

        tk.Label(
            form,
            text="Farmer",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=12
        )

        farmer_box = ttk.Combobox(
            form,
            values=list(farmer_map.keys()),
            width=25,
            state="readonly"
        )

        farmer_box.grid(
            row=0,
            column=1
        )

        tk.Label(
            form,
            text="Type",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=2,
            padx=15
        )

        type_box = ttk.Combobox(
            form,
            values=["Expense", "Revenue"],
            width=15,
            state="readonly"
        )

        type_box.set("Expense")

        type_box.grid(
            row=0,
            column=3
        )

        tk.Label(
            form,
            text="Category",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=1,
            column=0,
            padx=15,
            pady=12
        )

        category_box = ttk.Combobox(
            form,
            values=[
                "Seeds",
                "Fertilizer",
                "Labour",
                "Irrigation",
                "Equipment",
                "Transport",
                "Pesticide",
                "Other",
                "Crop Sale",
                "Other Revenue"
            ],
            width=25
        )

        category_box.grid(
            row=1,
            column=1
        )

        tk.Label(
            form,
            text="Amount ₹",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=1,
            column=2,
            padx=15
        )

        amount_entry = self.entry(form, 18)
        amount_entry.grid(
            row=1,
            column=3
        )

        tk.Label(
            form,
            text="Description",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=12
        )

        description_entry = self.entry(form, 50)
        description_entry.grid(
            row=2,
            column=1,
            columnspan=3,
            sticky="w"
        )

        def add_transaction():

            farmer_text = farmer_box.get()

            if not farmer_text:
                messagebox.showwarning(
                    "Validation",
                    "Select a farmer."
                )
                return

            try:

                amount = float(
                    amount_entry.get()
                )

                if amount <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showwarning(
                    "Validation",
                    "Enter a valid positive amount."
                )
                return

            farmer_id = farmer_map[farmer_text]

            transaction_type = type_box.get()

            category = category_box.get()

            if not category:
                category = "Other"

            description = description_entry.get()

            try:

                conn = get_connection()
                cursor = conn.cursor()

                if transaction_type == "Expense":

                    cursor.execute("""
                        INSERT INTO expenses
                        (farmer_id, category, amount,
                         description, expense_date)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (
                        farmer_id,
                        category,
                        amount,
                        description,
                        date.today()
                    ))

                else:

                    cursor.execute("""
                        INSERT INTO revenue
                        (farmer_id, amount,
                         description, revenue_date)
                        VALUES (%s,%s,%s,%s)
                    """, (
                        farmer_id,
                        amount,
                        description,
                        date.today()
                    ))

                conn.commit()

                cursor.close()
                conn.close()

                messagebox.showinfo(
                    "Success",
                    f"{transaction_type} added successfully."
                )

                amount_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)

                load_data()

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        self.styled_button(
            form,
            "➕ Add Transaction",
            add_transaction
        ).grid(
            row=3,
            column=1,
            padx=15,
            pady=12,
            sticky="w"
        )

        # TABLE

        table_card = self.card(self.main)
        table_card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        columns = (
            "Type",
            "Farmer",
            "Category",
            "Amount",
            "Description",
            "Date"
        )

        tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        def load_data():

            for item in tree.get_children():
                tree.delete(item)

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT 'Expense',
                           farmers.name,
                           expenses.category,
                           expenses.amount,
                           expenses.description,
                           expenses.expense_date
                    FROM expenses
                    JOIN farmers
                    ON expenses.farmer_id = farmers.id

                    UNION ALL

                    SELECT 'Revenue',
                           farmers.name,
                           'Revenue',
                           revenue.amount,
                           revenue.description,
                           revenue.revenue_date
                    FROM revenue
                    JOIN farmers
                    ON revenue.farmer_id = farmers.id

                    ORDER BY 6 DESC
                """)

                rows = cursor.fetchall()

                cursor.close()
                conn.close()

                for row in rows:
                    tree.insert("", "end", values=row)

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        load_data()

    # ============================================================
    # REPORTS
    # ============================================================

    def show_reports(self):

        self.clear_main()

        self.page_title(
            "📊 Reports & Analytics",
            "View farm financial and crop information"
        )

        top = tk.Frame(
            self.main,
            bg=BG
        )
        top.pack(
            fill="x",
            padx=30
        )

        farmer_list = self.get_farmer_list()

        farmer_map = {
            f"{x[0]} - {x[1]}": x[0]
            for x in farmer_list
        }

        tk.Label(
            top,
            text="Select Farmer:",
            bg=BG,
            fg=TEXT,
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            padx=(0, 10)
        )

        farmer_box = ttk.Combobox(
            top,
            values=list(farmer_map.keys()),
            width=30,
            state="readonly"
        )

        farmer_box.pack(
            side="left"
        )

        report_frame = tk.Frame(
            self.main,
            bg=BG
        )
        report_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        summary = self.card(report_frame)
        summary.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        chart_card = self.card(report_frame)
        chart_card.pack(
            side="left",
            fill="both",
            expand=True
        )

        report_text = tk.Text(
            summary,
            width=38,
            height=25,
            font=("Arial", 10),
            bg=WHITE,
            fg=TEXT,
            relief="flat"
        )

        report_text.pack(
            padx=20,
            pady=20
        )

        def generate_report():

            farmer_text = farmer_box.get()

            if not farmer_text:
                messagebox.showwarning(
                    "Select Farmer",
                    "Please select a farmer."
                )
                return

            farmer_id = farmer_map[farmer_text]

            try:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COALESCE(SUM(amount),0)
                    FROM expenses
                    WHERE farmer_id=%s
                """, (farmer_id,))

                expenses = float(
                    cursor.fetchone()[0]
                )

                cursor.execute("""
                    SELECT COALESCE(SUM(amount),0)
                    FROM revenue
                    WHERE farmer_id=%s
                """, (farmer_id,))

                revenue = float(
                    cursor.fetchone()[0]
                )

                cursor.execute("""
                    SELECT COUNT(*),
                           COALESCE(SUM(land_area),0)
                    FROM farms
                    WHERE farmer_id=%s
                """, (farmer_id,))

                farm_count, land = cursor.fetchone()

                cursor.execute("""
                    SELECT recommended_crop
                    FROM recommendations
                    WHERE farmer_id=%s
                    ORDER BY id DESC
                    LIMIT 1
                """, (farmer_id,))

                crop_row = cursor.fetchone()

                crop = (
                    crop_row[0]
                    if crop_row
                    else "No recommendation yet"
                )

                cursor.close()
                conn.close()

                profit = revenue - expenses

                report_text.delete(
                    "1.0",
                    tk.END
                )

                report_text.insert(
                    tk.END,
                    f"FARMER REPORT\n"
                    f"{'=' * 30}\n\n"
                    f"Farmer: {farmer_text}\n\n"
                    f"Number of Farms: {farm_count}\n"
                    f"Total Land: {land} acres\n\n"
                    f"Total Expenses:\n"
                    f"₹{expenses:,.2f}\n\n"
                    f"Total Revenue:\n"
                    f"₹{revenue:,.2f}\n\n"
                    f"Estimated Balance:\n"
                    f"₹{profit:,.2f}\n\n"
                    f"Latest Crop Recommendation:\n"
                    f"{crop}\n\n"
                    f"Report Date:\n"
                    f"{date.today()}"
                )

                # chart
                for widget in chart_card.winfo_children():
                    widget.destroy()

                tk.Label(
                    chart_card,
                    text="Financial Overview",
                    font=("Arial", 15, "bold"),
                    bg=WHITE,
                    fg=TEXT
                ).pack(
                    anchor="w",
                    padx=20,
                    pady=15
                )

                fig = Figure(
                    figsize=(6, 4),
                    dpi=90
                )

                ax = fig.add_subplot(111)

                labels = [
                    "Expenses",
                    "Revenue"
                ]

                values = [
                    expenses,
                    revenue
                ]

                ax.bar(
                    labels,
                    values
                )

                ax.set_ylabel("Amount (₹)")
                ax.set_title("Farmer Financial Summary")

                fig.tight_layout()

                canvas = FigureCanvasTkAgg(
                    fig,
                    master=chart_card
                )

                canvas.draw()

                canvas.get_tk_widget().pack(
                    fill="both",
                    expand=True,
                    padx=20,
                    pady=10
                )

            except Error as e:
                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        self.styled_button(
            top,
            "📊 Generate Report",
            generate_report
        ).pack(
            side="left",
            padx=15
        )


# ================================================================
# START APPLICATION
# ================================================================

def main():

    if not create_database():
        return

    if not setup_tables():
        return

    root = tk.Tk()

    # ttk styling
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except:
        pass

    style.configure(
        "Treeview",
        rowheight=30,
        font=("Arial", 9)
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 9, "bold")
    )

    app = AgricultureApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()

