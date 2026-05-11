import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

window = tk.Tk()
window.title("Avix Mobile")
window.geometry("720x480")

# Load background image
bg = Image.open("background.png")
bg = bg.resize((720, 480))

# Add dark layer
overlay = Image.new("RGBA", (720, 480), (0, 0, 0, 150))
bg = bg.convert("RGBA")
dark_bg = Image.alpha_composite(bg, overlay)

bg_image = ImageTk.PhotoImage(dark_bg)

# Canvas background
canvas = tk.Canvas(window, width=720, height=480, highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=bg_image, anchor="nw")

# Transparent Avix LK text
canvas.create_text(
    360, 150,
    text="Avix LK",
    font=("Ubuntu", 42, "bold"),
    fill="#FFD700"
)

# Progress bar style
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

# Loading bar
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

def open_new_window():
    window.destroy()

    new_window = tk.Tk()
    new_window.title("Avix Mobile - Home")
    new_window.geometry("720x480")

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

def start_loading():
    enter_btn.config(state="disabled")

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

enter_btn = tk.Button(
    window,
    text="ENTER",
    font=("Roboto Mono", 25, "bold"),
    bg="#8B0000",
    fg="white",
    activebackground="#B22222",
    activeforeground="white",
    width=18,
    command=start_loading
)

canvas.create_window(360, 230, window=enter_btn)

window.mainloop()