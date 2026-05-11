import tkinter as tk


window = tk.Tk()

window.title('Avix Mobile')

window.geometry('720x480')


tklbl = tk.Label (window,text = "Avix.lk",  font = ("Times New Roman", 40))
tklbl.config(font ="syfean", )
tklbl.grid(row = 2, columnspan= 8, padx= (10,10), pady=(30,0))

def clicked():
    res = "Welcome " + txt.get()
    tklbl.configure(text = res)

txt = tk.Entry(window, width = 15)
txt.grid(column = 2, row = 2)

btn = tk.Button(window, text = 'Click me', command = clicked)
btn.grid(column =3, row = 2)

window.mainloop()


