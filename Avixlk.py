import tkinter as tk

window = tk.Tk()

window.title("Avix Mobile")
window.geometry("720x480")
window.config(bg="light blue")

# Make the window grid expand properly
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.columnconfigure(0, weight=1)

# Avix LK label
title_label = tk.Label(
    window,
    text="Avix LK",
    font=("Times New Roman", 40, "bold"),
    fg="yellow",
    bg="light blue"
)

title_label.grid(row=0, column=0, pady=(120, 20))

# Button click function
def clicked():
    title_label.config(text="Welcome to Avix LK")

# Enter button
enter_btn = tk.Button(
    window,
    text="Enter",
    font=("Times New Roman", 18, "bold"),
    bg="#ff7f7f",   # light red
    fg="white",
    width=12,
    command=clicked
)

enter_btn.grid(row=1, column=0)

window.mainloop()