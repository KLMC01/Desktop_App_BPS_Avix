from __future__ import annotations

import calendar
import os
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
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

        self.draw_3d_button(47, 343, 151, 379, "HOME", self.go_home, font=("Arial", 10, "bold"))

        self.canvas.create_text(506, 87, text="Dashboard", font=("Arial", 31, "bold"), fill="#666666")
        self.canvas.create_text(503, 86, text="Dashboard", font=("Arial", 31, "bold"), fill="black")
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

    # -------------------- Chart page --------------------
    def open_chart_page(self, chart_type: str):
        if not self.ensure_excel_loaded():
            return
        self.selected_chart = chart_type
        self.clear_page()
        self.bg_image = self.prepare_dark_background()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.rounded_rectangle(self.canvas, 27, 20, 693, 396, radius=28, fill=self.PANEL_RIGHT, outline="")
        self.rounded_rectangle(self.canvas, 27, 20, 318, 396, radius=28, fill=self.PANEL_LEFT, outline="")

        self.canvas.create_text(47, 52, text="Avix.lk", font=("Arial", 24, "bold"), fill=self.ACCENT, anchor="w")
        self.canvas.create_line(47, 65, 125, 65, fill=self.ACCENT, width=2)

        self.canvas.create_text(507, 52, text=self.selected_chart, font=("Arial", 28, "bold"), fill="#666666")
        self.canvas.create_text(504, 48, text=self.selected_chart, font=("Arial", 28, "bold"), fill="black")
        self.canvas.create_text(
            504,
            76,
            text="Click the heading to change chart type",
            font=("Arial", 9),
            fill=self.DARK_GREEN,
        )
        self.canvas.tag_bind(self.canvas.find_closest(504, 48)[0], "<Button-1>", lambda event: self.show_chart_type_menu())

        self._build_chart_controls()
        self._build_chart_preview()

        self.draw_3d_button(47, 343, 168, 379, "DASHBOARD", self.show_dashboard, font=("Arial", 10, "bold"))
        self.draw_3d_button(
            566,
            350,
            660,
            384,
            "DOWNLOAD",
            self.download_pdf,
            main_color=self.PURPLE_BUTTON,
            border_color=self.PURPLE_BORDER,
            inner_color=self.PURPLE_BUTTON,
            highlight_color=self.PURPLE_HIGHLIGHT,
            shadow_color="#3E176D",
            text_shadow="#4A1C7E",
            font=("Arial", 9, "bold"),
        )
        self.add_footer()

        if self.sheet_names:
            self.sheet_var.set(self.sheet_names[0])
            self.load_selected_sheet()

    def show_chart_type_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        for chart_type in CHART_TYPES:
            menu.add_command(label=chart_type, command=lambda c=chart_type: self.open_chart_page(c))
        menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def _make_combo(self, x, y, variable, values, width=16, callback=None):
        combo = ttk.Combobox(
            self.root,
            textvariable=variable,
            values=values,
            state="readonly",
            width=width,
            font=("Arial", 9),
        )
        self.canvas.create_window(x, y, window=combo, anchor="w")
        if callback:
            combo.bind("<<ComboboxSelected>>", callback)
        return combo

    def _build_chart_controls(self):
        label_x = 58
        input_x = 178
        rows = [102, 133, 164, 195, 226, 257, 288]
        labels = ["Sheet", "X axis", "Y axis", "Date column", "Calculation", "Start date", "End date"]
        for y, label in zip(rows, labels):
            self.canvas.create_text(label_x, y, text=label, font=("Arial", 10, "bold"), fill=self.DARK_GREEN, anchor="w")

        self.sheet_combo = self._make_combo(178, 102, self.sheet_var, self.sheet_names, width=15, callback=lambda event: self.load_selected_sheet())
        self.x_combo = self._make_combo(178, 133, self.x_var, [], width=15)
        self.y_combo = self._make_combo(178, 164, self.y_var, [], width=15)
        self.date_combo = self._make_combo(178, 195, self.date_column_var, ["None"], width=15, callback=lambda event: self.reset_date_range())
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
        self.canvas.create_window(178, 257, window=self.start_date_label, anchor="w")
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
        self.canvas.create_window(282, 257, window=calendar_start)

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
        self.canvas.create_window(178, 288, window=self.end_date_label, anchor="w")
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
        self.canvas.create_window(282, 288, window=calendar_end)

        self.draw_3d_button(
            185,
            309,
            292,
            340,
            "GENERATE",
            self.generate_chart,
            main_color=self.PURPLE_BUTTON,
            border_color=self.PURPLE_BORDER,
            inner_color=self.PURPLE_BUTTON,
            highlight_color=self.PURPLE_HIGHLIGHT,
            shadow_color="#3E176D",
            text_shadow="#4A1C7E",
            font=("Arial", 9, "bold"),
        )

    def _build_chart_preview(self):
        preview = tk.Frame(self.root, bg="#DCDCDC", bd=1, relief="solid")
        self.canvas.create_window(358, 91, window=preview, anchor="nw", width=294, height=233)
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
            converted = pd.to_datetime(
                self.current_df[column],
                errors="coerce",
                format="mixed",
                dayfirst=True
            )
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
            converted = pd.to_datetime(self.current_df[column], errors="coerce").dropna()
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
            dates = pd.to_datetime(df[date_column], errors="coerce")
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

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.figure = Figure(figsize=(4.15, 3.1), dpi=80, facecolor="#DCDCDC")
        axis = self.figure.add_subplot(111)
        labels = result[self.x_var.get()].tolist()
        values = result["value"].tolist()

        if self.selected_chart == "Bar Chart":
            axis.barh(labels, values)
            axis.invert_yaxis()
            axis.set_xlabel(self.y_var.get())
            axis.set_ylabel(self.x_var.get())
        elif self.selected_chart == "Column Chart":
            axis.bar(labels, values)
            axis.set_xlabel(self.x_var.get())
            axis.set_ylabel(self.y_var.get())
            axis.tick_params(axis="x", rotation=45)
        elif self.selected_chart == "Line Chart":
            axis.plot(labels, values, marker="o")
            axis.set_xlabel(self.x_var.get())
            axis.set_ylabel(self.y_var.get())
            axis.tick_params(axis="x", rotation=45)
            axis.grid(True, alpha=0.25)
        elif self.selected_chart == "Pie Chart":
            positive = [(label, value) for label, value in zip(labels, values) if value >= 0]
            if not positive or sum(value for _, value in positive) <= 0:
                messagebox.showerror("Unable to generate pie chart", "Pie charts require positive values.")
                return
            pie_labels, pie_values = zip(*positive)
            axis.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90)
            axis.axis("equal")

        axis.set_title(self.last_chart_title, fontsize=10, fontweight="bold")
        self.figure.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=self.preview_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    # -------------------- PDF export --------------------
    def download_pdf(self):
        if self.figure is None or self.last_result is None:
            messagebox.showwarning("Generate chart first", "Generate a chart before downloading the PDF report.")
            return

        default_name = f"Avix_{self.selected_chart.replace(' ', '_')}_Report.pdf"
        output_path = filedialog.asksaveasfilename(
            title="Save PDF report",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF file", "*.pdf")],
        )
        if not output_path:
            return

        try:
            with PdfPages(output_path) as pdf:
                report = Figure(figsize=(8.27, 11.69))
                report.text(0.5, 0.965, "Avix Mobile LK", ha="center", fontsize=20, fontweight="bold")
                report.text(0.5, 0.935, "Business Analysis Report", ha="center", fontsize=14)
                report.text(0.08, 0.89, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fontsize=9)
                report.text(0.08, 0.865, f"Workbook: {os.path.basename(self.excel_path or '')}", fontsize=9)
                report.text(0.08, 0.84, f"Worksheet: {self.sheet_var.get()}", fontsize=9)
                report.text(0.08, 0.815, f"Chart type: {self.selected_chart}", fontsize=9)
                report.text(0.08, 0.79, f"X axis: {self.x_var.get()}", fontsize=9)
                report.text(0.08, 0.765, f"Y axis: {self.y_var.get()}", fontsize=9)
                report.text(0.08, 0.74, f"Calculation: {self.aggregation_var.get()}", fontsize=9)
                report.text(
                    0.08,
                    0.715,
                    f"Date range: {self.start_date_var.get()} to {self.end_date_var.get()}",
                    fontsize=9,
                )

                chart_axis = report.add_axes([0.09, 0.38, 0.82, 0.29])
                labels = self.last_result[self.x_var.get()].tolist()
                values = self.last_result["value"].tolist()

                if self.selected_chart == "Bar Chart":
                    chart_axis.barh(labels, values)
                    chart_axis.invert_yaxis()
                    chart_axis.set_xlabel(self.y_var.get())
                elif self.selected_chart == "Column Chart":
                    chart_axis.bar(labels, values)
                    chart_axis.tick_params(axis="x", rotation=45)
                elif self.selected_chart == "Line Chart":
                    chart_axis.plot(labels, values, marker="o")
                    chart_axis.tick_params(axis="x", rotation=45)
                    chart_axis.grid(True, alpha=0.25)
                else:
                    chart_axis.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
                    chart_axis.axis("equal")

                chart_axis.set_title(self.last_chart_title, fontsize=12, fontweight="bold")

                summary = self.last_result.sort_values("value", ascending=False).head(5)
                report.text(0.08, 0.32, "Top results", fontsize=12, fontweight="bold")
                y = 0.29
                for _, row in summary.iterrows():
                    report.text(
                        0.1,
                        y,
                        f"• {row[self.x_var.get()]}: {row['value']:,.2f}",
                        fontsize=10,
                    )
                    y -= 0.025

                report.text(
                    0.5,
                    0.04,
                    "Generated by the Avix Business Support System",
                    ha="center",
                    fontsize=8,
                )
                pdf.savefig(report)

            messagebox.showinfo("PDF created", f"The report was saved successfully:\n\n{output_path}")
        except Exception as exc:
            messagebox.showerror("PDF export failed", f"The PDF report could not be created.\n\nDetails: {exc}")


if __name__ == "__main__":
    app = tk.Tk()
    app.title("Avix Mobile")
    app.geometry("720x480")
    app.resizable(False, False)
    DashboardPage(app, app.destroy)
    app.mainloop()
