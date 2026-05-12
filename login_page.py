import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class LoginPage:
    def __init__(self, root, go_back, go_to_dashboard=None):
        self.root = root
        self.go_back = go_back
        self.go_to_dashboard = go_to_dashboard

        self.width = 720
        self.height = 480

        self.CORRECT_USERNAME = "klmc12"
        self.CORRECT_PASSWORD = "klmc@12"

        self.LOGIN_LEFT = "#91D9C0"
        self.LOGIN_RIGHT = "#BFE9EA"
        self.LOGIN_BUTTON = "#80BCA6"
        self.LOGIN_BUTTON_BORDER = "#4F8D7B"
        self.FOOTER_WHITE = "#FFFFFF"

        self.bg_image = None
        self.logo_image = None
        self.username_entry = None
        self.password_entry = None
        self.error_text_id = None
        self.back_btn = None

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

    def draw_back_button(self):
        self.back_btn = tk.Button(
            self.root,
            text="← BACK",
            font=("Arial", 10, "bold"),
            bg="#8B0000",
            fg="white",
            activebackground="#B30000",
            activeforeground="white",
            bd=2,
            relief="raised",
            cursor="hand2",
            command=self.go_back
        )

        self.canvas.create_window(
            67, 425,
            width=95,
            height=34,
            window=self.back_btn
        )

    def draw_login_button(self):
        # 3D shadow
        login_shadow = self.rounded_rectangle(
            self.canvas,
            529, 337, 636, 373,
            radius=7,
            fill="#4F8D7B",
            outline=""
        )

        # Main button body
        login_fill = self.rounded_rectangle(
            self.canvas,
            526, 332, 633, 368,
            radius=7,
            fill=self.LOGIN_BUTTON,
            outline=self.LOGIN_BUTTON_BORDER,
            width=2
        )

        # Inner button area
        login_inner = self.rounded_rectangle(
            self.canvas,
            532, 338, 627, 365,
            radius=6,
            fill=self.LOGIN_BUTTON,
            outline=""
        )

        # Top glossy highlight
        login_highlight = self.rounded_rectangle(
            self.canvas,
            536, 337, 623, 348,
            radius=5,
            fill="#9DD1BE",
            outline=""
        )

        # Text shadow
        login_text_shadow = self.canvas.create_text(
            582, 352,
            text="Login",
            font=("Arial", 11, "bold"),
            fill="#3F6F63"
        )

        # Main text
        login_text = self.canvas.create_text(
            580, 350,
            text="Login",
            font=("Arial", 11, "bold"),
            fill="white"
        )

        for item in [
            login_shadow,
            login_fill,
            login_inner,
            login_highlight,
            login_text_shadow,
            login_text
        ]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.check_login())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.error_text_id is not None:
            self.canvas.delete(self.error_text_id)

        if username == self.CORRECT_USERNAME and password == self.CORRECT_PASSWORD:
            if self.go_to_dashboard:
                self.go_to_dashboard()
            else:
                self.show_success_page()
        else:
            self.error_text_id = self.canvas.create_text(
                505, 378,
                text="*incorrect user name & password.. retry...",
                font=("Roboto Mono", 9, "bold"),
                fill="red",
                anchor="center",
                justify="left"
            )

    def destroy_inputs(self):
        if self.username_entry is not None:
            self.username_entry.destroy()
            self.username_entry = None

        if self.password_entry is not None:
            self.password_entry.destroy()
            self.password_entry = None

        if self.back_btn is not None:
            self.back_btn.destroy()
            self.back_btn = None

    def show_success_page(self):
        self.destroy_inputs()

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.canvas.create_text(
            360, 200,
            text="Login Successful",
            font=("Arial", 32, "bold"),
            fill="white"
        )

        self.canvas.create_text(
            360, 250,
            text="Dashboard page will open here.",
            font=("Arial", 14),
            fill="#DDEEFF"
        )

        self.add_footer()

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

        # Main card shadow
        self.rounded_rectangle(
            self.canvas,
            31, 52, 697, 401,
            radius=28,
            fill="#000000",
            outline=""
        )

        # Left panel
        self.rounded_rectangle(
            self.canvas,
            27, 47, 355, 396,
            radius=28,
            fill=self.LOGIN_LEFT,
            outline=""
        )

        # Right panel
        self.rounded_rectangle(
            self.canvas,
            318, 47, 693, 396,
            radius=28,
            fill=self.LOGIN_RIGHT,
            outline=""
        )

        # Welcome title
        self.canvas.create_text(
            48, 80,
            text="Welcome to Avix.lk",
            font=("Arial", 21, "bold"),
            fill="#5B5A00",
            anchor="w"
        )

        # Underline
        self.canvas.create_line(
            48, 94, 263, 94,
            fill="#5B5A00",
            width=3
        )

        description = (
            "Business Support\n"
            "System. This\n"
            "platform helps\n"
            "users upload Excel\n"
            "data, analyse sales\n"
            "performance,\n"
            "identify trends, and\n"
            "make better\n"
            "business decisions\n"
            "through clear data\n"
            "insights."
        )

        self.canvas.create_text(
            58, 130,
            text=description,
            font=("Arial", 14, "bold"),
            fill="#104225",
            anchor="nw",
            justify="left"
        )

        # Login title shadow
        self.canvas.create_text(
            403, 90,
            text="Login",
            font=("Arial", 30, "bold"),
            fill="#6B6B6B"
        )

        # Login title
        self.canvas.create_text(
            400, 88,
            text="Login",
            font=("Arial", 30, "bold"),
            fill="black"
        )

        # Username label
        self.canvas.create_text(
            505, 142,
            text="User Name",
            font=("Arial", 15, "bold"),
            fill="black"
        )

        # Username entry shadow
        self.rounded_rectangle(
            self.canvas,
            367, 169, 647, 203,
            radius=8,
            fill="#8FA6A8",
            outline=""
        )

        self.username_entry = tk.Entry(
            self.root,
            font=("Arial", 14),
            bg="#E6E6E6",
            fg="black",
            bd=0,
            justify="center"
        )

        self.canvas.create_window(
            506, 182,
            width=276,
            height=32,
            window=self.username_entry
        )

        # Password label
        self.canvas.create_text(
            505, 237,
            text="Password",
            font=("Arial", 15, "bold"),
            fill="black"
        )

        # Password entry shadow
        self.rounded_rectangle(
            self.canvas,
            367, 264, 647, 298,
            radius=8,
            fill="#8FA6A8",
            outline=""
        )

        self.password_entry = tk.Entry(
            self.root,
            font=("Arial", 14),
            bg="#E6E6E6",
            fg="black",
            bd=0,
            justify="center",
            show="*"
        )

        self.canvas.create_window(
            506, 277,
            width=276,
            height=32,
            window=self.password_entry
        )

        # 3D login button
        self.draw_login_button()

        # Logo box bottom-right
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

        # Back button bottom-left
        self.draw_back_button()

        self.add_footer()