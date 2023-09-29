import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import notes_database as ndb


class CategoryListInterface:
    def __init__(self, parent_object, parent_window, from_editor=False):
        self.category_id = None
        self.parent_object = parent_object
        self.parent_window = parent_window
        self.category_info = parent_object.categories
        self.from_editor = from_editor

        parent_x = self.parent_window.winfo_x() + 110
        parent_y = self.parent_window.winfo_y() + 160

        self.category_window = tk.Toplevel(self.parent_window)
        self.category_window.geometry(f"307x158+{parent_x}+{parent_y}")
        self.category_window.resizable(False, False)
        self.category_window.overrideredirect(True)
        self.category_window.configure(background="#d9d9d9")

        self.x_cursor = self.x_root = self.x_mouse = None
        self.y_cursor = self.y_root = self.y_mouse = None
        self.drag_frame = tk.Frame(self.category_window, bg="#b7b7b7", height=15, cursor="hand2")
        self.drag_frame.bind("<ButtonPress-1>", self.start_move)
        self.drag_frame.bind("<B1-Motion>", self.on_drag)
        self.drag_frame.pack(fill="x")

        self.combobox = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.category_window)
        self.category_combobox.place(relx=0.065, rely=0.443, relheight=0.165, relwidth=0.879)
        self.category_combobox.bind("<<ComboboxSelected>>", self.user_selected_combobox)
        self.category_combobox.configure(cursor="hand2")
        self.category_combobox.configure(font="-family {Comic Sans MS} -size 10")
        self.category_combobox.configure(state="readonly")
        self.category_combobox.configure(textvariable=self.combobox)
        self.category_combobox.configure(takefocus="")
        self.initialize_combobox()

        self.select_cat_label = tk.Label(self.category_window)
        self.select_cat_label.place(relx=0.055, rely=0.228, height=27, width=275)
        self.select_cat_label.configure(anchor='w')
        self.select_cat_label.configure(background="#d9d9d9")
        self.select_cat_label.configure(compound='left')
        self.select_cat_label.configure(disabledforeground="#a3a3a3")
        self.select_cat_label.configure(font="-family {Comic Sans MS} -size 12")
        self.select_cat_label.configure(foreground="#000000")
        select_cat_text = "Select category:" if self.from_editor else "Select category filter:"
        self.select_cat_label.configure(text=select_cat_text)

        self.select_button = tk.Button(self.category_window)
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
        self.select_button.configure(state="disabled")
        self.select_button.configure(text='''Select''')

        self.back_button = tk.Button(self.category_window)
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
        self.back_button.configure(text='''Back''')

        self.create_button = tk.Button(self.category_window)
        self.create_button.place(relx=0.749, rely=0.677, height=28, width=59) if self.from_editor else None
        self.create_button.configure(activebackground="#b5b5b5")
        self.create_button.configure(activeforeground="black")
        self.create_button.configure(background="#d9d9d9")
        self.create_button.configure(command=self.create_category)
        self.create_button.configure(compound='left')
        self.create_button.configure(disabledforeground="#a3a3a3")
        self.create_button.configure(font="-family {Comic Sans MS} -size 9")
        self.create_button.configure(foreground="#000000")
        self.create_button.configure(highlightbackground="#d9d9d9")
        self.create_button.configure(highlightcolor="black")
        self.create_button.configure(pady="0")
        self.create_button.configure(text='''Create''')

    def start_move(self, event):
        self.x_cursor = event.x
        self.y_cursor = event.y

    def on_drag(self, event):
        self.x_mouse = event.x_root
        self.y_mouse = event.y_root

        new_x = self.x_mouse - self.x_cursor
        new_y = self.y_mouse - self.y_cursor

        self.category_window.geometry(f"+{new_x}+{new_y}")

    def user_selected_combobox(self, event):
        _ = event  # Ignore
        self.select_button.configure(state="normal")
        self.category_window.focus_set()

    def initialize_combobox(self):
        combobox_values = []
        for category in self.category_info:
            combobox_values.append(category[1])
        self.category_combobox["values"] = combobox_values
        self.category_combobox.set("Select a category")

    def go_select(self):
        selected_category = self.category_combobox.get()
        self.category_id = (0, "None")
        for category in self.category_info:
            if selected_category == category[1]:
                self.category_id = category
        self.category_window.destroy()

    def go_back(self):
        self.category_window.destroy()

    def create_category(self):
        create_cat_window = CreateCategoryInterface(self.parent_object, self.category_window)
        self.create_button.configure(state="disabled")
        create_cat_window.create_category_window.wait_window()
        self.category_info = ndb.get_categories()
        self.create_button.configure(state="normal")

        category_info = create_cat_window.category_info
        category_name = category_info[1] if category_info else None
        if category_name:
            current_list = list(self.category_combobox["values"])
            current_list.append(category_name)
            self.category_combobox["values"] = current_list
            self.category_combobox.set(category_name)
            self.select_button.configure(state="normal")


class CreateCategoryInterface:
    def __init__(self, parent_object, parent_window):
        self.parent_object = parent_object
        self.parent_window = parent_window
        self.category_info = None

        parent_x = self.parent_window.winfo_x() + 30
        parent_y = self.parent_window.winfo_y() + 30

        self.create_category_window = tk.Toplevel(self.parent_window)
        self.create_category_window.geometry(f"307x158+{parent_x}+{parent_y}")
        self.create_category_window.minsize(120, 1)
        self.create_category_window.maxsize(1924, 1061)
        self.create_category_window.resizable(False, False)
        self.create_category_window.title("create_category_windowlevel 0")
        self.create_category_window.overrideredirect(True)
        self.create_category_window.configure(background="#d9d9d9")
        self.create_category_window.configure(highlightbackground="#d9d9d9")
        self.create_category_window.configure(highlightcolor="black")

        self.x_cursor = self.x_root = self.x_mouse = None
        self.y_cursor = self.y_root = self.y_mouse = None
        self.drag_frame = tk.Frame(self.create_category_window, bg="#b7b7b7", height=15, cursor="hand2")
        self.drag_frame.bind("<ButtonPress-1>", self.start_move)
        self.drag_frame.bind("<B1-Motion>", self.on_drag)
        self.drag_frame.pack(fill="x")

        self.create_cat_label = tk.Label(self.create_category_window)
        self.create_cat_label.place(relx=0.055, rely=0.228, height=27, width=275)
        self.create_cat_label.configure(activebackground="#f9f9f9")
        self.create_cat_label.configure(anchor='w')
        self.create_cat_label.configure(background="#d9d9d9")
        self.create_cat_label.configure(compound='left')
        self.create_cat_label.configure(disabledforeground="#a3a3a3")
        self.create_cat_label.configure(font="-family {Comic Sans MS} -size 12")
        self.create_cat_label.configure(foreground="#000000")
        self.create_cat_label.configure(highlightbackground="#d9d9d9")
        self.create_cat_label.configure(highlightcolor="black")
        self.create_cat_label.configure(text='''Enter category name:''')

        self.create_button = tk.Button(self.create_category_window)
        self.create_button.place(relx=0.065, rely=0.677, height=28, width=59)
        self.create_button.configure(activebackground="#b5b5b5")
        self.create_button.configure(activeforeground="black")
        self.create_button.configure(background="#d9d9d9")
        self.create_button.configure(command=self.create_category)
        self.create_button.configure(compound='left')
        self.create_button.configure(disabledforeground="#a3a3a3")
        self.create_button.configure(font="-family {Comic Sans MS} -size 9")
        self.create_button.configure(foreground="#000000")
        self.create_button.configure(highlightbackground="#d9d9d9")
        self.create_button.configure(highlightcolor="black")
        self.create_button.configure(pady="0")
        self.create_button.configure(state="disabled")
        self.create_button.configure(text='''Create''')

        self.back_button = tk.Button(self.create_category_window)
        self.back_button.place(relx=0.293, rely=0.677, height=28, width=59)
        self.back_button.configure(activebackground="#b5b5b5")
        self.back_button.configure(activeforeground="black")
        self.back_button.configure(background="#d9d9d9")
        self.back_button.configure(command=self.go_back)
        self.back_button.configure(compound='left')
        self.back_button.configure(disabledforeground="#a3a3a3")
        self.back_button.configure(font="-family {Comic Sans MS} -size 9")
        self.back_button.configure(foreground="#000000")
        self.back_button.configure(highlightbackground="#d9d9d9")
        self.back_button.configure(highlightcolor="black")
        self.back_button.configure(pady="0")
        self.back_button.configure(text='''Back''')

        self.cat_name_entry = tk.Entry(self.create_category_window)
        self.cat_name_entry.place(relx=0.065, rely=0.443, height=25, relwidth=0.876)
        self.cat_name_entry.bind("<KeyRelease>", self.entry_event)
        self.cat_name_entry.bind("<Key-Return>", self.create_category)
        self.cat_name_entry.configure(background="white")
        self.cat_name_entry.configure(disabledforeground="#a3a3a3")
        self.cat_name_entry.configure(font="-family {Comic Sans MS} -size 10")
        self.cat_name_entry.configure(foreground="#000000")
        self.cat_name_entry.configure(highlightbackground="#d9d9d9")
        self.cat_name_entry.configure(highlightcolor="black")
        self.cat_name_entry.configure(insertbackground="black")
        self.cat_name_entry.configure(selectbackground="#c4c4c4")
        self.cat_name_entry.configure(selectforeground="black")

    def start_move(self, event=None):
        self.x_cursor = event.x
        self.y_cursor = event.y

    def on_drag(self, event=None):
        self.x_mouse = event.x_root
        self.y_mouse = event.y_root

        new_x = self.x_mouse - self.x_cursor
        new_y = self.y_mouse - self.y_cursor

        self.create_category_window.geometry(f"+{new_x}+{new_y}")

    def entry_event(self, event=None):
        _ = event  # Ignore
        if self.cat_name_entry.get() == "":
            self.create_button.configure(state="disabled")
        else:
            self.create_button.configure(state="normal")

    def create_category(self, event=None):
        _ = event  # Ignore
        category_name = self.cat_name_entry.get()
        categories = self.parent_object.categories

        for category in categories:
            if category_name.lower() == category[1].lower():
                proceed = messagebox.askyesno("Duplicate Category Found", "An existing category with the same name "
                                                                          "found, do you still want to create this "
                                                                          "category? They might be treated as the "
                                                                          "same category.")
                if not proceed:
                    self.create_category_window.focus_set()
                    self.parent_window.focus_set()
                    return

        self.category_info = ndb.create_category(category_name)
        messagebox.showinfo("Success!", "Category was created successfully :D")
        self.parent_object.categories = ndb.get_categories()
        self.create_category_window.destroy()
        self.parent_window.focus_set()

    def go_back(self):
        self.create_category_window.destroy()


class DeleteCategoryInterface:
    def __init__(self, parent_object, parent_window):
        self.category_id = None
        self.parent_object = parent_object
        self.parent_window = parent_window
        self.category_info = parent_object.categories

        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()

        self.delete_category_window = tk.Toplevel(self.parent_window)
        self.delete_category_window.geometry(f"307x158+{parent_x}+{parent_y}")
        self.delete_category_window.resizable(False, False)
        self.delete_category_window.overrideredirect(True)
        self.delete_category_window.configure(background="#d9d9d9")

        self.x_cursor = self.x_root = self.x_mouse = None
        self.y_cursor = self.y_root = self.y_mouse = None
        self.drag_frame = tk.Frame(self.delete_category_window, bg="#b7b7b7", height=15, cursor="hand2")
        self.drag_frame.bind("<ButtonPress-1>", self.start_move)
        self.drag_frame.bind("<B1-Motion>", self.on_drag)
        self.drag_frame.pack(fill="x")

        self.combobox = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.delete_category_window)
        self.category_combobox.place(relx=0.065, rely=0.443, relheight=0.165, relwidth=0.879)
        self.category_combobox.bind("<<ComboboxSelected>>", self.user_selected_combobox)
        self.category_combobox.configure(cursor="hand2")
        self.category_combobox.configure(font="-family {Comic Sans MS} -size 10")
        self.category_combobox.configure(state="readonly")
        self.category_combobox.configure(textvariable=self.combobox)
        self.category_combobox.configure(takefocus="")
        self.initialize_combobox()

        self.delete_cat_label = tk.Label(self.delete_category_window)
        self.delete_cat_label.place(relx=0.055, rely=0.228, height=27, width=275)
        self.delete_cat_label.configure(anchor='w')
        self.delete_cat_label.configure(background="#d9d9d9")
        self.delete_cat_label.configure(compound='left')
        self.delete_cat_label.configure(disabledforeground="#a3a3a3")
        self.delete_cat_label.configure(font="-family {Comic Sans MS} -size 12")
        self.delete_cat_label.configure(foreground="#000000")
        self.delete_cat_label.configure(text='''Delete a category:''')

        self.delete_button = tk.Button(self.delete_category_window)
        self.delete_button.place(relx=0.068, rely=0.677, height=28, width=59)
        self.delete_button.configure(activebackground="#b5b5b5")
        self.delete_button.configure(activeforeground="black")
        self.delete_button.configure(background="#d9d9d9")
        self.delete_button.configure(command=self.delete_category)
        self.delete_button.configure(compound='left')
        self.delete_button.configure(cursor="hand2")
        self.delete_button.configure(disabledforeground="#a3a3a3")
        self.delete_button.configure(font="-family {Comic Sans MS} -size 9")
        self.delete_button.configure(foreground="#000000")
        self.delete_button.configure(highlightbackground="#d9d9d9")
        self.delete_button.configure(highlightcolor="black")
        self.delete_button.configure(pady="0")
        self.delete_button.configure(state="disabled")
        self.delete_button.configure(text='''Delete''')

        self.back_button = tk.Button(self.delete_category_window)
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
        self.back_button.configure(text='''Back''')

    def start_move(self, event):
        self.x_cursor = event.x
        self.y_cursor = event.y

    def on_drag(self, event):
        self.x_mouse = event.x_root
        self.y_mouse = event.y_root

        new_x = self.x_mouse - self.x_cursor
        new_y = self.y_mouse - self.y_cursor

        self.delete_category_window.geometry(f"+{new_x}+{new_y}")

    def user_selected_combobox(self, event):
        _ = event  # Ignore
        self.delete_button.configure(state="normal")
        self.delete_category_window.focus_set()

    def initialize_combobox(self):
        combobox_values = []
        for category in self.category_info:
            if category[1].lower() == "none":
                continue
            combobox_values.append(category[1])
        self.category_combobox["values"] = combobox_values
        self.category_combobox.set("Select a category")

    def go_back(self):
        self.delete_category_window.destroy()

    def delete_category(self):
        selected_category = self.category_combobox.get()
        self.category_id = (0, "None")
        for category in self.category_info:
            if selected_category == category[1]:
                all_notes = ndb.get_all_notes()
                for note in all_notes:
                    if note[1] == category[0]:
                        ndb.change_note_category(0, note[0])
                ndb.delete_category(category[0])
                messagebox.showinfo("Done", f"Category deletion successful! All notes having {selected_category} "
                                            "category will be set to None.")
                self.parent_object.update_notes()
                self.delete_category_window.focus_set()

        current_list = ndb.get_categories()
        current_list = [category[1] for category in current_list if category[1].lower() != "none"]
        self.category_combobox["values"] = current_list
        self.category_combobox.set("Select a category to delete")
        self.delete_button.configure(state="disabled")