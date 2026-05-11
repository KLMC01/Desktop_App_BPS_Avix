import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

window = tk.Tk()
window.title("Avix Mobile")
window.geometry("720x480")
window.resizable(False, False)

# ---------------- BACKGROUND IMAGE ----------------
bg = Image.open("background.png")
bg = bg.resize((720, 480))

overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
bg = bg.convert("RGBA")
dark_bg = Image.alpha_composite(bg, overlay)

bg_image = ImageTk.PhotoImage(dark_bg)

canvas = tk.Canvas(window, width=720, height=480, highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=bg_image, anchor="nw")


# ---------------- ROUNDED RECTANGLE FUNCTION ----------------
def rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
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
    return canvas.create_polygon(points, smooth=True, **kwargs)


# ---------------- LOGO BOX WITH IMAGE ----------------
# Shadow
rounded_rectangle(
    canvas,
    28, 23, 115, 110,
    radius=22,
    fill="#000000",
    outline=""
)

# Logo box
rounded_rectangle(
    canvas,
    24, 20, 110, 105,
    radius=22,
    fill="#111827",
    outline="#00CFFF",
    width=2
)

# Load logo image
logo = Image.open("logo.jpg")
logo = logo.resize((70, 70))
logo = logo.convert("RGBA")

# Make logo rounded
mask = Image.new("L", logo.size, 0)
draw = ImageDraw.Draw(mask)
draw.rounded_rectangle((0, 0, 70, 70), radius=18, fill=255)

rounded_logo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
rounded_logo.paste(logo, (0, 0), mask)

logo_image = ImageTk.PhotoImage(rounded_logo)

# Add logo image to canvas
canvas.create_image(67, 62, image=logo_image, anchor="center")
canvas.logo_image = logo_image


# ---------------- TITLE TEXT ----------------
canvas.create_text(
    360, 150,
    text="Avix LK",
    font=("Ubuntu", 42, "bold"),
    fill="#FFD700"
)


# ---------------- PROGRESS BAR STYLE ----------------
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Dark.Horizontal.TProgressbar",
    troughcolor="#1C2541",
    background="#FFD700",
    bordercolor="#1C2541",
    lightcolor="#FFD700",
    darkcolor="#FFD700"
)

progress = ttk.Progressbar(
    window,
    orient="horizontal",
    length=300,
    mode="determinate",
    style="Dark.Horizontal.TProgressbar"
)

progress_label = tk.Label(
    window,
    text="",
    font=("Bahnschrift", 14),
    bg="#0B132B",
    fg="white"
)


# ---------------- NEW WINDOW ----------------
def open_new_window():
    window.destroy()

    new_window = tk.Tk()
    new_window.title("Avix Mobile - Home")
    new_window.geometry("720x480")
    new_window.resizable(False, False)

    new_bg = Image.open("background.png")
    new_bg = new_bg.resize((720, 480))
    new_bg = new_bg.convert("RGBA")

    new_overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
    new_dark_bg = Image.alpha_composite(new_bg, new_overlay)

    new_bg_image = ImageTk.PhotoImage(new_dark_bg)

    new_canvas = tk.Canvas(new_window, width=720, height=480, highlightthickness=0)
    new_canvas.pack(fill="both", expand=True)

    new_canvas.create_image(0, 0, image=new_bg_image, anchor="nw")
    new_canvas.image = new_bg_image

    new_canvas.create_text(
        360, 240,
        text="Welcome to Avix LK",
        font=("Ubuntu", 35, "bold"),
        fill="#FFD700"
    )

    new_window.mainloop()


# ---------------- LOADING FUNCTION ----------------
def start_loading():
    global button_disabled

    if button_disabled:
        return

    button_disabled = True

    canvas.itemconfig(button_fill, fill="#4A0000")
    canvas.itemconfig(button_text, fill="#BBBBBB")

    canvas.create_window(360, 300, window=progress)
    canvas.create_window(360, 330, window=progress_label)

    load_progress(0)


def load_progress(value):
    progress["value"] = value
    progress_label.config(text=str(value) + "%")

    if value < 100:
        window.after(40, load_progress, value + 1)
    else:
        window.after(300, open_new_window)


# ---------------- ROUNDED 3D ENTER BUTTON ----------------
button_disabled = False

# Bottom shadow for 3D effect
button_shadow = rounded_rectangle(
    canvas,
    225, 220, 495, 283,
    radius=30,
    fill="#2B0000",
    outline=""
)

# Main button body
button_fill = rounded_rectangle(
    canvas,
    225, 210, 495, 273,
    radius=30,
    fill="#8B0000",
    outline="#FF6B6B",
    width=2
)

# Top highlight line
button_highlight = rounded_rectangle(
    canvas,
    238, 218, 482, 240,
    radius=20,
    fill="#B22222",
    outline=""
)

# Button text
button_text = canvas.create_text(
    360, 242,
    text="ENTER",
    font=("Roboto Mono", 25, "bold"),
    fill="white"
)

# Make all button parts clickable
for item in [button_shadow, button_fill, button_highlight, button_text]:
    canvas.tag_bind(item, "<Button-1>", lambda event: start_loading())
    canvas.tag_bind(item, "<Enter>", lambda event: canvas.config(cursor="hand2"))
    canvas.tag_bind(item, "<Leave>", lambda event: canvas.config(cursor=""))


window.mainloop()