import tkinter as tk
from pathlib import Path

from welcome_page import WelcomePage
from login_page import LoginPage
from dashboard import DashboardPage


class AvixApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Avix Mobile")
        self.geometry("720x480")
        self.resizable(False, False)

        project_dir = Path(__file__).resolve().parent
        icon_path = project_dir / "icon.ico"

        if icon_path.exists():
            self.iconbitmap(str(icon_path))

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


if __name__ == "__main__":
    app = AvixApp()
    app.mainloop()