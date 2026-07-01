from __future__ import annotations

import calendar
import os
import textwrap
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
import numpy as np
from PIL import Image, ImageTk, ImageDraw

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


CHART_TYPES = ["Bar Chart", "Line Chart", "Pie Chart", "Column Chart"]
AGGREGATIONS = ["Sum", "Average", "Count", "Minimum", "Maximum"]


class CalendarDialog(tk.Toplevel):
    """Simple dependency-free calendar picker."""

    def __init__(self, parent: tk.Misc, initial_date: date | None = None, title: str = "Select date"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#EAF7F7")

        selected = initial_date or date.today()
        self.year = selected.year
        self.month = selected.month
        self.result: date | None = None

        self.header = tk.Frame(self, bg="#EAF7F7")
        self.header.pack(fill="x", padx=10, pady=(10, 4))

        tk.Button(
            self.header,
            text="◀",
            command=self.previous_month,
            bg="#80BCA6",
            fg="white",
            activebackground="#6EA992",
            relief="flat",
            font=("Arial", 10, "bold"),
            width=4,
            cursor="hand2",
        ).pack(side="left")

        self.month_label = tk.Label(
            self.header,
            bg="#EAF7F7",
            fg="#0E4A37",
            font=("Arial", 12, "bold"),
            width=18,
        )
        self.month_label.pack(side="left", padx=8)

        tk.Button(
            self.header,
            text="▶",
            command=self.next_month,
            bg="#80BCA6",
            fg="white",
            activebackground="#6EA992",
            relief="flat",
            font=("Arial", 10, "bold"),
            width=4,
            cursor="hand2",
        ).pack(side="right")

        self.days_frame = tk.Frame(self, bg="#EAF7F7")
        self.days_frame.pack(padx=10, pady=(2, 10))
        self.draw_month()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def previous_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.draw_month()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.draw_month()

    def draw_month(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        self.month_label.configure(text=f"{calendar.month_name[self.month]} {self.year}")

        for column, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            tk.Label(
                self.days_frame,
                text=name,
                bg="#EAF7F7",
                fg="#0E4A37",
                font=("Arial", 9, "bold"),
                width=4,
            ).grid(row=0, column=column, padx=1, pady=2)

        weeks = calendar.monthcalendar(self.year, self.month)
        today = date.today()

        for row, week in enumerate(weeks, start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    tk.Label(self.days_frame, text="", bg="#EAF7F7", width=4).grid(
                        row=row, column=column, padx=1, pady=1
                    )
                    continue

                chosen = date(self.year, self.month, day_number)
                is_today = chosen == today
                button = tk.Button(
                    self.days_frame,
                    text=str(day_number),
                    command=lambda d=chosen: self.choose(d),
                    bg="#5D8C00" if is_today else "white",
                    fg="white" if is_today else "#0E4A37",
                    activebackground="#91D9C0",
                    activeforeground="#0E4A37",
                    relief="flat",
                    width=4,
                    font=("Arial", 9, "bold" if is_today else "normal"),
                    cursor="hand2",
                )
                button.grid(row=row, column=column, padx=1, pady=1)

    def choose(self, selected: date):
        self.result = selected
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    @classmethod
    def ask_date(cls, parent: tk.Misc, initial_date: date | None = None, title: str = "Select date"):
        dialog = cls(parent, initial_date=initial_date, title=title)
        parent.wait_window(dialog)
        return dialog.result


class DashboardPage:
    """Dashboard, chart builder, Excel reader and PDF exporter in one file."""

    def __init__(self, root: tk.Tk, go_home):
        self.root = root
        self.go_home = go_home
        self.width = 720
        self.height = 480
        self.project_dir = Path(__file__).resolve().parent

        self.PANEL_LEFT = "#91D9C0"
        self.PANEL_RIGHT = "#BFE9EA"
        self.DARK_GREEN = "#0E4A37"
        self.ACCENT = "#5B5A00"
        self.MUTED = "#5B6B68"

        self.BUTTON_BORDER = "#FF8A8A"
        self.BUTTON_MAIN = "#990000"
        self.BUTTON_INNER = "#B30000"
        self.BUTTON_HIGHLIGHT = "#D42A2A"
        self.BUTTON_SHADOW = "#2A0000"
        self.TEXT_SHADOW = "#5A0000"
        self.BUTTON_TEXT = "#FFFFFF"

        self.GREEN_BUTTON = "#80BCA6"
        self.GREEN_BORDER = "#4F8D7B"
        self.GREEN_HIGHLIGHT = "#9DD1BE"
        self.PURPLE_BUTTON = "#8A42E8"
        self.PURPLE_BORDER = "#5A209D"
        self.PURPLE_HIGHLIGHT = "#A96BFA"

        self.bg_image = None
        self.logo_image = None
        self.canvas = None
        self.figure = None
        self.chart_canvas = None
        self.last_result = None
        self.last_chart_type = None
        self.last_chart_title = None
        self.has_generated = False
        self.chart_heading_id = None
        self.chart_subheading_id = None
        self.left_panel_id = None
        self.preview_window_id = None
        self.control_items = []
        self.expand_button_items = []
        self.is_chart_expanded = False
        self.animation_running = False

        self.excel_path: str | None = getattr(self.root, "excel_path", None)
        self.excel_file: pd.ExcelFile | None = None
        self.current_df = pd.DataFrame()
        self.sheet_names: list[str] = []

        self.selected_chart = "Bar Chart"
        self.start_date: date | None = None
        self.end_date: date | None = None

        self.sheet_var = tk.StringVar()
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.date_column_var = tk.StringVar(value="None")
        self.aggregation_var = tk.StringVar(value="Sum")
        self.start_date_var = tk.StringVar(value="Not selected")
        self.end_date_var = tk.StringVar(value="Not selected")
        self.status_var = tk.StringVar(value="Upload an Excel file to begin.")

        self.show_dashboard()

    # -------------------- Assets and layout helpers --------------------
    def _asset_path(self, *names: str) -> Path | None:
        for name in names:
            path = self.project_dir / name
            if path.exists():
                return path
        return None

    def clear_page(self):
        if self.chart_canvas is not None:
            try:
                self.chart_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.chart_canvas = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def prepare_dark_background(self):
        bg_path = self._asset_path("Background.png", "background.png")
        if bg_path:
            bg = Image.open(bg_path).resize((720, 480)).convert("RGBA")
        else:
            bg = Image.new("RGBA", (720, 480), (4, 16, 26, 255))
        overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 145))
        return ImageTk.PhotoImage(Image.alpha_composite(bg, overlay))

    @staticmethod
    def rounded_rectangle(canvas_obj, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return canvas_obj.create_polygon(points, smooth=True, **kwargs)

    def add_footer(self):
        self.canvas.create_text(
            360,
            458,
            text="Copyright © 2026 Avix Mobile LK. All rights reserved.",
            font=("Roboto Mono", 9),
            fill="white",
        )

    def create_logo_image(self, size=50, radius=10):
        logo_path = self._asset_path("logo.jpg", "logo.png")
        if logo_path:
            logo = Image.open(logo_path).resize((size, size)).convert("RGBA")
        else:
            logo = Image.new("RGBA", (size, size), (255, 255, 255, 255))
            ImageDraw.Draw(logo).text((size // 4, size // 3), "A", fill="black")

        mask = Image.new("L", logo.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
        rounded = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        rounded.paste(logo, (0, 0), mask)
        self.logo_image = ImageTk.PhotoImage(rounded)
        return self.logo_image

    def draw_3d_button(
        self,
        x1,
        y1,
        x2,
        y2,
        text,
        command,
        main_color=None,
        border_color=None,
        inner_color=None,
        highlight_color=None,
        shadow_color=None,
        text_shadow=None,
        font=("Arial", 11, "bold"),
        enabled=True,
    ):
        main_color = main_color or self.BUTTON_MAIN
        border_color = border_color or self.BUTTON_BORDER
        inner_color = inner_color or self.BUTTON_INNER
        highlight_color = highlight_color or self.BUTTON_HIGHLIGHT
        shadow_color = shadow_color or self.BUTTON_SHADOW
        text_shadow = text_shadow or self.TEXT_SHADOW

        if not enabled:
            main_color = inner_color = "#8A9A96"
            highlight_color = "#AAB6B3"
            border_color = "#65736F"
            shadow_color = "#48514F"
            text_shadow = "#5A6461"

        shadow = self.rounded_rectangle(
            self.canvas, x1 + 3, y1 + 5, x2 + 3, y2 + 5, radius=7, fill=shadow_color, outline=""
        )
        fill = self.rounded_rectangle(
            self.canvas, x1, y1, x2, y2, radius=7, fill=main_color, outline=border_color, width=2
        )
        inner = self.rounded_rectangle(
            self.canvas, x1 + 6, y1 + 6, x2 - 6, y2 - 4, radius=6, fill=inner_color, outline=""
        )
        highlight = self.rounded_rectangle(
            self.canvas, x1 + 10, y1 + 6, x2 - 10, y1 + 17, radius=5, fill=highlight_color, outline=""
        )
        tx = (x1 + x2) / 2
        ty = (y1 + y2) / 2
        shadow_text = self.canvas.create_text(tx + 2, ty + 2, text=text, font=font, fill=text_shadow)
        main_text = self.canvas.create_text(tx, ty, text=text, font=font, fill=self.BUTTON_TEXT)

        items = [shadow, fill, inner, highlight, shadow_text, main_text]
        if enabled:
            for item in items:
                self.canvas.tag_bind(item, "<Button-1>", lambda event: command())
                self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))
        return items

    # -------------------- Excel handling --------------------
    def upload_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel sales file",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            self.excel_file = pd.ExcelFile(file_path)
            if not self.excel_file.sheet_names:
                raise ValueError("The workbook has no worksheets.")
            self.excel_path = file_path
            self.root.excel_path = file_path
            self.sheet_names = list(self.excel_file.sheet_names)
            preview = pd.read_excel(file_path, sheet_name=self.sheet_names[0], nrows=5)
            if preview.empty and not list(preview.columns):
                raise ValueError("The first worksheet does not contain readable tabular data.")
        except ImportError as exc:
            missing = "openpyxl" if str(file_path).lower().endswith(".xlsx") else "xlrd"
            messagebox.showerror(
                "Missing dependency",
                f"Python needs the '{missing}' package to read this Excel format.\n\n"
                f"Install it using:\npython -m pip install {missing}",
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Unable to open workbook",
                "The Excel file could not be opened. Make sure it is a valid .xlsx or .xls file.\n\n"
                f"Details: {exc}",
            )
            return

        self.status_var.set(
            f"Loaded: {os.path.basename(file_path)}  •  {len(self.sheet_names)} sheet(s)"
        )
        self.show_dashboard()

    def ensure_excel_loaded(self) -> bool:
        if self.excel_path and self.excel_file is None:
            try:
                self.excel_file = pd.ExcelFile(self.excel_path)
                self.sheet_names = list(self.excel_file.sheet_names)
            except Exception:
                self.excel_file = None
        if not self.excel_path or self.excel_file is None:
            messagebox.showwarning("Excel file required", "Please upload an Excel file first.")
            return False
        return True

    # -------------------- Dashboard page --------------------
    def show_dashboard(self):
        self.clear_page()
        self.bg_image = self.prepare_dark_background()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.rounded_rectangle(self.canvas, 27, 47, 693, 396, radius=28, fill=self.PANEL_RIGHT, outline="")
        self.rounded_rectangle(self.canvas, 27, 47, 318, 396, radius=28, fill=self.PANEL_LEFT, outline="")

        self.canvas.create_text(47, 82, text="Avix.lk", font=("Arial", 25, "bold"), fill=self.ACCENT, anchor="w")
        self.canvas.create_line(47, 96, 125, 96, fill=self.ACCENT, width=2)
        self.canvas.create_text(
            57,
            126,
            text="Upload your Excel sales\nfile to begin business\nanalysis and decision\nsupport.",
            font=("Arial", 13, "bold"),
            fill=self.DARK_GREEN,
            anchor="nw",
            justify="left",
        )

        self.draw_3d_button(
            87,
            230,
            253,
            269,
            "UPLOAD EXCEL FILE",
            self.upload_excel_file,
            main_color=self.GREEN_BUTTON,
            border_color=self.GREEN_BORDER,
            inner_color=self.GREEN_BUTTON,
            highlight_color=self.GREEN_HIGHLIGHT,
            shadow_color="#3F7464",
            text_shadow="#3F6F63",
            font=("Arial", 10, "bold"),
        )

        status = self.status_var.get()
        if self.excel_path:
            status = f"Loaded: {os.path.basename(self.excel_path)}"
        self.canvas.create_text(
            170,
            300,
            text=status,
            font=("Arial", 9, "bold"),
            fill=self.DARK_GREEN if self.excel_path else self.MUTED,
            width=235,
            justify="center",
        )

        self.draw_3d_button(47, 347, 119, 377, "HOME", self.go_home, font=("Arial", 9, "bold"))
        self.draw_3d_button(128, 347, 210, 377, "LOGIN", self.go_login, font=("Arial", 9, "bold"))

        self.canvas.create_text(503, 83, text="Dashboard", font=("Arial", 31, "bold"), fill="black")
        self.canvas.create_text(
            503,
            124,
            text="Choose a chart type after uploading the workbook",
            font=("Arial", 10),
            fill=self.DARK_GREEN,
        )

        positions = [
            (352, 170, 477, 218, "BAR CHART"),
            (523, 170, 648, 218, "LINE CHART"),
            (352, 270, 477, 318, "PIE CHART"),
            (523, 270, 648, 318, "COLUMN CHART"),
        ]
        colors = [
            ("#27C87A", "#138A50", "#27C87A", "#62E5A7", "#0A6B3B", "#176A45"),
            ("#28B8E0", "#167D9C", "#28B8E0", "#65D5F2", "#0E6680", "#176A7B"),
            ("#F0A83B", "#A26A13", "#F0A83B", "#FFD07A", "#80500C", "#8D5C12"),
            ("#8A65E8", "#5C3BA5", "#8A65E8", "#AD93F2", "#442B7A", "#51358C"),
        ]
        enabled = bool(self.excel_path)

        for (x1, y1, x2, y2, label), palette in zip(positions, colors):
            chart_type = label.title()
            self.draw_3d_button(
                x1,
                y1,
                x2,
                y2,
                label,
                lambda c=chart_type: self.open_chart_page(c),
                main_color=palette[0],
                border_color=palette[1],
                inner_color=palette[2],
                highlight_color=palette[3],
                shadow_color=palette[4],
                text_shadow=palette[5],
                font=("Arial", 10, "bold"),
                enabled=enabled,
            )

        self.rounded_rectangle(self.canvas, 611, 409, 675, 472, radius=10, fill="#000000", outline="#00D8FF", width=2)
        self.canvas.create_image(643, 440, image=self.create_logo_image(50, 10), anchor="center")
        self.add_footer()

    def go_login(self):
        """Open the application's login page when available."""
        callback = getattr(self.root, "show_login_page", None)
        if callable(callback):
            callback()
        else:
            messagebox.showwarning("Navigation unavailable", "The login page callback is not available in main.py.")

    # -------------------- Chart page --------------------
    def open_chart_page(self, chart_type: str):
        if not self.ensure_excel_loaded():
            return
        self.selected_chart = chart_type
        self.has_generated = False
        self.is_chart_expanded = False
        self.animation_running = False
        self.control_items = []
        self.expand_button_items = []
        self.clear_page()
        self.bg_image = self.prepare_dark_background()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.rounded_rectangle(self.canvas, 27, 20, 693, 396, radius=28, fill=self.PANEL_RIGHT, outline="")
        self.left_panel_id = self.rounded_rectangle(
            self.canvas, 27, 20, 318, 396, radius=28, fill=self.PANEL_LEFT, outline=""
        )

        avix_title = self.canvas.create_text(
            47, 52, text="Avix.lk", font=("Arial", 24, "bold"), fill=self.ACCENT, anchor="w"
        )
        avix_line = self.canvas.create_line(47, 65, 125, 65, fill=self.ACCENT, width=2)
        self.control_items.extend([avix_title, avix_line])

        self.chart_heading_id = self.canvas.create_text(
            504, 48, text=self.selected_chart, font=("Arial", 28, "bold"), fill="black"
        )
        self.chart_subheading_id = self.canvas.create_text(
            504,
            76,
            text="Click the heading to change chart type",
            font=("Arial", 9),
            fill=self.DARK_GREEN,
        )
        self.canvas.tag_bind(self.chart_heading_id, "<Button-1>", lambda event: self.show_chart_type_menu())
        self.canvas.tag_bind(self.chart_heading_id, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(self.chart_heading_id, "<Leave>", lambda event: self.canvas.config(cursor=""))

        self._build_chart_controls()
        self._build_chart_preview()

        self.draw_3d_button(47, 348, 132, 376, "DASHBOARD", self.show_dashboard, font=("Arial", 8, "bold"))
        self.draw_3d_button(
            557, 350, 661, 382, "DOWNLOAD", self.download_pdf,
            main_color="#E39A2D", border_color="#9C6516", inner_color="#E39A2D",
            highlight_color="#F7C36A", shadow_color="#704609", text_shadow="#80530F",
            font=("Arial", 8, "bold"),
        )
        self.expand_button_items = self.draw_3d_button(
            469, 352, 548, 379, "MAXIMIZE", self.maximize_chart,
            main_color="#2B6CB0", border_color="#194A7A", inner_color="#2B6CB0",
            highlight_color="#6AA6E8", shadow_color="#123757", text_shadow="#183F67",
            font=("Arial", 7, "bold"),
        )

        self.rounded_rectangle(self.canvas, 611, 409, 675, 472, radius=10, fill="#000000", outline="#00D8FF", width=2)
        self.canvas.create_image(643, 440, image=self.create_logo_image(50, 10), anchor="center")
        self.add_footer()

        if self.sheet_names:
            self.sheet_var.set(self.sheet_names[0])
            self.load_selected_sheet()

    def show_chart_type_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        for chart_type in CHART_TYPES:
            menu.add_command(label=chart_type, command=lambda c=chart_type: self.change_chart_type(c))
        menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def change_chart_type(self, chart_type: str):
        """Change chart type without losing the user's current selections."""
        self.selected_chart = chart_type
        if self.chart_heading_id is not None:
            self.canvas.itemconfigure(self.chart_heading_id, text=chart_type)
        if self.has_generated:
            self.generate_chart()

    def _make_combo(self, x, y, variable, values, width=16, callback=None):
        combo = ttk.Combobox(
            self.root,
            textvariable=variable,
            values=values,
            state="readonly",
            width=width,
            font=("Arial", 9),
        )
        item_id = self.canvas.create_window(x, y, window=combo, anchor="w")
        self.control_items.append(item_id)
        if callback:
            combo.bind("<<ComboboxSelected>>", callback)
        return combo

    def _build_chart_controls(self):
        label_x = 58
        rows = [102, 133, 164, 195, 226, 257, 288]
        labels = ["Sheet", "X axis", "Y axis", "Date column", "Calculation", "Start date", "End date"]
        for y, label in zip(rows, labels):
            item_id = self.canvas.create_text(
                label_x, y, text=label, font=("Arial", 10, "bold"), fill=self.DARK_GREEN, anchor="w"
            )
            self.control_items.append(item_id)

        self.sheet_combo = self._make_combo(
            178, 102, self.sheet_var, self.sheet_names, width=15,
            callback=lambda event: self.load_selected_sheet()
        )
        self.x_combo = self._make_combo(178, 133, self.x_var, [], width=15)
        self.y_combo = self._make_combo(178, 164, self.y_var, [], width=15)
        self.date_combo = self._make_combo(
            178, 195, self.date_column_var, ["None"], width=15,
            callback=lambda event: self.reset_date_range()
        )
        self.aggregation_combo = self._make_combo(178, 226, self.aggregation_var, AGGREGATIONS, width=15)

        self.start_date_label = tk.Label(
            self.root,
            textvariable=self.start_date_var,
            bg="#E7E7E7",
            fg="#333333",
            font=("Arial", 9),
            width=14,
            anchor="w",
            padx=5,
        )
        start_label_item = self.canvas.create_window(178, 257, window=self.start_date_label, anchor="w")
        self.control_items.append(start_label_item)
        calendar_start = tk.Button(
            self.root,
            text="📅",
            command=lambda: self.pick_date("start"),
            bg="#80BCA6",
            fg="white",
            activebackground="#6EA992",
            relief="flat",
            cursor="hand2",
            width=3,
        )
        start_calendar_item = self.canvas.create_window(282, 257, window=calendar_start)
        self.control_items.append(start_calendar_item)

        self.end_date_label = tk.Label(
            self.root,
            textvariable=self.end_date_var,
            bg="#E7E7E7",
            fg="#333333",
            font=("Arial", 9),
            width=14,
            anchor="w",
            padx=5,
        )
        end_label_item = self.canvas.create_window(178, 288, window=self.end_date_label, anchor="w")
        self.control_items.append(end_label_item)
        calendar_end = tk.Button(
            self.root,
            text="📅",
            command=lambda: self.pick_date("end"),
            bg="#80BCA6",
            fg="white",
            activebackground="#6EA992",
            relief="flat",
            cursor="hand2",
            width=3,
        )
        end_calendar_item = self.canvas.create_window(282, 288, window=calendar_end)
        self.control_items.append(end_calendar_item)

        generate_items = self.draw_3d_button(
            185, 309, 292, 340, "GENERATE", self.generate_chart,
            main_color="#7B2CBF", border_color="#4B176E",
            inner_color="#7B2CBF", highlight_color="#B46CE0",
            shadow_color="#3A0F55", text_shadow="#4B176E",
            font=("Arial", 9, "bold"),
        )
        self.control_items.extend(generate_items)

    def _build_chart_preview(self):
        preview = tk.Frame(self.root, bg="#DCDCDC", bd=1, relief="solid")
        self.preview_window_id = self.canvas.create_window(
            358, 91, window=preview, anchor="nw", width=294, height=233
        )
        self.preview_frame = preview
        tk.Label(
            preview,
            text="Select fields and click Generate",
            bg="#DCDCDC",
            fg="#6D6D6D",
            font=("Arial", 11, "bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")

    def load_selected_sheet(self):
        if not self.sheet_var.get() or not self.excel_path:
            return
        try:
            self.current_df = pd.read_excel(self.excel_path, sheet_name=self.sheet_var.get())
        except Exception as exc:
            messagebox.showerror("Unable to read worksheet", str(exc))
            return

        columns = [str(column) for column in self.current_df.columns]
        numeric_columns = [
            str(column)
            for column in self.current_df.columns
            if pd.api.types.is_numeric_dtype(self.current_df[column])
        ]
        date_columns = []
        for column in self.current_df.columns:
            if pd.api.types.is_datetime64_any_dtype(self.current_df[column]):
                date_columns.append(str(column))
                continue
            converted = pd.to_datetime(self.current_df[column], errors="coerce", format="mixed", dayfirst=True)
            if len(converted) and converted.notna().mean() >= 0.75:
                date_columns.append(str(column))

        self.x_combo.configure(values=columns)
        self.y_combo.configure(values=numeric_columns or columns)
        self.date_combo.configure(values=["None"] + date_columns)

        if columns:
            self.x_var.set(columns[0])
        if numeric_columns:
            self.y_var.set(numeric_columns[0])
        elif columns:
            self.y_var.set(columns[-1])
        self.date_column_var.set(date_columns[0] if date_columns else "None")
        self.reset_date_range()

    # -------------------- Date selection --------------------
    def reset_date_range(self):
        self.start_date = None
        self.end_date = None
        self.start_date_var.set("Not selected")
        self.end_date_var.set("Not selected")

        column = self.date_column_var.get()
        if column and column != "None" and column in self.current_df.columns:
            converted = pd.to_datetime(self.current_df[column], errors="coerce", format="mixed", dayfirst=True).dropna()
            if not converted.empty:
                self.start_date = converted.min().date()
                self.end_date = converted.max().date()
                self.start_date_var.set(self.start_date.strftime("%Y-%m-%d"))
                self.end_date_var.set(self.end_date.strftime("%Y-%m-%d"))

    def pick_date(self, which: str):
        column = self.date_column_var.get()
        if not column or column == "None":
            messagebox.showinfo("Select date column", "Select a date column before choosing a date range.")
            return

        initial = self.start_date if which == "start" else self.end_date
        selected = CalendarDialog.ask_date(
            self.root,
            initial_date=initial,
            title="Select start date" if which == "start" else "Select end date",
        )
        if selected is None:
            return

        if which == "start":
            if self.end_date and selected > self.end_date:
                messagebox.showwarning("Invalid range", "Start date cannot be after the end date.")
                return
            self.start_date = selected
            self.start_date_var.set(selected.strftime("%Y-%m-%d"))
        else:
            if self.start_date and selected < self.start_date:
                messagebox.showwarning("Invalid range", "End date cannot be before the start date.")
                return
            self.end_date = selected
            self.end_date_var.set(selected.strftime("%Y-%m-%d"))

    # -------------------- Chart generation --------------------
    def _filtered_dataframe(self) -> pd.DataFrame:
        df = self.current_df.copy()
        date_column = self.date_column_var.get()
        if date_column and date_column != "None" and date_column in df.columns:
            dates = pd.to_datetime(df[date_column], errors="coerce", format="mixed", dayfirst=True)
            mask = dates.notna()
            if self.start_date:
                mask &= dates.dt.date >= self.start_date
            if self.end_date:
                mask &= dates.dt.date <= self.end_date
            df = df.loc[mask].copy()
        return df

    def _aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        agg = self.aggregation_var.get()

        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError("Please select valid X-axis and Y-axis columns.")

        working = df[[x_col, y_col]].copy()
        working = working.dropna(subset=[x_col])

        if agg != "Count":
            working[y_col] = pd.to_numeric(working[y_col], errors="coerce")
            working = working.dropna(subset=[y_col])
            if working.empty:
                raise ValueError("The selected Y-axis does not contain usable numeric values.")

        grouped = working.groupby(x_col, dropna=False)[y_col]
        if agg == "Sum":
            result = grouped.sum()
        elif agg == "Average":
            result = grouped.mean()
        elif agg == "Count":
            result = grouped.count()
        elif agg == "Minimum":
            result = grouped.min()
        elif agg == "Maximum":
            result = grouped.max()
        else:
            raise ValueError("Unsupported calculation.")

        output = result.reset_index(name="value")
        output[x_col] = output[x_col].astype(str)
        return output

    def _draw_chart_on_axis(self, axis, result=None, chart_type=None, title=None):
        result = result if result is not None else self.last_result
        chart_type = chart_type or self.selected_chart
        if result is None:
            raise ValueError("No chart data is available.")

        labels = result[self.x_var.get()].tolist()
        values = result["value"].tolist()

        if chart_type == "Bar Chart":
            axis.barh(labels, values)
            axis.invert_yaxis()
            axis.set_xlabel(self.y_var.get())
            axis.set_ylabel(self.x_var.get())
        elif chart_type == "Column Chart":
            axis.bar(labels, values)
            axis.set_xlabel(self.x_var.get())
            axis.set_ylabel(self.y_var.get())
            axis.tick_params(axis="x", rotation=45)
        elif chart_type == "Line Chart":
            axis.plot(labels, values, marker="o", linewidth=2)
            axis.set_xlabel(self.x_var.get())
            axis.set_ylabel(self.y_var.get())
            axis.tick_params(axis="x", rotation=45)
            axis.grid(True, alpha=0.25)
        elif chart_type == "Pie Chart":
            positive = [(label, value) for label, value in zip(labels, values) if value >= 0]
            if not positive or sum(value for _, value in positive) <= 0:
                raise ValueError("Pie charts require positive values.")
            pie_labels, pie_values = zip(*positive)
            axis.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90)
            axis.axis("equal")

        axis.set_title(title or self.last_chart_title or chart_type, fontsize=11, fontweight="bold")

    def generate_chart(self):
        if self.current_df.empty:
            messagebox.showwarning("No worksheet data", "The selected worksheet has no usable rows.")
            return

        try:
            filtered = self._filtered_dataframe()
            if filtered.empty:
                raise ValueError("No rows are available for the selected date range.")
            result = self._aggregate(filtered)
            if result.empty:
                raise ValueError("No chart data could be created from the selected columns.")
        except Exception as exc:
            messagebox.showerror("Unable to generate chart", str(exc))
            return

        if self.selected_chart == "Pie Chart":
            result = result.sort_values("value", ascending=False).head(8)
        else:
            result = result.sort_values("value", ascending=False).head(15)

        self.last_result = result
        self.last_chart_type = self.selected_chart
        self.last_chart_title = f"{self.aggregation_var.get()} of {self.y_var.get()} by {self.x_var.get()}"
        self.has_generated = True

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.figure = Figure(figsize=(4.15, 3.1), dpi=80, facecolor="#DCDCDC")
        axis = self.figure.add_subplot(111)
        try:
            self._draw_chart_on_axis(axis, result=result)
        except ValueError as exc:
            messagebox.showerror("Unable to generate chart", str(exc))
            return
        self.figure.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=self.preview_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _set_expand_button_text(self, text: str):
        if len(self.expand_button_items) >= 2:
            for item in self.expand_button_items[-2:]:
                self.canvas.itemconfigure(item, text=text)

    def maximize_chart(self):
        """Animate the controls out of view and enlarge the embedded chart area."""
        if self.last_result is None:
            messagebox.showwarning("Generate chart first", "Generate a chart before maximizing it.")
            return
        if self.animation_running:
            return

        self.animation_running = True
        expanding = not self.is_chart_expanded
        total_steps = 18
        move_per_step = -14 if expanding else 14
        width_per_step = 14 if expanding else -14
        heading_move = -6 if expanding else 6
        target_text = "MINIMIZE" if expanding else "MAXIMIZE"

        def animate(step=0):
            if step >= total_steps:
                self.is_chart_expanded = expanding
                self.animation_running = False
                self._set_expand_button_text(target_text)
                if self.chart_canvas is not None:
                    self.chart_canvas.draw_idle()
                return

            if self.left_panel_id is not None:
                self.canvas.move(self.left_panel_id, move_per_step, 0)
            for item in self.control_items:
                try:
                    self.canvas.move(item, move_per_step, 0)
                except tk.TclError:
                    pass

            if self.preview_window_id is not None:
                self.canvas.move(self.preview_window_id, move_per_step, 0)
                current_width = float(self.canvas.itemcget(self.preview_window_id, "width") or 294)
                self.canvas.itemconfigure(self.preview_window_id, width=max(294, current_width + width_per_step))

            if self.chart_heading_id is not None:
                self.canvas.move(self.chart_heading_id, heading_move, 0)
            if self.chart_subheading_id is not None:
                self.canvas.move(self.chart_subheading_id, heading_move, 0)

            self.root.after(18, lambda: animate(step + 1))

        animate()

    # -------------------- PDF export --------------------
    def _add_report_watermark(self, figure):
        logo_path = self._asset_path("logo.jpg", "logo.png")
        if not logo_path:
            return
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((700, 700))
            image_array = np.asarray(logo)
            figure.figimage(
                image_array,
                xo=max(0, int((figure.bbox.xmax - image_array.shape[1]) / 2)),
                yo=max(0, int((figure.bbox.ymax - image_array.shape[0]) / 2)),
                alpha=0.055,
                zorder=0,
            )
        except Exception:
            pass

    def _report_footer(self, figure, page_number: int):
        figure.text(0.08, 0.028, "Avix Mobile LK • Business Support Analytics", fontsize=7.5, color="#5B6B68")
        figure.text(0.92, 0.028, f"Page {page_number}", fontsize=7.5, color="#5B6B68", ha="right")
        figure.lines.append(
            __import__("matplotlib").lines.Line2D([0.08, 0.92], [0.045, 0.045], transform=figure.transFigure, color="#91D9C0", linewidth=1)
        )

    def _insight_lines(self):
        ordered = self.last_result.sort_values("value", ascending=False)
        top = ordered.iloc[0]
        bottom = ordered.iloc[-1]
        total = float(ordered["value"].sum())
        average = float(ordered["value"].mean())
        count = len(ordered)
        x_col = self.x_var.get()
        return [
            f"Highest result: {top[x_col]} with {top['value']:,.2f}.",
            f"Lowest result: {bottom[x_col]} with {bottom['value']:,.2f}.",
            f"Combined value across {count} categories: {total:,.2f}; average category value: {average:,.2f}.",
        ]

    def download_pdf(self):
        """Export a professional report with exactly three pages.

        Page 1: portrait executive summary.
        Page 2: landscape chart-only page.
        Page 3: portrait detailed analysis.
        """
        if self.figure is None or self.last_result is None:
            messagebox.showwarning(
                "Generate chart first",
                "Generate a chart before downloading the PDF report.",
            )
            return

        default_name = f"Avix_{self.selected_chart.replace(' ', '_')}_Business_Report.pdf"
        output_path = filedialog.asksaveasfilename(
            title="Save professional PDF report",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF file", "*.pdf")],
        )
        if not output_path:
            return

        try:
            with PdfPages(output_path) as pdf:
                # ============================================================
                # PAGE 1 — PORTRAIT EXECUTIVE SUMMARY
                # ============================================================
                page1 = Figure(figsize=(8.27, 11.69), facecolor="#F8FBFB")
                self._add_report_watermark(page1)

                page1.text(
                    0.08, 0.95, "AVIX MOBILE LK",
                    fontsize=20, fontweight="bold", color="#0E4A37",
                )
                page1.text(
                    0.08, 0.922, "Business Analysis Report",
                    fontsize=13, color="#5B5A00",
                )
                page1.text(
                    0.92, 0.95,
                    datetime.now().strftime("%d %B %Y"),
                    fontsize=8.5, ha="right", color="#5B6B68",
                )
                page1.lines.append(
                    __import__("matplotlib").lines.Line2D(
                        [0.08, 0.92], [0.905, 0.905],
                        transform=page1.transFigure,
                        color="#91D9C0", linewidth=2,
                    )
                )

                page1.text(
                    0.08, 0.87, "REPORT OVERVIEW",
                    fontsize=11, fontweight="bold", color="#0E4A37",
                )

                metadata = [
                    ("Workbook", os.path.basename(self.excel_path or "")),
                    ("Worksheet", self.sheet_var.get()),
                    ("Chart type", self.selected_chart),
                    ("Analysis", self.last_chart_title or ""),
                    ("X-axis", self.x_var.get()),
                    ("Y-axis", self.y_var.get()),
                    ("Calculation", self.aggregation_var.get()),
                    ("Date range", f"{self.start_date_var.get()} to {self.end_date_var.get()}"),
                ]

                y = 0.83
                for index, (label, value) in enumerate(metadata):
                    column_x = 0.08 if index % 2 == 0 else 0.52
                    row_index = index // 2
                    item_y = y - (row_index * 0.065)
                    page1.text(
                        column_x, item_y,
                        label.upper(),
                        fontsize=7.5, fontweight="bold", color="#5B6B68",
                    )
                    page1.text(
                        column_x, item_y - 0.022,
                        str(value),
                        fontsize=9, color="#1F2D2A",
                    )

                page1.text(
                    0.08, 0.53, "EXECUTIVE SUMMARY",
                    fontsize=11, fontweight="bold", color="#0E4A37",
                )
                summary = (
                    f"This report analyses the {self.aggregation_var.get().lower()} of "
                    f"{self.y_var.get()} by {self.x_var.get()} using the selected Excel "
                    "worksheet and date range. The chart on page 2 provides a visual "
                    "comparison of the processed results, while page 3 presents the "
                    "detailed values, method, recommendations, and limitations."
                )
                page1.text(
                    0.08, 0.495,
                    "\n".join(textwrap.wrap(summary, 105)),
                    fontsize=9.5, color="#1F2D2A", va="top",
                    linespacing=1.45,
                )

                page1.text(
                    0.08, 0.37, "KEY INSIGHTS",
                    fontsize=11, fontweight="bold", color="#0E4A37",
                )
                insight_y = 0.335
                for line in self._insight_lines():
                    wrapped_lines = textwrap.wrap(line, 96)
                    page1.text(
                        0.095, insight_y,
                        "• " + "\n  ".join(wrapped_lines),
                        fontsize=9.5, color="#1F2D2A", va="top",
                        linespacing=1.4,
                    )
                    insight_y -= 0.055 + max(0, len(wrapped_lines) - 1) * 0.022

                page1.text(
                    0.08, 0.16, "REPORT PURPOSE",
                    fontsize=11, fontweight="bold", color="#0E4A37",
                )
                purpose = (
                    "The report supports evidence-based business decisions by converting "
                    "uploaded sales data into a clear visual analysis and structured findings. "
                    "The results should be reviewed together with stock levels, profit margins, "
                    "customer demand, and operational knowledge."
                )
                page1.text(
                    0.08, 0.13,
                    "\n".join(textwrap.wrap(purpose, 105)),
                    fontsize=9, color="#1F2D2A", va="top",
                    linespacing=1.4,
                )

                self._report_footer(page1, 1)
                pdf.savefig(page1, facecolor=page1.get_facecolor(), bbox_inches=None)

                # ============================================================
                # PAGE 2 — LANDSCAPE CHART PAGE
                # ============================================================
                page2 = Figure(figsize=(11.69, 8.27), facecolor="#F8FBFB")
                self._add_report_watermark(page2)

                page2.text(
                    0.055, 0.945, "AVIX MOBILE LK",
                    fontsize=17, fontweight="bold", color="#0E4A37",
                )
                page2.text(
                    0.055, 0.91, "Chart Analysis",
                    fontsize=11, color="#5B5A00",
                )
                page2.text(
                    0.945, 0.945,
                    self.selected_chart,
                    fontsize=10, ha="right", color="#5B6B68",
                )
                page2.lines.append(
                    __import__("matplotlib").lines.Line2D(
                        [0.055, 0.945], [0.885, 0.885],
                        transform=page2.transFigure,
                        color="#91D9C0", linewidth=2,
                    )
                )

                chart_axis = page2.add_axes([0.08, 0.16, 0.84, 0.66], facecolor="#FFFFFF")
                self._draw_chart_on_axis(
                    chart_axis,
                    result=self.last_result,
                    chart_type=self.selected_chart,
                    title=self.last_chart_title or self.selected_chart,
                )
                chart_axis.tick_params(labelsize=9)

                if self.selected_chart in ("Column Chart", "Line Chart"):
                    for label in chart_axis.get_xticklabels():
                        label.set_rotation(35)
                        label.set_horizontalalignment("right")

                page2.text(
                    0.055, 0.095,
                    f"Worksheet: {self.sheet_var.get()}   |   "
                    f"Date range: {self.start_date_var.get()} to {self.end_date_var.get()}   |   "
                    f"Calculation: {self.aggregation_var.get()}",
                    fontsize=8.5, color="#5B6B68",
                )

                self._report_footer(page2, 2)
                pdf.savefig(page2, facecolor=page2.get_facecolor(), bbox_inches=None)

                # ============================================================
                # PAGE 3 — PORTRAIT DETAILED ANALYSIS
                # ============================================================
                page3 = Figure(figsize=(8.27, 11.69), facecolor="#F8FBFB")
                self._add_report_watermark(page3)

                page3.text(
                    0.08, 0.95, "DETAILED ANALYSIS",
                    fontsize=18, fontweight="bold", color="#0E4A37",
                )
                page3.text(
                    0.08, 0.92,
                    self.last_chart_title or self.selected_chart,
                    fontsize=11, color="#5B5A00",
                )
                page3.lines.append(
                    __import__("matplotlib").lines.Line2D(
                        [0.08, 0.92], [0.90, 0.90],
                        transform=page3.transFigure,
                        color="#91D9C0", linewidth=2,
                    )
                )

                page3.text(
                    0.08, 0.865, "TOP ANALYSIS RESULTS",
                    fontsize=10.5, fontweight="bold", color="#0E4A37",
                )

                table_data = self.last_result.sort_values("value", ascending=False).head(12)
                table_axis = page3.add_axes([0.08, 0.59, 0.84, 0.27])
                table_axis.axis("off")
                cell_text = [
                    [str(row[self.x_var.get()]), f"{row['value']:,.2f}"]
                    for _, row in table_data.iterrows()
                ]
                table = table_axis.table(
                    cellText=cell_text,
                    colLabels=[
                        self.x_var.get(),
                        f"{self.aggregation_var.get()} of {self.y_var.get()}",
                    ],
                    loc="center",
                    cellLoc="left",
                    colColours=["#91D9C0", "#91D9C0"],
                )
                table.auto_set_font_size(False)
                table.set_fontsize(8.5)
                table.scale(1, 1.35)
                for (row, col), cell in table.get_celld().items():
                    cell.set_edgecolor("#C7D9D4")
                    if row == 0:
                        cell.set_text_props(weight="bold", color="#0E4A37")
                    elif row % 2 == 0:
                        cell.set_facecolor("#EDF7F4")

                page3.text(
                    0.08, 0.53, "METHODOLOGY",
                    fontsize=10.5, fontweight="bold", color="#0E4A37",
                )
                method = (
                    "The application imported the selected Excel worksheet, filtered "
                    "records using the chosen date column and calendar range, grouped "
                    "records by the selected X-axis field, and applied the selected "
                    f"{self.aggregation_var.get().lower()} calculation to "
                    f"{self.y_var.get()}. The processed result was visualized as a "
                    f"{self.selected_chart.lower()}."
                )
                page3.text(
                    0.08, 0.492,
                    "\n".join(textwrap.wrap(method, 108)),
                    fontsize=9, color="#1F2D2A", va="top",
                    linespacing=1.35,
                )

                page3.text(
                    0.08, 0.40, "BUSINESS RECOMMENDATIONS",
                    fontsize=10.5, fontweight="bold", color="#0E4A37",
                )
                ordered = self.last_result.sort_values("value", ascending=False)
                leader = ordered.iloc[0][self.x_var.get()]
                laggard = ordered.iloc[-1][self.x_var.get()]
                recommendations = [
                    (
                        f"Give priority to {leader}, which produced the strongest result, "
                        "when planning stock, promotion, or operational resources."
                    ),
                    (
                        f"Review the performance of {laggard} to determine whether pricing, "
                        "promotion, availability, or customer demand is limiting its result."
                    ),
                    (
                        "Repeat the analysis using updated data so decisions reflect the "
                        "latest business conditions."
                    ),
                    (
                        "Compare the findings with profit, stock level, and customer feedback "
                        "before making major purchasing decisions."
                    ),
                ]
                rec_y = 0.358
                for number, recommendation in enumerate(recommendations, start=1):
                    wrapped_lines = textwrap.wrap(recommendation, 96)
                    page3.text(
                        0.09, rec_y,
                        f"{number}.",
                        fontsize=9, fontweight="bold", color="#5B5A00",
                    )
                    page3.text(
                        0.12, rec_y,
                        "\n".join(wrapped_lines),
                        fontsize=9, color="#1F2D2A", va="top",
                        linespacing=1.3,
                    )
                    rec_y -= 0.05 + max(0, len(wrapped_lines) - 1) * 0.018

                page3.text(
                    0.08, 0.12, "LIMITATIONS",
                    fontsize=10.5, fontweight="bold", color="#0E4A37",
                )
                limitation = (
                    "Report accuracy depends on the completeness and correctness of the "
                    "uploaded Excel data. Missing values, inconsistent dates, duplicate "
                    "records, or incorrect numeric entries may affect the findings."
                )
                page3.text(
                    0.08, 0.111,
                    "\n".join(textwrap.wrap(limitation, 108)),
                    fontsize=8.5, color="#1F2D2A", va="top",
                    linespacing=1.3,
                )

                self._report_footer(page3, 3)
                pdf.savefig(page3, facecolor=page3.get_facecolor(), bbox_inches=None)

            messagebox.showinfo(
                "PDF created",
                "The professional three-page report was saved successfully:\n\n"
                f"{output_path}",
            )
        except Exception as exc:
            messagebox.showerror(
                "PDF export failed",
                "The PDF report could not be created.\n\n"
                f"Details: {exc}",
            )


if __name__ == "__main__":
    app = tk.Tk()
    app.title("Avix Mobile")
    app.geometry("720x480")
    app.resizable(False, False)
    DashboardPage(app, app.destroy)
    app.mainloop()
