import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import json
import os

from category_window import DeleteCategoryInterface
import notes_database as ndb
from tooltip import ToolTip

_tooltip_font = "-family {Comic Sans MS} -size 10"


class SettingsInterface:
    def __init__(self, parent_object, parent_window):
        self.parent_window = parent_window
        self.parent_object = parent_object
        self.settings = self.load_settings()

        parent_x = self.parent_window.winfo_x() + 80
        parent_y = self.parent_window.winfo_y() + 160

        self.settings_window = tk.Toplevel(self.parent_window)
        self.settings_window.geometry(f"366x189+{parent_x}+{parent_y}")
        self.settings_window.minsize(120, 1)
        self.settings_window.maxsize(1924, 1061)
        self.settings_window.overrideredirect(True)
        self.settings_window.resizable(False,  False)
        self.settings_window.title("Settings")
        self.settings_window.configure(background="#d9d9d9")

        self.x_cursor = self.x_root = self.x_mouse = None
        self.y_cursor = self.y_root = self.y_mouse = None
        self.drag_frame = tk.Frame(self.settings_window, bg="#b7b7b7", height=15, cursor="hand2")
        self.drag_frame.bind("<ButtonPress-1>", self.start_move)
        self.drag_frame.bind("<B1-Motion>", self.on_drag)
        self.drag_frame.pack(fill="x")

        self.settings_label = tk.Label(self.settings_window)
        self.settings_label.place(relx=0.292, rely=0.079, height=43, width=155)
        self.settings_label.configure(background="#d9d9d9")
        self.settings_label.configure(compound='left')
        self.settings_label.configure(disabledforeground="#a3a3a3")
        self.settings_label.configure(font="-family {Comic Sans MS} -size 20 -weight bold")
        self.settings_label.configure(foreground="#000000")
        self.settings_label.configure(text='''Settings''')

        self.settings_separator = ttk.Separator(self.settings_window)
        self.settings_separator.place(relx=0.5, rely=0.317,  relheight=0.582)
        self.settings_separator.configure(orient="vertical")

        self.delete_categories_button = tk.Button(self.settings_window)
        self.delete_categories_button.place(relx=0.055, rely=0.317, height=28, width=139)
        self.delete_categories_button.configure(activebackground="#b5b5b5")
        self.delete_categories_button.configure(activeforeground="black")
        self.delete_categories_button.configure(background="#d9d9d9")
        self.delete_categories_button.configure(command=self.delete_categories)
        self.delete_categories_button.configure(compound='left')
        self.delete_categories_button.configure(cursor='hand2')
        self.delete_categories_button.configure(disabledforeground="#a3a3a3")
        self.delete_categories_button.configure(font="-family {Comic Sans MS} -size 11")
        self.delete_categories_button.configure(foreground="#000000")
        self.delete_categories_button.configure(highlightbackground="#d9d9d9")
        self.delete_categories_button.configure(highlightcolor="black")
        self.delete_categories_button.configure(pady="0")
        self.delete_categories_button.configure(relief="flat")
        self.delete_categories_button.configure(text='''Delete Categories''')
        ToolTip(self.delete_categories_button, "Delete a category you don't need anymore :D", font=_tooltip_font)

        self.autosave_button = tk.Button(self.settings_window)
        self.autosave_button.place(relx=0.055, rely=0.476, height=28, width=139)
        self.autosave_button.configure(activebackground="#b5b5b5")
        self.autosave_button.configure(activeforeground="black")
        self.autosave_button.configure(background="#d9d9d9")
        self.autosave_button.configure(command=self.toggle_autosave)
        self.autosave_button.configure(compound='left')
        self.autosave_button.configure(cursor='hand2')
        self.autosave_button.configure(disabledforeground="#a3a3a3")
        self.autosave_button.configure(font="-family {Comic Sans MS} -size 11")
        self.autosave_button.configure(foreground="#000000")
        self.autosave_button.configure(highlightbackground="#d9d9d9")
        self.autosave_button.configure(highlightcolor="black")
        self.autosave_button.configure(pady="0")
        self.autosave_button.configure(relief="flat")
        autosave_state = "Autosave - On" if self.settings["autosave"] else "Autosave - Off"
        self.autosave_button.configure(text=autosave_state)
        ToolTip(self.autosave_button, "If enabled, your modifications to a note will be autosaved every 30 seconds!",
                font=_tooltip_font)

        self.export_notes_button = tk.Button(self.settings_window)
        self.export_notes_button.place(relx=0.574, rely=0.317, height=28, width=139)
        self.export_notes_button.configure(activebackground="#b5b5b5")
        self.export_notes_button.configure(activeforeground="black")
        self.export_notes_button.configure(background="#d9d9d9")
        self.export_notes_button.configure(command=self.export_to_json)
        self.export_notes_button.configure(compound='left')
        self.export_notes_button.configure(cursor='hand2')
        self.export_notes_button.configure(disabledforeground="#a3a3a3")
        self.export_notes_button.configure(font="-family {Comic Sans MS} -size 11")
        self.export_notes_button.configure(foreground="#000000")
        self.export_notes_button.configure(highlightbackground="#d9d9d9")
        self.export_notes_button.configure(highlightcolor="black")
        self.export_notes_button.configure(pady="0")
        self.export_notes_button.configure(relief="flat")
        self.export_notes_button.configure(text='''Export Notes''')
        ToolTip(self.export_notes_button, "Export all your notes to a JSON file format ;-)", font=_tooltip_font)

        self.import_notes_button = tk.Button(self.settings_window)
        self.import_notes_button.place(relx=0.574, rely=0.476, height=28, width=139)
        self.import_notes_button.configure(activebackground="#b5b5b5")
        self.import_notes_button.configure(activeforeground="black")
        self.import_notes_button.configure(background="#d9d9d9")
        self.import_notes_button.configure(command=self.import_from_json)
        self.import_notes_button.configure(compound='left')
        self.import_notes_button.configure(cursor='hand2')
        self.import_notes_button.configure(disabledforeground="#a3a3a3")
        self.import_notes_button.configure(font="-family {Comic Sans MS} -size 11")
        self.import_notes_button.configure(foreground="#000000")
        self.import_notes_button.configure(highlightbackground="#d9d9d9")
        self.import_notes_button.configure(highlightcolor="black")
        self.import_notes_button.configure(pady="0")
        self.import_notes_button.configure(relief="flat")
        self.import_notes_button.configure(text='''Import Notes''')
        ToolTip(self.import_notes_button, "Import notes from a JSON file format :O", font=_tooltip_font)

        self.return_button = tk.Button(self.settings_window)
        self.return_button.place(relx=0.393, rely=0.769, height=28, width=79)
        self.return_button.configure(activebackground="#b5b5b5")
        self.return_button.configure(activeforeground="black")
        self.return_button.configure(background="#d9d9d9")
        self.return_button.configure(command=self.go_back)
        self.return_button.configure(compound='left')
        self.return_button.configure(cursor='hand2')
        self.return_button.configure(disabledforeground="#a3a3a3")
        self.return_button.configure(font="-family {Comic Sans MS} -size 11 -underline 1")
        self.return_button.configure(foreground="#000000")
        self.return_button.configure(highlightbackground="#d9d9d9")
        self.return_button.configure(highlightcolor="black")
        self.return_button.configure(pady="0")
        self.return_button.configure(relief="flat")
        self.return_button.configure(text='''Return''')

        self.dev_name_label = tk.Label(self.settings_window)
        self.dev_name_label.place(relx=0.0, rely=0.899, height=23, width=105)
        self.dev_name_label.configure(anchor='w')
        self.dev_name_label.configure(background="#d9d9d9")
        self.dev_name_label.configure(compound='left')
        self.dev_name_label.configure(disabledforeground="#a3a3a3")
        self.dev_name_label.configure(font="-family {Comic Sans MS} -size 9")
        self.dev_name_label.configure(foreground="#000000")
        self.dev_name_label.configure(text='''rikkadesu ©2023''')
        ToolTip(self.dev_name_label, "I love my projects!", font=_tooltip_font, delay=1.5)

    def start_move(self, event):
        self.x_cursor = event.x
        self.y_cursor = event.y

    def on_drag(self, event):
        self.x_mouse = event.x_root
        self.y_mouse = event.y_root

        new_x = self.x_mouse - self.x_cursor
        new_y = self.y_mouse - self.y_cursor

        self.settings_window.geometry(f"+{new_x}+{new_y}")

    def load_settings(self):
        _ = self  # Ignore
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                settings = json.load(file)
                return settings
        else:
            messagebox.showwarning("Something went wrong :(", "Configurations failed to load. Default values will be"
                                                              " used :)")
            with open("settings.json", "w") as settings:
                settings_data = {
                    "autosave": 1
                }
                json.dump(settings_data, settings)

    def save_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "w") as settings:
                json.dump(self.settings, settings)

    def delete_categories(self):
        self.settings_window.withdraw()
        delete_cat = DeleteCategoryInterface(self.parent_object, self.settings_window)
        self.delete_categories_button.configure(state="disabled")
        delete_cat.delete_category_window.wait_window()
        self.settings_window.deiconify()
        self.delete_categories_button.configure(state="normal")

    def toggle_autosave(self):
        if self.settings.get("autosave"):
            self.settings["autosave"] = 0
            self.autosave_button.configure(text="Autosave - Off")
        else:
            self.settings["autosave"] = 1
            self.autosave_button.configure(text="Autosave - On")

        self.save_settings()

    def export_to_json(self):
        file_path = filedialog.asksaveasfile(parent=self.settings_window,
                                             title="Please select where to save your notes export",
                                             filetypes=(("JSON file", "json"),))
        if file_path:
            try:
                ndb.export_to_json(self.settings.get("version"), file_path.name)
                messagebox.showinfo("Success", f"Your notes was exported to {file_path.name}.json")
            except Exception:
                messagebox.showwarning("Export failed", "Something went wrong, exporting was not successful :(")
        self.settings_window.focus_set()

    def import_from_json(self):
        file_path = filedialog.askopenfile(parent=self.settings_window, title="Select import file",
                                           filetypes=(("JSON file", ".json"),))
        if file_path:
            try:
                success = ndb.import_from_json(file_path.name, self.settings.get("version"))
                messagebox.showinfo("Success", "Notes and Categories were imported successfully!") if success else None
                self.parent_object.notes_info = ndb.get_all_notes()
                self.parent_object.update_notes()
            except Exception:
                messagebox.showwarning("Invalid file", "Please select the correct import file :(")
        self.settings_window.focus_set()

    def go_back(self):
        self.settings_window.destroy()