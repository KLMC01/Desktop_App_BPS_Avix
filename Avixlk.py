import tkinter as tk
from tkinter import ttk

window = tk.Tk()

window.title("Avix Mobile")
window.geometry("720x480")
window.config(bg="#FF69B4")

# Make center layout
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.columnconfigure(0, weight=1)

# Avix LK label
title_label = tk.Label(
    window,
    text="Avix LK",
    font=("Times New Roman", 40, "bold"),
    fg="red",
    bg="light blue"
)
title_label.grid(row=0, column=0, pady=(120, 20))

# Loading bar
progress = ttk.Progressbar(
    window,
    orient="horizontal",
    length=300,
    mode="determinate"
)

progress_label = tk.Label(
    window,
    text="",
    font=("Times New Roman", 14),
    bg="light blue",
    fg="black"
)

# New window function
def open_new_window():
    window.destroy()

    new_window = tk.Tk()
    new_window.title("Avix Mobile - Home")
    new_window.geometry("720x480")
    new_window.config(bg="light blue")

    welcome_label = tk.Label(
        new_window,
        text="Welcome to Avix LK",
        font=("Times New Roman", 35, "bold"),
        fg="yellow",
        bg="light blue"
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
    text="Enter",
    font=("Times New Roman", 18, "bold"),
    bg="#ff7f7f",
    fg="white",
    width=12,
    command=start_loading
)
enter_btn.grid(row=1, column=0)

window.mainloop()