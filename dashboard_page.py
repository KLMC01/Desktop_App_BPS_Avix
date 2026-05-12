import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import os


class DashboardPage:
    def __init__(self, root, go_home):
        self.root = root
        self.go_home = go_home

        self.width = 720
        self.height = 480

        self.TITLE_YELLOW = "#FFF238"
        self.SUBTITLE_GREEN = "#C8F96A"
        self.FOOTER_WHITE = "#FFFFFF"

        self.PANEL_LEFT = "#91D9C0"
        self.PANEL_RIGHT = "#BFE9EA"

        self.UPLOAD_BUTTON = "#80BCA6"
        self.UPLOAD_BUTTON_BORDER = "#4F8D7B"

        self.HOME_BUTTON = "#8B0000"
        self.HOME_BUTTON_BORDER = "#FF6B6B"

        self.bg_image = None
        self.logo_image = None
        self.file_text_id = None

        self.show_page()

    def prepare_dark_background(self):
        bg = Image.open("background.png")
        bg = bg.resize((720, 480))
        bg = bg.convert("RGBA")

        overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
        dark_bg = Image.alpha_composite(bg, overlay)

        return ImageTk.PhotoImage(dark_bg)

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

    def add_footer(self):
        self.canvas.create_text(
            360, 458,
            text="Copyright @ 2026 Avix Mobile LK. All rights reserved.",
            font=("Roboto Mono", 9),
            fill=self.FOOTER_WHITE
        )

    def create_logo_image(self, size=50, radius=10):
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

    def upload_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            file_name = os.path.basename(file_path)

            if self.file_text_id is not None:
                self.canvas.delete(self.file_text_id)

            self.file_text_id = self.canvas.create_text(
                360, 340,
                text=f"Selected file: {file_name}",
                font=("Arial", 12, "bold"),
                fill="#104225"
            )
        else:
            if self.file_text_id is not None:
                self.canvas.delete(self.file_text_id)

            self.file_text_id = self.canvas.create_text(
                360, 340,
                text="No file selected.",
                font=("Arial", 12, "bold"),
                fill="#B00000"
            )

    def draw_upload_button(self):
        upload_shadow = self.rounded_rectangle(
            self.canvas,
            228, 252, 492, 318,
            radius=16,
            fill="#4F8D7B",
            outline=""
        )

        upload_fill = self.rounded_rectangle(
            self.canvas,
            224, 242, 496, 308,
            radius=16,
            fill=self.UPLOAD_BUTTON,
            outline=self.UPLOAD_BUTTON_BORDER,
            width=3
        )

        upload_inner = self.rounded_rectangle(
            self.canvas,
            238, 254, 482, 298,
            radius=12,
            fill=self.UPLOAD_BUTTON,
            outline=""
        )

        upload_highlight = self.rounded_rectangle(
            self.canvas,
            250, 254, 470, 274,
            radius=10,
            fill="#9DD1BE",
            outline=""
        )

        upload_text_shadow = self.canvas.create_text(
            363, 283,
            text="Upload Excel",
            font=("Arial", 19, "bold"),
            fill="#3F6F63"
        )

        upload_text = self.canvas.create_text(
            360, 280,
            text="Upload Excel",
            font=("Arial", 19, "bold"),
            fill="white"
        )

        for item in [
            upload_shadow,
            upload_fill,
            upload_inner,
            upload_highlight,
            upload_text_shadow,
            upload_text
        ]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.upload_excel_file())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

    def draw_home_button(self):
        home_shadow = self.rounded_rectangle(
            self.canvas,
            30, 418, 135, 454,
            radius=7,
            fill="#3B0000",
            outline=""
        )

        home_fill = self.rounded_rectangle(
            self.canvas,
            27, 413, 132, 449,
            radius=7,
            fill=self.HOME_BUTTON,
            outline=self.HOME_BUTTON_BORDER,
            width=2
        )

        home_inner = self.rounded_rectangle(
            self.canvas,
            33, 419, 126, 446,
            radius=6,
            fill=self.HOME_BUTTON,
            outline=""
        )

        home_highlight = self.rounded_rectangle(
            self.canvas,
            37, 418, 122, 429,
            radius=5,
            fill="#C52B2B",
            outline=""
        )

        home_text_shadow = self.canvas.create_text(
            83, 433,
            text="HOME",
            font=("Arial", 10, "bold"),
            fill="#4A0000"
        )

        home_text = self.canvas.create_text(
            80, 431,
            text="HOME",
            font=("Arial", 10, "bold"),
            fill="white"
        )

        for item in [
            home_shadow,
            home_fill,
            home_inner,
            home_highlight,
            home_text_shadow,
            home_text
        ]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.go_home())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

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

        self.rounded_rectangle(
            self.canvas,
            31, 52, 697, 401,
            radius=28,
            fill="#000000",
            outline=""
        )

        self.rounded_rectangle(
            self.canvas,
            27, 47, 693, 396,
            radius=28,
            fill=self.PANEL_RIGHT,
            outline=""
        )

        self.rounded_rectangle(
            self.canvas,
            27, 47, 255, 396,
            radius=28,
            fill=self.PANEL_LEFT,
            outline=""
        )

        self.canvas.create_text(
            50, 82,
            text="Avix LK",
            font=("Arial", 28, "bold"),
            fill="#5B5A00",
            anchor="w"
        )

        self.canvas.create_line(
            50, 102, 180, 102,
            fill="#5B5A00",
            width=3
        )

        self.canvas.create_text(
            50, 130,
            text="Business Support\nDashboard",
            font=("Arial", 18, "bold"),
            fill="#104225",
            anchor="nw",
            justify="left"
        )

        self.canvas.create_text(
            50, 210,
            text="Upload your Excel sales\nfile to begin business\nanalysis and decision\nsupport process.",
            font=("Arial", 12, "bold"),
            fill="#104225",
            anchor="nw",
            justify="left"
        )

        self.canvas.create_text(
            465, 90,
            text="Dashboard",
            font=("Arial", 34, "bold"),
            fill="#6B6B6B"
        )

        self.canvas.create_text(
            462, 86,
            text="Dashboard",
            font=("Arial", 34, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            462, 145,
            text="Excel File Upload",
            font=("Arial", 18, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            462, 180,
            text="Select your business sales Excel file to continue.",
            font=("Arial", 12),
            fill="#104225"
        )

        self.draw_upload_button()

        self.rounded_rectangle(
            self.canvas,
            611, 409, 675, 472,
            radius=10,
            fill="#000000",
            outline="#00D8FF",
            width=2
        )

        small_logo = self.create_logo_image(50, 10)
        self.canvas.create_image(643, 440, image=small_logo, anchor="center")

        self.draw_home_button()

        self.add_footer()