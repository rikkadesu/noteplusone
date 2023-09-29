import tkinter as tk


root = tk.Tk()
root.geometry("300x300")


def open_new_window():
    tk.Toplevel(root)


button = tk.Button(master=root, text="Legerson")
button.configure(width=20, height=5)
button.configure(command=open_new_window)
button.pack()

button1 = tk.Button(master=root, text="Legerson")
button1.configure(width=20, height=5)
button1.configure(command=open_new_window)
button1.pack()

root.mainloop()