import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw


class WelcomePage:
    def __init__(self, root, go_to_login):
        self.root = root
        self.go_to_login = go_to_login

        self.width = 720
        self.height = 480

        # ---------------- COLORS ----------------
        self.TITLE_YELLOW = "#FFF238"
        self.SUBTITLE_GREEN = "#C8F96A"

        self.BUTTON_BORDER = "#FF8A8A"
        self.BUTTON_MAIN = "#990000"
        self.BUTTON_INNER = "#B30000"
        self.BUTTON_HIGHLIGHT = "#D42A2A"
        self.BUTTON_SHADOW = "#2A0000"
        self.TEXT_SHADOW = "#5A0000"
        self.BUTTON_TEXT = "#FFFFFF"

        self.PROGRESS_BLUE = "#6D84FF"
        self.PROGRESS_BG = "#D7F1F2"
        self.FOOTER_WHITE = "#FFFFFF"

        self.button_disabled = False
        self.progress = None
        self.progress_label = None
        self.bg_image = None
        self.logo_image = None

        self.setup_progress_style()
        self.show_page()

    # ---------------- BACKGROUND PREP ----------------
    def prepare_dark_background(self):
        bg = Image.open("background.png")
        bg = bg.resize((720, 480))
        bg = bg.convert("RGBA")

        overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
        dark_bg = Image.alpha_composite(bg, overlay)

        return ImageTk.PhotoImage(dark_bg)

    # ---------------- ROUNDED RECTANGLE FUNCTION ----------------
    def rounded_rectangle(self, canvas_obj, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas_obj.create_polygon(points, smooth=True, **kwargs)

    # ---------------- FOOTER ----------------
    def add_footer(self, canvas_obj):
        canvas_obj.create_text(
            360, 455,
            text="Copyright @ 2026 Avix Mobile LK. All rights reserved.",
            font=("Roboto Mono", 9),
            fill=self.FOOTER_WHITE
        )

    # ---------------- LOGO IMAGE ----------------
    def create_logo_image(self, size=72, radius=16):
        logo = Image.open("logo.jpg")
        logo = logo.resize((size, size))
        logo = logo.convert("RGBA")

        mask = Image.new("L", logo.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)

        rounded_logo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        rounded_logo.paste(logo, (0, 0), mask)

        self.logo_image = ImageTk.PhotoImage(rounded_logo)
        return self.logo_image

    # ---------------- LOGO DRAW ----------------
    def draw_logo(self, canvas_obj):
        self.rounded_rectangle(
            canvas_obj,
            55, 43, 145, 130,
            radius=18,
            fill="#000000",
            outline=""
        )

        self.rounded_rectangle(
            canvas_obj,
            50, 38, 140, 125,
            radius=18,
            fill="#111827",
            outline="#00D8FF",
            width=2
        )

        logo = self.create_logo_image(72, 16)
        canvas_obj.create_image(95, 82, image=logo, anchor="center")

    # ---------------- PROGRESS BAR STYLE ----------------
    def setup_progress_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Avix.Horizontal.TProgressbar",
            troughcolor=self.PROGRESS_BG,
            background=self.PROGRESS_BLUE,
            bordercolor=self.PROGRESS_BG,
            lightcolor=self.PROGRESS_BLUE,
            darkcolor=self.PROGRESS_BLUE
        )

    # ---------------- LOADING FUNCTION ----------------
    def start_loading(self):
        if self.button_disabled:
            return

        self.button_disabled = True

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=305,
            mode="determinate",
            style="Avix.Horizontal.TProgressbar"
        )

        self.progress_label = tk.Label(
            self.root,
            text="0%",
            font=("Arial", 11, "bold"),
            bg="#06101E",
            fg="white"
        )

        self.canvas.create_window(360, 375, window=self.progress)
        self.canvas.create_window(555, 375, window=self.progress_label)

        self.load_progress(0)

    def load_progress(self, value):
        self.progress["value"] = value
        self.progress_label.config(text=f"{value}%")

        if value < 100:
            self.root.after(40, self.load_progress, value + 1)
        else:
            self.root.after(300, self.open_login_page)

    def open_login_page(self):
        if self.progress is not None:
            self.progress.destroy()

        if self.progress_label is not None:
            self.progress_label.destroy()

        self.go_to_login()

    # ---------------- WELCOME PAGE ----------------
    def show_page(self):
        self.bg_image = self.prepare_dark_background()

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.draw_logo(self.canvas)

        self.canvas.create_text(
            360, 85,
            text="Avix LK",
            font=("Ubuntu", 48, "bold"),
            fill=self.TITLE_YELLOW
        )

        self.canvas.create_text(
            360, 130,
            text="Business Support System",
            font=("Arial", 14, "bold"),
            fill=self.SUBTITLE_GREEN
        )

        # ---------------- 3D ENTER BUTTON ----------------
        button_shadow = self.rounded_rectangle(
            self.canvas,
            184, 242, 536, 330,
            radius=18,
            fill=self.BUTTON_SHADOW,
            outline=""
        )

        button_fill = self.rounded_rectangle(
            self.canvas,
            180, 230, 540, 318,
            radius=18,
            fill=self.BUTTON_MAIN,
            outline=self.BUTTON_BORDER,
            width=3
        )

        button_inner = self.rounded_rectangle(
            self.canvas,
            195, 242, 525, 304,
            radius=14,
            fill=self.BUTTON_INNER,
            outline=""
        )

        button_highlight = self.rounded_rectangle(
            self.canvas,
            205, 244, 515, 272,
            radius=13,
            fill=self.BUTTON_HIGHLIGHT,
            outline=""
        )

        button_text_shadow = self.canvas.create_text(
            363, 280,
            text="ENTER",
            font=("Arial", 38, "bold"),
            fill=self.TEXT_SHADOW
        )

        button_text = self.canvas.create_text(
            360, 275,
            text="ENTER",
            font=("Arial", 38, "bold"),
            fill=self.BUTTON_TEXT
        )

        for item in [
            button_shadow,
            button_fill,
            button_inner,
            button_highlight,
            button_text_shadow,
            button_text
        ]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.start_loading())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

        self.add_footer(self.canvas)