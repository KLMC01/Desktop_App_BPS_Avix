import tkinter as tk
from welcome_page import WelcomePage
from login_page import LoginPage
from dashboard_page import DashboardPage


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
        DashboardPage(self, self.show_welcome_page)


app = AvixApp()
app.mainloop()