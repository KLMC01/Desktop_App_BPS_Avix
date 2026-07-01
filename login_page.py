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

        self.password_visible = False
        self.eye_text_id = None

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

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.config(show="*")
            self.password_visible = False
            self.canvas.itemconfig(self.eye_text_id, text="👁")
        else:
            self.password_entry.config(show="")
            self.password_visible = True
            self.canvas.itemconfig(self.eye_text_id, text="🙈")

    def draw_eye_icon(self):
        eye_bg = self.rounded_rectangle(
            self.canvas,
            610, 266, 642, 296,
            radius=8,
            fill="#D9D9D9",
            outline="#A8A8A8",
            width=1
        )

        self.eye_text_id = self.canvas.create_text(
            626, 281,
            text="👁",
            font=("Arial", 13),
            fill="black"
        )

        for item in [eye_bg, self.eye_text_id]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.toggle_password_visibility())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

    def draw_login_button(self):
        login_shadow = self.rounded_rectangle(
            self.canvas,
            529, 337, 636, 373,
            radius=7,
            fill="#4F8D7B",
            outline=""
        )

        login_fill = self.rounded_rectangle(
            self.canvas,
            526, 332, 633, 368,
            radius=7,
            fill=self.LOGIN_BUTTON,
            outline=self.LOGIN_BUTTON_BORDER,
            width=2
        )

        login_inner = self.rounded_rectangle(
            self.canvas,
            532, 338, 627, 365,
            radius=6,
            fill=self.LOGIN_BUTTON,
            outline=""
        )

        login_highlight = self.rounded_rectangle(
            self.canvas,
            536, 337, 623, 348,
            radius=5,
            fill="#9DD1BE",
            outline=""
        )

        login_text_shadow = self.canvas.create_text(
            582, 352,
            text="Login",
            font=("Arial", 11, "bold"),
            fill="#3F6F63"
        )

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

    def draw_back_button(self):
        back_shadow = self.rounded_rectangle(
            self.canvas,
            30, 418, 135, 454,
            radius=7,
            fill="#3B0000",
            outline=""
        )

        back_fill = self.rounded_rectangle(
            self.canvas,
            27, 413, 132, 449,
            radius=7,
            fill="#8B0000",
            outline="#FF6B6B",
            width=2
        )

        back_inner = self.rounded_rectangle(
            self.canvas,
            33, 419, 126, 446,
            radius=6,
            fill="#8B0000",
            outline=""
        )

        back_highlight = self.rounded_rectangle(
            self.canvas,
            37, 418, 122, 429,
            radius=5,
            fill="#C52B2B",
            outline=""
        )

        back_text_shadow = self.canvas.create_text(
            83, 433,
            text="BACK",
            font=("Arial", 10, "bold"),
            fill="#4A0000"
        )

        back_text = self.canvas.create_text(
            80, 431,
            text="BACK",
            font=("Arial", 10, "bold"),
            fill="white"
        )

        for item in [
            back_shadow,
            back_fill,
            back_inner,
            back_highlight,
            back_text_shadow,
            back_text
        ]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.go_back())
            self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))

    def focus_password(self, event=None):
        """Move keyboard focus from username to password."""
        if self.password_entry is not None:
            self.password_entry.focus_set()
            self.password_entry.icursor(tk.END)
        return "break"

    def submit_login(self, event=None):
        """Submit the login form from the keyboard."""
        self.check_login()
        return "break"

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

        self.rounded_rectangle(
            self.canvas,
            31, 52, 697, 401,
            radius=28,
            fill="#000000",
            outline=""
        )

        self.rounded_rectangle(
            self.canvas,
            27, 47, 355, 396,
            radius=28,
            fill=self.LOGIN_LEFT,
            outline=""
        )

        self.rounded_rectangle(
            self.canvas,
            318, 47, 693, 396,
            radius=28,
            fill=self.LOGIN_RIGHT,
            outline=""
        )

        self.canvas.create_text(
            48, 80,
            text="Welcome to Avix.lk",
            font=("Arial", 21, "bold"),
            fill="#5B5A00",
            anchor="w"
        )

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

        self.canvas.create_text(
            403, 90,
            text="Login",
            font=("Arial", 30, "bold"),
            fill="#6B6B6B"
        )

        self.canvas.create_text(
            400, 88,
            text="Login",
            font=("Arial", 30, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            505, 142,
            text="User Name",
            font=("Arial", 15, "bold"),
            fill="black"
        )

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

        # Press Enter after typing the username to move to Password.
        self.username_entry.bind("<Return>", self.focus_password)
        self.username_entry.bind("<KP_Enter>", self.focus_password)

        self.canvas.create_text(
            505, 237,
            text="Password",
            font=("Arial", 15, "bold"),
            fill="black"
        )

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
            487, 277,
            width=238,
            height=32,
            window=self.password_entry
        )

        # Press Enter after typing the password to run the Login action.
        self.password_entry.bind("<Return>", self.submit_login)
        self.password_entry.bind("<KP_Enter>", self.submit_login)

        # Start with the cursor ready in the username field.
        self.root.after_idle(self.username_entry.focus_set)

        self.draw_eye_icon()

        self.draw_login_button()

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

        self.draw_back_button()

        self.add_footer()