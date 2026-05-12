import tkinter as tk
from welcome_page import WelcomePage
from login_page import LoginPage


class AvixApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Avix Mobile")
        self.geometry("720x480")
        self.resizable(False, False)

        self.show_welcome_page()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_welcome_page(self):
        self.clear_window()
        WelcomePage(self, self.show_login_page)

    def show_login_page(self):
        self.clear_window()
        LoginPage(self, self.show_welcome_page, self.show_dashboard_page)

    def show_dashboard_page(self):
        self.clear_window()

        canvas = tk.Canvas(self, width=720, height=480, bg="#06101E", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(
            360, 210,
            text="Dashboard Page",
            font=("Arial", 34, "bold"),
            fill="white"
        )

        canvas.create_text(
            360, 255,
            text="Login successful. System dashboard will be designed here.",
            font=("Arial", 13),
            fill="#DDEEFF"
        )


app = AvixApp()
app.mainloop()