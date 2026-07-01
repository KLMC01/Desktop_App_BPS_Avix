from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class DashboardPage:
    """Avix Mobile analytics dashboard.

    This class is compatible with the existing project constructor:
        DashboardPage(root, go_home)
    """

    CHARTS = (
        "Bar Chart",
        "Line Chart",
        "Pie Chart",
        "Column Chart",
    )

    COLORS = {
        "bg": "#07111F",
        "panel_left": "#91D9C0",
        "panel_right": "#BFE9EA",
        "text": "#123B28",
        "title": "#101010",
        "gold": "#626000",
        "button": "#7AB8A5",
        "button_hover": "#67A792",
        "primary": "#7C3AED",
        "primary_hover": "#6D28D9",
        "danger": "#DC2626",
        "danger_hover": "#B91C1C",
        "card": "#F4FBFA",
        "muted": "#5D6D68",
        "success": "#0F9D58",
        "border": "#75AFAE",
    }

    def __init__(self, root: tk.Misc, go_home):
        self.root = root
        self.go_home = go_home

        self.base_dir = Path(__file__).resolve().parent
        self.excel_path: Optional[str] = None
        self.excel_file: Optional[pd.ExcelFile] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.current_chart_name = self.CHARTS[0]
        self.current_figure: Optional[Figure] = None
        self.chart_canvas: Optional[FigureCanvasTkAgg] = None
        self.logo_image = None
        self.background_image = None

        self.main_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        self.main_frame.pack(fill="both", expand=True)

        self._configure_ttk()
        self.show_dashboard()

    # ------------------------------------------------------------------
    # Shared UI helpers
    # ------------------------------------------------------------------
    def _configure_ttk(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Avix.TCombobox",
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground="#15372B",
            bordercolor="#89AAA2",
            lightcolor="#89AAA2",
            darkcolor="#89AAA2",
            padding=5,
            arrowsize=14,
        )
        style.map(
            "Avix.TCombobox",
            fieldbackground=[("readonly", "#FFFFFF")],
            foreground=[("readonly", "#15372B")],
        )

    def _clear(self) -> None:
        if self.chart_canvas is not None:
            try:
                self.chart_canvas.get_tk_widget().destroy()
            except tk.TclError:
                pass
            self.chart_canvas = None

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _asset_path(self, *names: str) -> Optional[Path]:
        for name in names:
            path = self.base_dir / name
            if path.exists():
                return path
        return None

    def _load_background(self, width: int = 720, height: int = 480):
        path = self._asset_path("Background.png", "background.png")
        if not path:
            return None
        try:
            image = Image.open(path).convert("RGBA").resize((width, height))
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 150))
            image = Image.alpha_composite(image, overlay)
            self.background_image = ImageTk.PhotoImage(image)
            return self.background_image
        except Exception:
            return None

    def _load_logo(self, size: int = 52):
        path = self._asset_path("logo.jpg", "Logo.jpg", "logo.png")
        if not path:
            return None
        try:
            image = Image.open(path).convert("RGBA").resize((size, size))
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, size, size), radius=10, fill=255)
            rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
            rounded.paste(image, (0, 0), mask)
            self.logo_image = ImageTk.PhotoImage(rounded)
            return self.logo_image
        except Exception:
            return None

    def _background_canvas(self) -> tk.Canvas:
        canvas = tk.Canvas(
            self.main_frame,
            width=720,
            height=480,
            bg=self.COLORS["bg"],
            highlightthickness=0,
        )
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        image = self._load_background()
        if image:
            canvas.create_image(0, 0, image=image, anchor="nw")
        return canvas

    def _button(
        self,
        parent,
        text: str,
        command,
        bg: str,
        hover: str,
        fg: str = "white",
        width: int = 14,
        font=("Arial", 10, "bold"),
        state: str = "normal",
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            disabledforeground="#E8E8E8",
            relief="flat",
            bd=0,
            cursor="hand2" if state == "normal" else "arrow",
            width=width,
            font=font,
            padx=8,
            pady=7,
            state=state,
        )
        button.bind("<Enter>", lambda _e: button.config(bg=hover) if button["state"] == "normal" else None)
        button.bind("<Leave>", lambda _e: button.config(bg=bg) if button["state"] == "normal" else None)
        return button

    def _add_branding(self, parent: tk.Widget, compact: bool = False) -> None:
        tk.Label(
            parent,
            text="Avix.lk",
            bg=self.COLORS["panel_left"],
            fg=self.COLORS["gold"],
            font=("Arial", 21 if not compact else 18, "bold", "underline"),
        ).place(x=20, y=18)

    def _add_footer(self, canvas: tk.Canvas) -> None:
        canvas.create_text(
            360,
            458,
            text="Copyright © 2026 Avix Mobile LK. All rights reserved.",
            font=("Courier New", 9),
            fill="white",
        )
        logo = self._load_logo(48)
        if logo:
            canvas.create_image(643, 438, image=logo, anchor="center")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def show_dashboard(self) -> None:
        self._clear()
        canvas = self._background_canvas()

        container = tk.Frame(self.main_frame, bg=self.COLORS["panel_right"])
        container.place(x=27, y=47, width=666, height=349)

        left = tk.Frame(container, bg=self.COLORS["panel_left"])
        left.place(x=0, y=0, width=292, height=349)
        right = tk.Frame(container, bg=self.COLORS["panel_right"])
        right.place(x=292, y=0, width=374, height=349)

        self._add_branding(left)
        tk.Label(
            left,
            text="Upload your Excel sales\nfile to begin business\nanalysis and decision\nsupport process.",
            bg=self.COLORS["panel_left"],
            fg=self.COLORS["text"],
            justify="left",
            font=("Arial", 10, "bold"),
        ).place(x=30, y=80)

        self.file_status_var = tk.StringVar(
            value=(
                f"Selected: {Path(self.excel_path).name}"
                if self.excel_path
                else "No Excel file selected"
            )
        )
        tk.Label(
            left,
            textvariable=self.file_status_var,
            bg="#DDF4EB",
            fg=self.COLORS["text"],
            justify="left",
            wraplength=225,
            font=("Arial", 9, "bold"),
            padx=10,
            pady=8,
        ).place(x=20, y=190, width=252, height=48)

        upload = self._button(
            left,
            "Upload Excel File",
            self.upload_excel_file,
            self.COLORS["button"],
            self.COLORS["button_hover"],
            width=19,
            font=("Arial", 11, "bold"),
        )
        upload.place(x=52, y=252)

        home = self._button(
            left,
            "Home",
            self.go_home,
            self.COLORS["danger"],
            self.COLORS["danger_hover"],
            width=10,
        )
        home.place(x=20, y=302)

        tk.Label(
            right,
            text="Dashboard",
            bg=self.COLORS["panel_right"],
            fg=self.COLORS["title"],
            font=("Arial", 25, "bold"),
        ).pack(pady=(16, 4))
        tk.Label(
            right,
            text="Choose one analysis after uploading your workbook",
            bg=self.COLORS["panel_right"],
            fg=self.COLORS["muted"],
            font=("Arial", 9),
        ).pack()

        chart_area = tk.Frame(right, bg=self.COLORS["panel_right"])
        chart_area.place(x=22, y=78, width=330, height=245)

        enabled = self.excel_file is not None
        positions = [(30, 20), (190, 20), (30, 140), (190, 140)]
        short_names = ["Bar Chart", "Line Chart", "Pie Chart", "Column Chart"]

        for chart_name, short_name, (x, y) in zip(self.CHARTS, short_names, positions):
            card = tk.Frame(
                chart_area,
                bg=self.COLORS["card"] if enabled else "#D7E0DE",
                highlightbackground=self.COLORS["border"],
                highlightthickness=1,
                cursor="hand2" if enabled else "arrow",
            )
            card.place(x=x, y=y, width=120, height=100)

            icon = tk.Label(
                card,
                text=self._chart_icon(chart_name),
                bg=card["bg"],
                fg=self.COLORS["success"] if enabled else "#8A9894",
                font=("Arial", 27, "bold"),
            )
            icon.pack(pady=(7, 1))
            label = tk.Label(
                card,
                text=short_name,
                bg=card["bg"],
                fg="#8B0000" if enabled else "#6B7472",
                font=("Arial", 8, "bold"),
                wraplength=105,
                justify="center",
            )
            label.pack()

            if enabled:
                for widget in (card, icon, label):
                    widget.bind("<Button-1>", lambda _e, c=chart_name: self.show_chart_page(c))

        if not enabled:
            tk.Label(
                right,
                text="Upload an Excel file to unlock the chart options.",
                bg=self.COLORS["panel_right"],
                fg=self.COLORS["danger"],
                font=("Arial", 9, "bold"),
            ).place(x=79, y=323)

        self._add_footer(canvas)

    def _chart_icon(self, chart_name: str) -> str:
        return {
            "Bar Chart": "▰",
            "Line Chart": "↗",
            "Pie Chart": "◕",
            "Column Chart": "▥",
        }.get(chart_name, "●")

    def upload_excel_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Excel sales file",
            filetypes=[("Excel workbooks", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            excel = pd.ExcelFile(path)
            if not excel.sheet_names:
                raise ValueError("The workbook does not contain any worksheets.")
            self.excel_path = path
            self.excel_file = excel
            self.current_df = None
            messagebox.showinfo(
                "Workbook loaded",
                f"{Path(path).name} was loaded successfully.\n\nSheets found: {len(excel.sheet_names)}",
            )
            self.show_dashboard()
        except Exception as exc:
            self.excel_path = None
            self.excel_file = None
            messagebox.showerror(
                "Unable to open workbook",
                "The Excel file could not be opened. Make sure it is a valid .xlsx or .xls file.\n\n"
                f"Details: {exc}",
            )

    # ------------------------------------------------------------------
    # Chart page
    # ------------------------------------------------------------------
    def show_chart_page(self, chart_name: str) -> None:
        if self.excel_file is None:
            messagebox.showwarning("Excel file required", "Upload an Excel file first.")
            return

        self.current_chart_name = chart_name
        self._clear()
        canvas = self._background_canvas()

        container = tk.Frame(self.main_frame, bg=self.COLORS["panel_right"])
        container.place(x=27, y=20, width=666, height=377)
        left = tk.Frame(container, bg=self.COLORS["panel_left"])
        left.place(x=0, y=0, width=292, height=377)
        right = tk.Frame(container, bg=self.COLORS["panel_right"])
        right.place(x=292, y=0, width=374, height=377)

        self._add_branding(left, compact=True)

        tk.Label(
            right,
            text="Select Analysis",
            bg=self.COLORS["panel_right"],
            fg=self.COLORS["muted"],
            font=("Arial", 8, "bold"),
        ).place(x=22, y=10)

        self.chart_type_var = tk.StringVar(value=chart_name)
        chart_combo = ttk.Combobox(
            right,
            textvariable=self.chart_type_var,
            values=self.CHARTS,
            state="readonly",
            style="Avix.TCombobox",
            font=("Arial", 12, "bold"),
        )
        chart_combo.place(x=20, y=30, width=330)
        chart_combo.bind("<<ComboboxSelected>>", self._change_chart_type)

        controls = tk.Frame(left, bg=self.COLORS["panel_left"])
        controls.place(x=18, y=62, width=256, height=257)

        self.sheet_var = tk.StringVar(value=self.excel_file.sheet_names[0])
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.date_var = tk.StringVar(value="None")
        self.aggregation_var = tk.StringVar(value="Sum")
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        row_y = 4
        row_y = self._add_combo_row(controls, "Sheet", self.sheet_var, self.excel_file.sheet_names, row_y)
        self.x_combo = self._add_combo_row(controls, "X axis", self.x_var, [], row_y, return_widget=True)
        row_y += 34
        self.y_combo = self._add_combo_row(controls, "Y axis", self.y_var, [], row_y, return_widget=True)
        row_y += 34
        self.date_combo = self._add_combo_row(controls, "Date column", self.date_var, ["None"], row_y, return_widget=True)
        row_y += 34
        row_y = self._add_combo_row(
            controls,
            "Aggregation",
            self.aggregation_var,
            ["Sum", "Average", "Count", "Minimum", "Maximum"],
            row_y,
        )

        tk.Label(
            controls,
            text="Date range",
            bg=self.COLORS["panel_left"],
            fg=self.COLORS["text"],
            font=("Arial", 9, "bold"),
        ).place(x=0, y=row_y + 3)
        tk.Entry(
            controls,
            textvariable=self.start_date_var,
            bd=0,
            font=("Arial", 8),
        ).place(x=87, y=row_y, width=76, height=24)
        tk.Entry(
            controls,
            textvariable=self.end_date_var,
            bd=0,
            font=("Arial", 8),
        ).place(x=169, y=row_y, width=76, height=24)
        tk.Label(
            controls,
            text="YYYY-MM-DD        YYYY-MM-DD",
            bg=self.COLORS["panel_left"],
            fg=self.COLORS["muted"],
            font=("Arial", 6),
        ).place(x=87, y=row_y + 25)

        sheet_combo = controls.winfo_children()[1]
        if isinstance(sheet_combo, ttk.Combobox):
            sheet_combo.bind("<<ComboboxSelected>>", self._load_selected_sheet)

        self._button(
            left,
            "Generate",
            self.generate_chart,
            self.COLORS["primary"],
            self.COLORS["primary_hover"],
            width=11,
            font=("Arial", 10, "bold"),
        ).place(x=165, y=323)

        self._button(
            left,
            "Dashboard",
            self.show_dashboard,
            self.COLORS["danger"],
            self.COLORS["danger_hover"],
            width=12,
        ).place(x=20, y=323)

        self.chart_holder = tk.Frame(
            right,
            bg="#E7E7E7",
            highlightbackground="#222222",
            highlightthickness=1,
        )
        self.chart_holder.place(x=20, y=75, width=330, height=250)

        self.placeholder_label = tk.Label(
            self.chart_holder,
            text="Choose the worksheet and columns,\nthen click Generate.",
            bg="#E7E7E7",
            fg=self.COLORS["muted"],
            font=("Arial", 11, "bold"),
            justify="center",
        )
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        self.download_button = self._button(
            right,
            "Download PDF",
            self.export_pdf_report,
            "#9B5DE5",
            "#7C3AED",
            width=13,
            state="disabled",
        )
        self.download_button.place(x=224, y=335)

        self.status_var = tk.StringVar(value=f"Workbook: {Path(self.excel_path).name}")
        tk.Label(
            right,
            textvariable=self.status_var,
            bg=self.COLORS["panel_right"],
            fg=self.COLORS["muted"],
            font=("Arial", 8),
            anchor="w",
        ).place(x=20, y=340, width=195)

        self._load_selected_sheet()
        self._add_footer(canvas)

    def _add_combo_row(
        self,
        parent,
        label_text: str,
        variable: tk.StringVar,
        values,
        y: int,
        return_widget: bool = False,
    ):
        tk.Label(
            parent,
            text=label_text,
            bg=self.COLORS["panel_left"],
            fg=self.COLORS["text"],
            font=("Arial", 9, "bold"),
        ).place(x=0, y=y + 4)
        combo = ttk.Combobox(
            parent,
            textvariable=variable,
            values=list(values),
            state="readonly",
            style="Avix.TCombobox",
            font=("Arial", 8),
        )
        combo.place(x=87, y=y, width=158, height=26)
        if values and not variable.get():
            variable.set(list(values)[0])
        return combo if return_widget else y + 34

    def _change_chart_type(self, _event=None) -> None:
        self.current_chart_name = self.chart_type_var.get()
        self.current_figure = None
        self.download_button.config(state="disabled", cursor="arrow")
        self.status_var.set("Analysis changed. Click Generate to refresh the chart.")

    def _load_selected_sheet(self, _event=None) -> None:
        try:
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_var.get())
            df.columns = [str(column).strip() for column in df.columns]
            df = df.dropna(how="all")
            if df.empty:
                raise ValueError("The selected worksheet is empty.")
            self.current_df = df

            columns = list(df.columns)
            numeric_columns = [column for column in columns if pd.api.types.is_numeric_dtype(df[column])]
            date_candidates = [column for column in columns if self._looks_like_date_column(df[column], column)]

            self.x_combo["values"] = columns
            self.y_combo["values"] = numeric_columns or columns
            self.date_combo["values"] = ["None"] + date_candidates

            self.x_var.set(self._best_x_column(columns))
            self.y_var.set(self._best_y_column(numeric_columns, columns))
            self.date_var.set(date_candidates[0] if date_candidates else "None")

            self.status_var.set(f"Loaded {len(df):,} rows from {self.sheet_var.get()}")
        except Exception as exc:
            self.current_df = None
            messagebox.showerror("Worksheet error", f"The selected worksheet could not be loaded.\n\n{exc}")

    def _looks_like_date_column(self, series: pd.Series, name: str) -> bool:
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        if any(keyword in name.lower() for keyword in ("date", "month", "day", "time")):
            parsed = pd.to_datetime(series, errors="coerce")
            return parsed.notna().mean() >= 0.5
        return False

    def _best_x_column(self, columns: list[str]) -> str:
        if self.current_chart_name == "Line Chart":
            priorities = ["date", "month", "time", "day"]
        elif self.current_chart_name == "Pie Chart":
            priorities = ["category", "type", "segment", "product", "item"]
        else:
            priorities = ["product", "item", "model", "category", "name"]
        return self._find_column(columns, priorities) or columns[0]

    def _best_y_column(self, numeric: list[str], all_columns: list[str]) -> str:
        pool = numeric or all_columns
        priorities = ["sales amount", "revenue", "sales", "profit", "amount", "total", "quantity", "qty"]
        return self._find_column(pool, priorities) or pool[0]

    @staticmethod
    def _find_column(columns, keywords) -> Optional[str]:
        normalized = {column: column.lower().strip().replace("_", " ") for column in columns}
        for keyword in keywords:
            for column, lower in normalized.items():
                if keyword == lower or keyword in lower:
                    return column
        return None

    # ------------------------------------------------------------------
    # Data preparation and chart generation
    # ------------------------------------------------------------------
    def generate_chart(self) -> None:
        if self.current_df is None:
            messagebox.showwarning("No worksheet", "Select a valid worksheet first.")
            return

        try:
            chart_name = self.chart_type_var.get()
            x_column = self.x_var.get()
            y_column = self.y_var.get()
            date_column = self.date_var.get()

            if not x_column or not y_column:
                raise ValueError("Select both X-axis and Y-axis columns.")
            if x_column not in self.current_df.columns or y_column not in self.current_df.columns:
                raise ValueError("One of the selected columns is not available in the worksheet.")

            df = self.current_df.copy()
            df = self._apply_date_filter(df, date_column)
            if df.empty:
                raise ValueError("No records remain after applying the selected date range.")

            figure = Figure(figsize=(5.2, 3.8), dpi=100, facecolor="#E7E7E7")
            axis = figure.add_subplot(111)
            axis.set_facecolor("#F8FAFA")

            if chart_name == "Bar Chart":
                summary = self._plot_bar(axis, df, x_column, y_column)
            elif chart_name == "Line Chart":
                summary = self._plot_line(axis, df, x_column, y_column)
            elif chart_name == "Pie Chart":
                summary = self._plot_pie(axis, df, x_column, y_column)
            elif chart_name == "Column Chart":
                summary = self._plot_column(axis, df, x_column, y_column)
            else:
                raise ValueError("Unsupported chart type.")

            figure.tight_layout(pad=1.4)
            self._display_figure(figure)
            self.current_figure = figure
            self.current_chart_name = chart_name
            self.last_summary = summary
            self.download_button.config(state="normal", cursor="hand2")
            self.status_var.set(summary)
        except Exception as exc:
            messagebox.showerror("Chart generation failed", str(exc))

    def _apply_date_filter(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        if not date_column or date_column == "None":
            return df

        if date_column not in df.columns:
            raise ValueError("The selected date column does not exist.")

        parsed = pd.to_datetime(df[date_column], errors="coerce")
        df = df.loc[parsed.notna()].copy()
        df[date_column] = parsed[parsed.notna()]

        start_text = self.start_date_var.get().strip()
        end_text = self.end_date_var.get().strip()

        if start_text:
            try:
                start = pd.to_datetime(start_text)
            except Exception as exc:
                raise ValueError("Start date must use YYYY-MM-DD format.") from exc
            df = df[df[date_column] >= start]

        if end_text:
            try:
                end = pd.to_datetime(end_text)
            except Exception as exc:
                raise ValueError("End date must use YYYY-MM-DD format.") from exc
            df = df[df[date_column] <= end]

        return df

    def _aggregate(self, df: pd.DataFrame, x_column: str, y_column: str) -> pd.Series:
        operation = self.aggregation_var.get()
        data = df[[x_column, y_column]].copy()
        data[x_column] = data[x_column].astype(str).replace("nan", "Unknown")
        data[y_column] = pd.to_numeric(data[y_column], errors="coerce")
        data = data.dropna(subset=[y_column])
        if data.empty:
            raise ValueError(f"'{y_column}' does not contain usable numeric values.")

        grouped = data.groupby(x_column)[y_column]
        if operation == "Average":
            return grouped.mean()
        if operation == "Count":
            return grouped.count()
        if operation == "Minimum":
            return grouped.min()
        if operation == "Maximum":
            return grouped.max()
        return grouped.sum()

    def _plot_bar(self, axis, df, x_column, y_column) -> str:
        grouped = self._aggregate(df, x_column, y_column).sort_values(ascending=False).head(10)
        axis.barh(grouped.index[::-1], grouped.values[::-1])
        axis.set_title(f"{self.aggregation_var.get()} of {y_column} by {x_column}", fontsize=11, fontweight="bold")
        axis.set_xlabel(f"{self.aggregation_var.get()} of {y_column}")
        axis.set_ylabel(x_column)
        axis.grid(axis="x", alpha=0.25)
        return f"Highest value: {grouped.index[0]} ({grouped.iloc[0]:,.2f})."

    def _plot_column(self, axis, df, x_column, y_column) -> str:
        grouped = self._aggregate(df, x_column, y_column).sort_values(ascending=False).head(10)
        axis.bar(grouped.index, grouped.values)
        axis.set_title(f"{self.aggregation_var.get()} of {y_column} by {x_column}", fontsize=11, fontweight="bold")
        axis.set_xlabel(x_column)
        axis.set_ylabel(f"{self.aggregation_var.get()} of {y_column}")
        axis.tick_params(axis="x", rotation=35)
        axis.grid(axis="y", alpha=0.25)
        return f"Highest value: {grouped.index[0]} ({grouped.iloc[0]:,.2f})."

    def _plot_line(self, axis, df, x_column, y_column) -> str:
        work = df[[x_column, y_column]].copy()
        work[y_column] = pd.to_numeric(work[y_column], errors="coerce")
        parsed_dates = pd.to_datetime(work[x_column], errors="coerce")

        if parsed_dates.notna().mean() >= 0.6:
            work["__x__"] = parsed_dates
            work = work.dropna(subset=["__x__", y_column])
            grouped = work.groupby("__x__")[y_column]
            operation = self.aggregation_var.get()
            if operation == "Average":
                series = grouped.mean()
            elif operation == "Count":
                series = grouped.count()
            elif operation == "Minimum":
                series = grouped.min()
            elif operation == "Maximum":
                series = grouped.max()
            else:
                series = grouped.sum()
            series = series.sort_index()
        else:
            series = self._aggregate(df, x_column, y_column)

        if series.empty:
            raise ValueError("No valid values were found for the line chart.")
        axis.plot(series.index, series.values, marker="o", linewidth=2.2)
        axis.set_title(f"{y_column} trend by {x_column}", fontsize=11, fontweight="bold")
        axis.set_xlabel(x_column)
        axis.set_ylabel(f"{self.aggregation_var.get()} of {y_column}")
        axis.tick_params(axis="x", rotation=35)
        axis.grid(alpha=0.25)
        return f"Line chart generated with {len(series):,} data points."

    def _plot_pie(self, axis, df, x_column, y_column) -> str:
        grouped = self._aggregate(df, x_column, y_column).sort_values(ascending=False)
        grouped = grouped[grouped > 0]
        if grouped.empty:
            raise ValueError("Pie charts require positive numeric values.")
        if len(grouped) > 6:
            top = grouped.head(5)
            grouped = pd.concat([top, pd.Series({"Other": grouped.iloc[5:].sum()})])
        axis.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%", startangle=90)
        axis.set_title(f"Share of {y_column} by {x_column}", fontsize=11, fontweight="bold")
        return f"Largest share: {grouped.idxmax()} ({grouped.max():,.2f})."

    def _display_figure(self, figure: Figure) -> None:
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
        if hasattr(self, "placeholder_label") and self.placeholder_label.winfo_exists():
            self.placeholder_label.destroy()

        self.chart_canvas = FigureCanvasTkAgg(figure, master=self.chart_holder)
        self.chart_canvas.draw()
        widget = self.chart_canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # PDF report export
    # ------------------------------------------------------------------
    def export_pdf_report(self) -> None:
        if self.current_figure is None:
            messagebox.showwarning("Generate a chart", "Generate a chart before downloading the report.")
            return
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(
                "Missing dependency",
                "PDF export requires ReportLab. Install it with:\n\npip install reportlab",
            )
            return

        default_name = f"Avix_{self.current_chart_name.replace(' ', '_')}_Report.pdf"
        save_path = filedialog.asksaveasfilename(
            title="Save PDF report",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF document", "*.pdf")],
        )
        if not save_path:
            return

        temp_chart = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                temp_chart = temp.name
            self.current_figure.savefig(temp_chart, dpi=180, bbox_inches="tight", facecolor="white")

            document = SimpleDocTemplate(
                save_path,
                pagesize=A4,
                rightMargin=18 * mm,
                leftMargin=18 * mm,
                topMargin=16 * mm,
                bottomMargin=16 * mm,
                title=f"Avix Mobile - {self.current_chart_name}",
                author="Avix Mobile LK",
            )
            styles = getSampleStyleSheet()
            story = [
                Paragraph("Avix Mobile LK", styles["Title"]),
                Paragraph("Business Sales Analysis Report", styles["Heading2"]),
                Spacer(1, 6 * mm),
            ]

            details = [
                ["Analysis", self.current_chart_name],
                ["Source workbook", Path(self.excel_path).name if self.excel_path else "Not available"],
                ["Worksheet", self.sheet_var.get()],
                ["X-axis", self.x_var.get()],
                ["Y-axis", self.y_var.get()],
                ["Aggregation", self.aggregation_var.get()],
                ["Date range", self._date_range_text()],
            ]
            table = Table(details, colWidths=[43 * mm, 115 * mm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#91D9C0")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#15372B")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#75AFAE")),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#F5FBFA")]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.extend(
                [
                    table,
                    Spacer(1, 7 * mm),
                    Paragraph("Generated Chart", styles["Heading2"]),
                    Spacer(1, 3 * mm),
                    RLImage(temp_chart, width=170 * mm, height=102 * mm),
                    Spacer(1, 6 * mm),
                    Paragraph("Key Insight", styles["Heading2"]),
                    Paragraph(getattr(self, "last_summary", "Chart generated successfully."), styles["BodyText"]),
                    Spacer(1, 6 * mm),
                    Paragraph(
                        "This report was generated from the uploaded Excel workbook to support business analysis and decision-making.",
                        styles["BodyText"],
                    ),
                ]
            )
            document.build(story)
            messagebox.showinfo("PDF created", f"The report was saved successfully:\n\n{save_path}")
        except Exception as exc:
            messagebox.showerror("PDF export failed", f"The report could not be created.\n\n{exc}")
        finally:
            if temp_chart and os.path.exists(temp_chart):
                try:
                    os.remove(temp_chart)
                except OSError:
                    pass

    def _date_range_text(self) -> str:
        start = self.start_date_var.get().strip() or "Beginning"
        end = self.end_date_var.get().strip() or "Latest"
        return f"{start} to {end}"
