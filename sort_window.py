import tkinter as tk
import tkinter.ttk as ttk


class SortNotesInterface:
    def __init__(self, parent_object, parent_window):
        self.sort_by = parent_object.sort_notes_by
        self.sort_type = parent_object.sort_notes_type
        self.is_returned = False
        self.parent_object = parent_object
        self.parent_window = parent_window

        self.sort_window = tk.Toplevel(self.parent_window)
        self.sort_window.geometry("307x158+630+318")
        self.sort_window.resizable(False, False)
        self.sort_window.overrideredirect(True)
        self.sort_window.configure(background="#d9d9d9")

        self.x_cursor = self.x_root = self.x_mouse = None
        self.y_cursor = self.y_root = self.y_mouse = None
        self.drag_frame = tk.Frame(self.sort_window, bg="#b7b7b7", height=15, cursor="hand2")
        self.drag_frame.bind("<ButtonPress-1>", self.start_move)
        self.drag_frame.bind("<B1-Motion>", self.on_drag)
        self.drag_frame.pack(fill="x")

        self.combobox = tk.StringVar()
        self.method_combobox = ttk.Combobox(self.sort_window)
        self.method_combobox.place(relx=0.065, rely=0.443, relheight=0.165, relwidth=0.879)
        self.method_combobox.bind("<<ComboboxSelected>>", self.user_selected_combobox)
        self.method_combobox.configure(cursor="hand2")
        self.method_combobox.configure(font="-family {Comic Sans MS} -size 10")
        self.method_combobox.configure(state="readonly")
        self.method_combobox.configure(textvariable=self.combobox)
        self.method_combobox.configure(takefocus="")
        self.initialize_combobox()

        self.sort_mode_label = tk.Label(self.sort_window)
        self.sort_mode_label.place(relx=0.055, rely=0.228, height=27, width=275)
        self.sort_mode_label.configure(anchor='w')
        self.sort_mode_label.configure(background="#d9d9d9")
        self.sort_mode_label.configure(compound='left')
        self.sort_mode_label.configure(disabledforeground="#a3a3a3")
        self.sort_mode_label.configure(font="-family {Comic Sans MS} -size 12")
        self.sort_mode_label.configure(foreground="#000000")
        self.sort_mode_label.configure(text="Sort notes by:")

        self.sort_mode_type = tk.Button(self.sort_window)
        self.sort_mode_type.place(relx=0.715, rely=0.677, height=28, width=70)
        self.sort_mode_type.configure(activebackground="#b5b5b5")
        self.sort_mode_type.configure(activeforeground="black")
        self.sort_mode_type.configure(background="#d9d9d9")
        self.sort_mode_type.configure(command=self.toggle_sort_type)
        self.sort_mode_type.configure(compound='left')
        self.sort_mode_type.configure(cursor='hand2')
        self.sort_mode_type.configure(disabledforeground="#a3a3a3")
        self.sort_mode_type.configure(font="-family {Comic Sans MS} -size 9")
        self.sort_mode_type.configure(foreground="#000000")
        self.sort_mode_type.configure(highlightbackground="#d9d9d9")
        self.sort_mode_type.configure(highlightcolor="black")
        self.sort_mode_type.configure(pady="0")
        self.sort_mode_type.configure(text="Ascending" if self.sort_type == "asc" else "Descending")

        self.select_button = tk.Button(self.sort_window)
        self.select_button.place(relx=0.068, rely=0.677, height=28, width=59)
        self.select_button.configure(activebackground="#b5b5b5")
        self.select_button.configure(activeforeground="black")
        self.select_button.configure(background="#d9d9d9")
        self.select_button.configure(command=self.go_select)
        self.select_button.configure(compound='left')
        self.select_button.configure(cursor="hand2")
        self.select_button.configure(disabledforeground="#a3a3a3")
        self.select_button.configure(font="-family {Comic Sans MS} -size 9")
        self.select_button.configure(foreground="#000000")
        self.select_button.configure(highlightbackground="#d9d9d9")
        self.select_button.configure(highlightcolor="black")
        self.select_button.configure(pady="0")
        self.select_button.configure(text="Select")

        self.back_button = tk.Button(self.sort_window)
        self.back_button.place(relx=0.293, rely=0.677, height=28, width=59)
        self.back_button.configure(activebackground="#b5b5b5")
        self.back_button.configure(activeforeground="black")
        self.back_button.configure(background="#d9d9d9")
        self.back_button.configure(command=self.go_back)
        self.back_button.configure(compound='left')
        self.back_button.configure(cursor="hand2")
        self.back_button.configure(disabledforeground="#a3a3a3")
        self.back_button.configure(font="-family {Comic Sans MS} -size 9")
        self.back_button.configure(foreground="#000000")
        self.back_button.configure(highlightbackground="#d9d9d9")
        self.back_button.configure(highlightcolor="black")
        self.back_button.configure(pady="0")
        self.back_button.configure(text="Back")

    def start_move(self, event):
        self.x_cursor = event.x
        self.y_cursor = event.y

    def on_drag(self, event):
        self.x_mouse = event.x_root
        self.y_mouse = event.y_root

        new_x = self.x_mouse - self.x_cursor
        new_y = self.y_mouse - self.y_cursor

        self.sort_window.geometry(f"+{new_x}+{new_y}")

    def user_selected_combobox(self, event):
        _ = event  # Ignore
        self.select_button.configure(state="normal")
        self.sort_window.focus_set()

    def initialize_combobox(self):
        combobox_values = ["Note Title", "Category", "Modified Date"]
        self.method_combobox["values"] = combobox_values
        self.combobox.set(self.sort_by.title())

    def toggle_sort_type(self):
        if self.sort_type == "asc":
            self.sort_type = "desc"
            self.sort_mode_type.configure(text="Descending")
        else:
            self.sort_type = "asc"
            self.sort_mode_type.configure(text="Ascending")

    def go_select(self):
        self.sort_by = self.method_combobox.get()
        self.sort_window.destroy()

    def go_back(self):
        self.is_returned = True
        self.sort_window.destroy()