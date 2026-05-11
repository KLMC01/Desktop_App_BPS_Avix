from tkinter import *

window = Tk()

window.title ('Avix Mobile')



lbl = Label (window,text = "Hello", font = ("Arial", 75))
lbl.grid(column =0, row = 2)

def clicked():
    res = "Welcome " + txt.get()
    lbl.configure(text = res)

txt = Entry(window, width = 15)
txt.grid(column = 2, row = 2)

btn = Button(window, text = 'Click me', bg = "red", fg = "white", command = clicked)
btn.grid(column =2, row = 2)

window.mainloop()


