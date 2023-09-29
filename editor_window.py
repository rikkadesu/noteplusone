import string
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading
import time
import json
import os

import notes_database as ndb
from category_window import CategoryListInterface


class EditorInterface:
    def __init__(self, note_info, parent_object):
        # Note's basic information ====================================================================================
        self.note_info_object = note_info
        self.note_id: int = self.note_info_object.note_id
        self.note_category: tuple = self.note_info_object.note_category  # ex: (0, "None") where [0] is id and [1] is the name
        self.note_title: str = self.note_info_object.note_title
        self.note_text: str = self.note_info_object.note_text
        self.note_creation_date: str = self.note_info_object.note_creation_date
        # End note's basic information ================================================================================

        # Modify history ==============================================================================================
        self.MAX_MODIFY_HISTORY = 50
        self.modify_title_history_undo = []
        self.modify_title_history_redo = []
        self.modify_text_history_undo = []
        self.modify_text_history_redo = []
        self.is_saved = True
        self.focused_widget = "note_text"
        # End Modify history ==========================================================================================

        self.editor_frame = tk.Frame()
        self.note_info = note_info
        self.parent_object = parent_object
        self.parent_window = parent_object.main_window
        self.parent_window.protocol("WM_DELETE_WINDOW", self.closing_window)

        # Settings
        self.settings = self.load_settings()
        self.autosave_thread = None
        self.autosave_enabled = threading.Event()
        self.autosave_enabled.set() if self.settings["autosave"] else self.autosave_enabled.clear()
        # End Settings

        self.note_title_entry = tk.Entry(self.editor_frame)
        self.note_title_entry.place(relx=0.019, rely=0.022, height=30, relwidth=0.959)
        self.note_title_entry.bind("<FocusIn>", lambda e: self.get_latest_focus(self.note_title_entry))
        self.note_title_entry.bind("<Control-s>", self.save_note)
        self.note_title_entry.bind("<Control-z>", self.undo_text_changes)
        self.note_title_entry.bind("<Control-y>", self.redo_text_changes)
        self.note_title_entry.bind("<Key>", self.update_on_editor)
        self.note_title_entry.configure(background="white")
        self.note_title_entry.configure(disabledforeground="#a3a3a3")
        self.note_title_entry.configure(font="-family {Comic Sans MS} -size 14")
        self.note_title_entry.configure(foreground="#000000")
        self.note_title_entry.configure(insertbackground="black")
        self.note_title_entry.delete(0, tk.END)
        self.note_title_entry.insert(tk.END, self.note_title)

        self.note_text_entry = tk.Text(self.editor_frame)
        self.note_text_entry.place(relx=0.019, rely=0.11, relheight=0.794, relwidth=0.959)
        self.note_text_entry.bind("<FocusIn>", lambda e: self.get_latest_focus(self.note_text_entry))
        self.note_text_entry.bind("<Control-s>", self.save_note)
        self.note_text_entry.bind("<Control-z>", self.undo_text_changes)
        self.note_text_entry.bind("<Control-y>", self.redo_text_changes)
        self.note_text_entry.bind("<Key>", self.update_on_editor)
        self.note_text_entry.configure(background="white")
        self.note_text_entry.configure(font="-family {Comic Sans MS} -size 14")
        self.note_text_entry.configure(foreground="black")
        self.note_text_entry.configure(highlightbackground="#d9d9d9")
        self.note_text_entry.configure(highlightcolor="black")
        self.note_text_entry.configure(insertbackground="black")
        self.note_text_entry.configure(selectbackground="#c4c4c4")
        self.note_text_entry.configure(selectforeground="black")
        self.note_text_entry.configure(wrap="word")
        self.note_text_entry.delete(1.0, tk.END)
        self.note_text_entry.focus_set()
        self.note_text_entry.insert(tk.END, self.note_text)

        self.undo_button = tk.Button(self.editor_frame)
        self.undo_button.place(relx=0.437, rely=0.921, height=28, width=29)
        self.undo_button.configure(activebackground="#b5b5b5")
        self.undo_button.configure(activeforeground="black")
        self.undo_button.configure(background="#d9d9d9")
        self.undo_button.configure(command=self.undo_text_changes)
        self.undo_button.configure(compound='center')
        self.undo_button.configure(disabledforeground="#a3a3a3")
        self.undo_button.configure(font="-family {Comic Sans MS} -size 14 -weight bold")
        self.undo_button.configure(foreground="#000000")
        self.undo_button.configure(highlightbackground="#d9d9d9")
        self.undo_button.configure(highlightcolor="black")
        self.undo_button.configure(pady="0")
        self.undo_button.configure(state="disabled")
        self.undo_button.configure(text='''<''')

        self.redo_button = tk.Button(self.editor_frame)
        self.redo_button.place(relx=0.509, rely=0.921, height=28, width=29)
        self.redo_button.configure(activebackground="#b5b5b5")
        self.redo_button.configure(activeforeground="black")
        self.redo_button.configure(background="#d9d9d9")
        self.redo_button.configure(command=self.redo_text_changes)
        self.redo_button.configure(compound='left')
        self.redo_button.configure(disabledforeground="#a3a3a3")
        self.redo_button.configure(font="-family {Comic Sans MS} -size 14 -weight bold")
        self.redo_button.configure(foreground="#000000")
        self.redo_button.configure(highlightbackground="#d9d9d9")
        self.redo_button.configure(highlightcolor="black")
        self.redo_button.configure(pady="0")
        self.redo_button.configure(state="disabled")
        self.redo_button.configure(text='''>''')

        self.category_button = tk.Button(self.editor_frame)
        self.category_button.place(relx=0.136, rely=0.921, height=28, width=144)
        self.category_button.configure(activebackground="#b5b5b5")
        self.category_button.configure(activeforeground="black")
        self.category_button.configure(background="#d9d9d9")
        self.category_button.configure(command=self.select_category)
        self.category_button.configure(compound='left')
        self.category_button.configure(disabledforeground="#a3a3a3")
        self.category_button.configure(font="-family {Comic Sans MS} -size 9")
        self.category_button.configure(foreground="#000000")
        self.category_button.configure(highlightbackground="#d9d9d9")
        self.category_button.configure(highlightcolor="black")
        self.category_button.configure(pady="0")
        self.category_button.configure(text=self.note_category[1])

        self.back_button = tk.Button(self.editor_frame)
        self.back_button.place(relx=0.019, rely=0.921, height=28, width=49)
        self.back_button.configure(activebackground="#b5b5b5")
        self.back_button.configure(activeforeground="black")
        self.back_button.configure(background="#d9d9d9")
        self.back_button.configure(command=self.back_to_home)
        self.back_button.configure(compound='left')
        self.back_button.configure(disabledforeground="#a3a3a3")
        self.back_button.configure(font="-family {Comic Sans MS} -size 9")
        self.back_button.configure(foreground="#000000")
        self.back_button.configure(highlightbackground="#d9d9d9")
        self.back_button.configure(highlightcolor="black")
        self.back_button.configure(pady="0")
        self.back_button.configure(text='''Back''')

        self.save_button = tk.Button(self.editor_frame)
        self.save_button.place(relx=0.883, rely=0.921, height=28, width=49)
        self.save_button.configure(activebackground="#b5b5b5")
        self.save_button.configure(activeforeground="black")
        self.save_button.configure(background="#d9d9d9")
        self.save_button.configure(command=self.save_note)
        self.save_button.configure(compound='left')
        self.save_button.configure(disabledforeground="#a3a3a3")
        self.save_button.configure(font="-family {Comic Sans MS} -size 9")
        self.save_button.configure(foreground="#000000")
        self.save_button.configure(highlightbackground="#d9d9d9")
        self.save_button.configure(highlightcolor="black")
        self.save_button.configure(pady="0")
        self.save_button.configure(state="disabled")
        self.save_button.configure(text='''Save''')

        self.start_autosave()

    def load_settings(self):
        _ = self  # Ignore
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings:
                return json.load(settings)
        else:
            messagebox.showwarning("Something went wrong :(", "Configurations failed to load. Default values will be"
                                                              " used :)")
            with open("settings.json", "w") as settings:
                settings_data = {
                    "autosave": 1
                }
                json.dump(settings_data, settings)

    def get_latest_focus(self, widget):
        if widget == self.note_text_entry:
            self.focused_widget = "note_text"
            self.undo_button.configure(command=self.undo_text_changes)
            self.redo_button.configure(command=self.redo_text_changes)
            self.note_text_entry.bind("<Control-z>", self.undo_text_changes)
            self.note_text_entry.bind("<Control-y>", self.redo_text_changes)
            self.note_title_entry.unbind("<Control-z>")
            self.note_title_entry.unbind("<Control-y>")

            if len(self.modify_text_history_undo) == 0:
                self.undo_button.configure(state="disabled")
            else:
                self.undo_button.configure(state="normal")
            if len(self.modify_text_history_redo) != 0:
                self.redo_button.configure(state="normal")
            else:
                self.redo_button.configure(state="disabled")

        elif widget == self.note_title_entry:
            self.focused_widget = "note_title"
            self.undo_button.configure(command=self.undo_title_changes)
            self.redo_button.configure(command=self.redo_title_changes)
            self.note_title_entry.bind("<Control-z>", self.undo_title_changes)
            self.note_title_entry.bind("<Control-y>", self.redo_title_changes)
            self.note_text_entry.unbind("<Control-z>")
            self.note_text_entry.unbind("<Control-y>")

            if len(self.modify_title_history_undo) == 0:
                self.undo_button.configure(state="disabled")
            else:
                self.undo_button.configure(state="normal")
            if len(self.modify_title_history_redo) != 0:
                self.redo_button.configure(state="normal")
            else:
                self.redo_button.configure(state="disabled")

    def save_history(self):
        """ This method is responsible for saving modification history for the undo functionality. The length of the
            modification history can be changed depending on what is set by either the developer or the user if the
            developer made the users able to change this value. """

        if self.focused_widget == "note_text":
            if len(self.modify_text_history_undo) == self.MAX_MODIFY_HISTORY:
                self.modify_text_history_undo.pop(0)

            note_text = self.note_text_entry.get("1.0", "end-1c")
            if note_text != "":
                self.modify_text_history_undo.append(note_text)

        elif self.focused_widget == "note_title":
            if len(self.modify_title_history_undo) == self.MAX_MODIFY_HISTORY:
                self.modify_title_history_undo.pop(0)

            note_title = self.note_title_entry.get()
            if note_title != "":
                self.modify_title_history_undo.append(note_title)

    def update_on_editor(self, event=None):
        """ This method is used as a process bound to the Text widget. Every time the Text widget receives a Key event,
            this method will be called and update related functions like button states and saving text modification
            histories. """

        _ = event  # Ignore
        try:
            pressed = event.keysym
            if str.isalnum(pressed) or pressed in string.punctuation:
                self.save_button.configure(state="normal")
                self.undo_button.configure(state="normal")
                self.redo_button.configure(state="normal")
                self.is_saved = False
                self.save_history()
        except AttributeError as AE:
            print(f"Error: {str(AE).title()}. No need to worry though. Just doing my keybind job :)")

    def undo_text_changes(self, event=None):
        """ This method is a command for the undo button. This works by saving a modification history to a list.
            Once this method is called, the text widget will take the latest value in the undo history list.

            Algorithm explanation:
            - When the method is called, a variable will take the latest version from the undo history list using pop().
            - The method also take into account the redo functionality, so before changing the contents of the Text
              widget, its current values will be appended to a redo history list.
            - The latest retrieved modification will then be used to overwrite the current values in the Text widget to
              simulate an undo process.
            - Some pieces of the algorithm like the self.update_on_editor and the conditional statements are added for
              checks if further undo and redo functions can be done. """

        _ = event  # Ignore
        if len(self.modify_text_history_undo) != 0:
            last_modification = self.modify_text_history_undo.pop(-1)
            self.modify_text_history_redo.append(self.note_text_entry.get("1.0", "end-1c"))

            self.note_text_entry.delete("1.0", "end")
            self.note_text_entry.insert("1.0", last_modification)
            self.update_on_editor()
            self.save_button.configure(state="normal")

            if len(self.modify_text_history_undo) == 0:
                self.undo_button.configure(state="disabled")
            if len(self.modify_text_history_redo) != 0:
                self.redo_button.configure(state="normal")

    def redo_text_changes(self, event=None):
        """ This method is a command for the redo button. This works by saving a modification history to a list.
            Once this method is called, the text widget will take the latest value in the redo history list.

            Algorithm explanation:
            - When the method is called, a variable will take the latest version from the redo history list using pop().
            - The method also take into account the undo functionality, so before changing the contents of the Text
              widget, its current values will be appended to an undo history list.
            - The latest retrieved modification will then be used to overwrite the current values in the Text widget to
              simulate a redo process.
            - Some pieces of the algorithm like the self.update_on_editor and the conditional statements are added for
              checks if further undo and redo functions can be done. """

        _ = event  # Ignore
        if len(self.modify_text_history_redo) != 0:
            last_modification = self.modify_text_history_redo.pop(-1)
            self.modify_text_history_undo.append(self.note_text_entry.get("1.0", "end-1c"))

            self.note_text_entry.delete("1.0", "end")
            self.note_text_entry.insert("1.0", last_modification)
            self.update_on_editor()
            self.save_button.configure(state="normal")

            if len(self.modify_text_history_redo) == 0:
                self.redo_button.configure(state="disabled")
            if len(self.modify_text_history_undo) != 0:
                self.undo_button.configure(state="normal")

    def undo_title_changes(self, event=None):
        """ This method is a command for the undo button. This works by saving a modification history to a list.
            Once this method is called, the text widget will take the latest value in the undo history list.

            Algorithm explanation:
            - When the method is called, a variable will take the latest version from the undo history list using pop().
            - The method also take into account the redo functionality, so before changing the contents of the Text
              widget, its current values will be appended to a redo history list.
            - The latest retrieved modification will then be used to overwrite the current values in the Text widget to
              simulate an undo process.
            - Some pieces of the algorithm like the self.update_on_editor and the conditional statements are added for
              checks if further undo and redo functions can be done. """

        _ = event  # Ignore
        if len(self.modify_title_history_undo) != 0:
            last_modification = self.modify_title_history_undo.pop(-1)
            self.modify_title_history_redo.append(self.note_title_entry.get())

            self.note_title_entry.delete(0, tk.END)
            self.note_title_entry.insert(0, last_modification)
            self.update_on_editor()
            self.save_button.configure(state="normal")

            if len(self.modify_title_history_undo) == 0:
                self.undo_button.configure(state="disabled")
            if len(self.modify_title_history_redo) != 0:
                self.redo_button.configure(state="normal")

    def redo_title_changes(self, event=None):
        """ This method is a command for the redo button. This works by saving a modification history to a list.
            Once this method is called, the text widget will take the latest value in the redo history list.

            Algorithm explanation:
            - When the method is called, a variable will take the latest version from the redo history list using pop().
            - The method also take into account the undo functionality, so before changing the contents of the Text
              widget, its current values will be appended to an undo history list.
            - The latest retrieved modification will then be used to overwrite the current values in the Text widget to
              simulate a redo process.
            - Some pieces of the algorithm like the self.update_on_editor and the conditional statements are added for
              checks if further undo and redo functions can be done. """

        _ = event  # Ignore
        if len(self.modify_title_history_redo) != 0:
            last_modification = self.modify_title_history_redo.pop(-1)
            self.modify_title_history_undo.append(self.note_title_entry.get())

            self.note_title_entry.delete(0, tk.END)
            self.note_title_entry.insert(0, last_modification)
            self.update_on_editor()
            self.save_button.configure(state="normal")

            if len(self.modify_title_history_redo) == 0:
                self.redo_button.configure(state="disabled")
            if len(self.modify_title_history_undo) != 0:
                self.undo_button.configure(state="normal")

    def select_category(self):
        cat_window = CategoryListInterface(self.parent_object, self.parent_window, True)
        self.category_button.configure(state="disabled")
        cat_window.category_window.wait_window()
        self.category_button.configure(state="normal")
        selected_category = cat_window.category_id
        try:
            if selected_category:
                self.note_category = self.note_info.note_category = selected_category
                ndb.change_note_category(self.note_category[0], self.note_id) if self.note_id else None
                self.category_button.configure(text=self.note_category[1])
                category_button_text = f"{self.note_title}\nCategory: {self.note_category[1]}\n" \
                                       f"Last Modified: {self.note_creation_date}"
                self.note_info.button.configure(text=category_button_text)
        except TypeError:
            print("User returned without selecting a filter. No need to worry.")

    def back_to_home(self):
        """ This method takes into account the possibility of going back to the homepage before saving their work.
            Users will be prompt to save their work before returning. """

        if not self.is_saved:
            proceed_save = messagebox.askyesno("Heads up!", "Changes are not saved yet, do you want to save "
                                                            "before returning to home?")
            if proceed_save:
                self.save_note()

        if self.parent_object.is_category_filtered:
            selected_category = self.parent_object.current_category
            self.parent_object.notes_info = ndb.get_filtered_notes(selected_category[0])
        else:
            self.parent_object.notes_info = ndb.get_all_notes()

        self.autosave_enabled.clear()
        self.editor_frame.pack_forget()
        self.parent_window.protocol("WM_DELETE_WINDOW", "")
        self.parent_object.update_notes()
        self.parent_object.main_frame.pack(expand=True, fill="both")

    def save_note(self, event=None, autosave=False):
        """ This method works by taking all necessary details and saving them in their respective variables.
            A method from the notes_database.py is then called to save these details in the database. """

        _ = event  # Ignore
        if self.is_saved:
            return

        if self.note_title_entry.get() == "":
            self.note_title = self.note_info.note_title = self.note_text_entry.get("1.0", "1.end")
            self.note_title_entry.insert(0, self.note_title)
        else:
            self.note_title = self.note_info.note_title = self.note_title_entry.get()
        self.note_text = self.note_info.note_text = self.note_text_entry.get("1.0", "end-1c")
        self.note_creation_date = self.note_info.note_creation_date = datetime.now()

        if self.note_title != "" or self.note_text != "":
            if self.note_id is not None:
                ndb.save_note(self.note_id, self.note_title, self.note_text, self.note_category[0],
                              self.note_creation_date)
            else:
                note_id = ndb.add_note(note_category=self.note_category, note_title=self.note_title,
                                       note_text=self.note_text, creation_date=self.note_creation_date)

                self.note_id = self.note_info.note_id = note_id
                self.note_info.button.configure(text=self.note_title)

                is_not_filtered = not self.parent_object.is_category_filtered
                is_same_category_filter = self.parent_object.current_category == self.note_category[1]
                if any((is_not_filtered, is_same_category_filter)):
                    self.parent_object.notes_list_height += 100
                    self.parent_object.update_size(None)
                    self.parent_object.notes_list.append(self.note_info)
                    self.note_info.frame.pack(expand=True, fill="both")
                    self.parent_object.notes_canvas.yview_moveto(999)
        else:
            proceed_saving = messagebox.askyesno("Wait up!", "Saving a note without any contents will delete "
                                                             "the note instead. Continue?")
            if proceed_saving:
                ndb.delete_note(self.note_id)
                self.note_info.frame.pack_forget()
                self.parent_object.notes_list_height -= 100
                self.parent_object.update_size()
                self.editor_frame.pack_forget()
                self.parent_object.main_window.protocol("WM_DELETE_WINDOW")
                self.parent_object.main_frame.pack(expand=True, fill="both")
            return

        self.save_button.configure(state="disabled")
        button_text = f"{self.note_title}\nCategory: {self.note_category[1]}\n" \
                      f"Last Modified: {self.note_creation_date.strftime('%B %d, %Y %I:%M:%S %p')}"
        self.note_info.button.configure(text=button_text)
        messagebox.showinfo("Success!", "Your changes have been saved.") if not autosave else None
        self.is_saved = True

    def autosave_timer(self):
        try:
            def autosave():
                if self.settings["autosave"]:
                    self.save_note(autosave=True)
                    print("Autosaved")

            autosave_interval = 5
            for i in range(6):
                time.sleep(autosave_interval) if self.autosave_enabled.is_set() else None
            while self.autosave_enabled.is_set():
                autosave()
                for i in range(6):
                    time.sleep(autosave_interval) if self.autosave_enabled.is_set() else None
        except RuntimeError:
            pass

    def start_autosave(self):
        self.autosave_thread = threading.Thread(target=self.autosave_timer)
        self.autosave_thread.start()

    def closing_window(self, event=None):
        """ This method takes into account the possibility of closing the app window without saving their work.
            Users will be prompt to save their work before returning. """

        _ = event  # Ignore
        if not self.is_saved:
            proceed_save = messagebox.askyesnocancel("Heads up!", "Changes are not saved yet, do you want to save "
                                                     "before closing the program?")
            if proceed_save is None:
                return
            elif proceed_save:
                self.save_note()

        self.parent_object.main_window.destroy()
        self.autosave_enabled.clear()
