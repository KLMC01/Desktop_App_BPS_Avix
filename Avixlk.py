import tkinter as tk
from tkinter import ttk

window = tk.Tk()

window.title("Avix Mobile")
window.geometry("720x480")
window.config(bg="#0B132B")  # dark navy background

# Background image
bg_image = tk.PhotoImage(file="sample.png")  # put your image name here

bg_label = tk.Label(window, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Make center layout
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.columnconfigure(0, weight=1)

# Progress bar dark style
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

# Avix LK label
title_label = tk.Label(
    window,
    text="Avix LK",
    font=("Times New Roman", 40, "bold"),
    fg="#FFD700",      # gold title
    bg="#0B132B"       # same as window bg
)
title_label.grid(row=0, column=0, pady=(120, 20))

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
    font=("Times New Roman", 14),
    bg="#0B132B",
    fg="white"
)

# New window function
def open_new_window():
    window.destroy()

    new_window = tk.Tk()
    new_window.title("Avix Mobile - Home")
    new_window.geometry("720x480")
    new_window.config(bg="#0B132B")

    welcome_label = tk.Label(
        new_window,
        text="Welcome to Avix LK",
        font=("Times New Roman", 35, "bold"),
        fg="#FFD700",
        bg="#0B132B"
    )
    welcome_label.pack(expand=True)

    new_window.mainloop()

# Loading function
def start_loading():
    enter_btn.config(state="disabled")

    progress.grid(row=2, column=0, pady=(10, 5))
    progress_label.grid(row=3, column=0)

    load_progress(0)

def load_progress(value):
    progress["value"] = value
    progress_label.config(text=str(value) + "%")

    if value < 100:
        window.after(40, load_progress, value + 1)
    else:
        window.after(300, open_new_window)

# Enter button
enter_btn = tk.Button(
    window,
    text="E N T E R",
    font=("Century Gothic", 35, "bold"),
    bg="#8B0000",      # dark red
    fg="white",
    activebackground="#B22222",
    activeforeground="white",
    width=18,
    command=start_loading
)
enter_btn.grid(row=1, column=0)

window.mainloop()