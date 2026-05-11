from tkinter import *

window = Tk()

window.title ('Avix Mobile')


lbl = Label (window,text = "Hello", font = ("Arial", 75))
lbl.grid(column =0, row = 2)

def clicked():
    lbl.configure(text = "Hi Everyone!!")


btn = Button(window, text = 'Click me', bg = "red", fg = "white", command = Clicked)
btn.grid(column =2, row = 2)

window.mainloop()


