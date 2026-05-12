import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

window = tk.Tk()
window.title("Avix Mobile")
window.geometry("720x480")
window.resizable(False, False)

# ---------------- COLORS ----------------
TITLE_YELLOW = "#FFF238"
SUBTITLE_GREEN = "#C8F96A"
BUTTON_BORDER = "#FF8A8A"
BUTTON_MAIN = "#990000"
BUTTON_INNER = "#B30000"
BUTTON_HIGHLIGHT = "#D42A2A"
BUTTON_SHADOW = "#2A0000"
TEXT_SHADOW = "#5A0000"
BUTTON_TEXT = "#FFFFFF"
PROGRESS_BLUE = "#6D84FF"
PROGRESS_BG = "#D7F1F2"
FOOTER_WHITE = "#FFFFFF"

BACK_BUTTON_MAIN = "#B30000"
BACK_BUTTON_HIGHLIGHT = "#D42A2A"
BACK_BUTTON_SHADOW = "#2A0000"
BACK_BUTTON_BORDER = "#FF8A8A"

button_disabled = False
progress = None
progress_label = None
canvas = None
bg_image = None
logo_image = None


# ---------------- BACKGROUND PREP ----------------
def prepare_dark_background():
    bg = Image.open("background.png")
    bg = bg.resize((720, 480))
    bg = bg.convert("RGBA")

    overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
    dark_bg = Image.alpha_composite(bg, overlay)

    return ImageTk.PhotoImage(dark_bg)


# ---------------- ROUNDED RECTANGLE FUNCTION ----------------
def rounded_rectangle(canvas_obj, x1, y1, x2, y2, radius=25, **kwargs):
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
def add_footer(canvas_obj):
    canvas_obj.create_text(
        360, 455,
        text="Copyright @ 2026 Avix Mobile LK. All rights reserved.",
        font=("Roboto Mono", 9),
        fill=FOOTER_WHITE
    )


# ---------------- LOGO DRAW ----------------
def draw_logo(canvas_obj):
    global logo_image

    rounded_rectangle(
        canvas_obj,
        55, 43, 145, 130,
        radius=18,
        fill="#000000",
        outline=""
    )

    rounded_rectangle(
        canvas_obj,
        50, 38, 140, 125,
        radius=18,
        fill="#111827",
        outline="#00D8FF",
        width=2
    )

    logo = Image.open("logo.jpg")
    logo = logo.resize((72, 72))
    logo = logo.convert("RGBA")

    mask = Image.new("L", logo.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, 72, 72), radius=16, fill=255)

    rounded_logo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    rounded_logo.paste(logo, (0, 0), mask)

    logo_image = ImageTk.PhotoImage(rounded_logo)

    canvas_obj.create_image(95, 82, image=logo_image, anchor="center")


# ---------------- PROGRESS BAR STYLE ----------------
def setup_progress_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Avix.Horizontal.TProgressbar",
        troughcolor=PROGRESS_BG,
        background=PROGRESS_BLUE,
        bordercolor=PROGRESS_BG,
        lightcolor=PROGRESS_BLUE,
        darkcolor=PROGRESS_BLUE
    )


# ---------------- BACK BUTTON ----------------
def draw_back_button(canvas_obj):
    back_shadow = rounded_rectangle(
        canvas_obj,
        35, 405, 155, 452,
        radius=12,
        fill=BACK_BUTTON_SHADOW,
        outline=""
    )

    back_fill = rounded_rectangle(
        canvas_obj,
        32, 398, 152, 445,
        radius=12,
        fill=BACK_BUTTON_MAIN,
        outline=BACK_BUTTON_BORDER,
        width=2
    )

    back_highlight = rounded_rectangle(
        canvas_obj,
        43, 405, 141, 420,
        radius=8,
        fill=BACK_BUTTON_HIGHLIGHT,
        outline=""
    )

    back_text_shadow = canvas_obj.create_text(
        94, 426,
        text="BACK",
        font=("Arial", 15, "bold"),
        fill="#5A0000"
    )

    back_text = canvas_obj.create_text(
        92, 423,
        text="BACK",
        font=("Arial", 15, "bold"),
        fill="white"
    )

    for item in [back_shadow, back_fill, back_highlight, back_text_shadow, back_text]:
        canvas_obj.tag_bind(item, "<Button-1>", lambda event: show_welcome_page())
        canvas_obj.tag_bind(item, "<Enter>", lambda event: canvas_obj.config(cursor="hand2"))
        canvas_obj.tag_bind(item, "<Leave>", lambda event: canvas_obj.config(cursor=""))


# ---------------- LOGIN PAGE PLACEHOLDER ----------------
def show_login_page():
    global canvas, bg_image, button_disabled, progress, progress_label

    button_disabled = False

    if progress is not None:
        progress.destroy()

    if progress_label is not None:
        progress_label.destroy()

    canvas.delete("all")
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    canvas.create_text(
        360, 70,
        text="Avix LK",
        font=("Ubuntu", 42, "bold"),
        fill=TITLE_YELLOW
    )

    canvas.create_text(
        360, 112,
        text="Business Support System",
        font=("Arial", 14, "bold"),
        fill=SUBTITLE_GREEN
    )

    canvas.create_text(
        360, 190,
        text="Login Page",
        font=("Arial", 28, "bold"),
        fill="white"
    )

    canvas.create_text(
        360, 235,
        text="Your login UI design will be added here.",
        font=("Arial", 13),
        fill="#DDEEFF"
    )

    canvas.create_text(
        360, 265,
        text="After this, user can enter username and password to access the system.",
        font=("Arial", 11),
        fill="#DDEEFF"
    )

    draw_back_button(canvas)
    add_footer(canvas)


# ---------------- LOADING FUNCTION ----------------
def start_loading():
    global button_disabled, progress, progress_label

    if button_disabled:
        return

    button_disabled = True

    progress = ttk.Progressbar(
        window,
        orient="horizontal",
        length=305,
        mode="determinate",
        style="Avix.Horizontal.TProgressbar"
    )

    progress_label = tk.Label(
        window,
        text="0%",
        font=("Arial", 11, "bold"),
        bg="#06101E",
        fg="white"
    )

    canvas.create_window(360, 375, window=progress)
    canvas.create_window(555, 375, window=progress_label)

    load_progress(0)


def load_progress(value):
    progress["value"] = value
    progress_label.config(text=f"{value}%")

    if value < 100:
        window.after(40, load_progress, value + 1)
    else:
        window.after(300, show_login_page)


# ---------------- WELCOME PAGE ----------------
def show_welcome_page():
    global canvas, bg_image, button_disabled, progress, progress_label

    button_disabled = False

    if progress is not None:
        progress.destroy()

    if progress_label is not None:
        progress_label.destroy()

    if canvas is None:
        bg_image = prepare_dark_background()

        canvas = tk.Canvas(window, width=720, height=480, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
    else:
        canvas.delete("all")

    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    draw_logo(canvas)

    canvas.create_text(
        360, 85,
        text="Avix LK",
        font=("Ubuntu", 48, "bold"),
        fill=TITLE_YELLOW
    )

    canvas.create_text(
        360, 130,
        text="Business Support System",
        font=("Arial", 14, "bold"),
        fill=SUBTITLE_GREEN
    )

    # ---------------- 3D ENTER BUTTON ----------------
    button_shadow = rounded_rectangle(
        canvas,
        184, 242, 536, 330,
        radius=18,
        fill=BUTTON_SHADOW,
        outline=""
    )

    button_fill = rounded_rectangle(
        canvas,
        180, 230, 540, 318,
        radius=18,
        fill=BUTTON_MAIN,
        outline=BUTTON_BORDER,
        width=3
    )

    button_inner = rounded_rectangle(
        canvas,
        195, 242, 525, 304,
        radius=14,
        fill=BUTTON_INNER,
        outline=""
    )

    button_highlight = rounded_rectangle(
        canvas,
        205, 244, 515, 272,
        radius=13,
        fill=BUTTON_HIGHLIGHT,
        outline=""
    )

    button_text_shadow = canvas.create_text(
        363, 280,
        text="ENTER",
        font=("Arial", 38, "bold"),
        fill=TEXT_SHADOW
    )

    button_text = canvas.create_text(
        360, 275,
        text="ENTER",
        font=("Arial", 38, "bold"),
        fill=BUTTON_TEXT
    )

    for item in [button_shadow, button_fill, button_inner, button_highlight, button_text_shadow, button_text]:
        canvas.tag_bind(item, "<Button-1>", lambda event: start_loading())
        canvas.tag_bind(item, "<Enter>", lambda event: canvas.config(cursor="hand2"))
        canvas.tag_bind(item, "<Leave>", lambda event: canvas.config(cursor=""))

    add_footer(canvas)


# ---------------- RUN ----------------
setup_progress_style()
show_welcome_page()
window.mainloop()