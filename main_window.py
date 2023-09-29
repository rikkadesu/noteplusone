import _tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import notes_database as ndb
import datetime
import json
import os

from editor_window import EditorInterface
from category_window import CategoryListInterface
from settings_window import SettingsInterface
from sort_window import SortNotesInterface
from tooltip import ToolTip

APP_VERSION = "1.0.1"


class MainInterface:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("515x456+569+146")
        self.main_window.minsize(515, 456)
        self.main_window.maxsize(1924, 1061)
        self.main_window.resizable(False, True)
        self.main_window.title("Notes += 1")
        self.main_window.configure(background="#d9d9d9")
        self.main_window.configure(highlightbackground="#d9d9d9")
        self.main_window.configure(highlightcolor="black")

        self.main_frame = tk.Frame(master=self.main_window, bg="#d9d9d9")
        self.main_frame.pack(expand=True, fill="both")

        self.main_header = tk.Label(self.main_frame)
        self.main_header.place(relx=0.019, y=5, height=81, width=494)
        self.main_header.configure(activebackground="#f9f9f9")
        self.main_header.configure(background="#d9d9d9")
        self.main_header.configure(compound='left')
        self.main_header.configure(disabledforeground="#a3a3a3")
        self.main_header.configure(font="-family {Comic Sans MS} -size 30 -weight bold")
        self.main_header.configure(foreground="#000000")
        self.main_header.configure(highlightbackground="#d9d9d9")
        self.main_header.configure(highlightcolor="black")
        self.main_header.configure(text='''Notes += 1''')
        ToolTip(self.main_header, "What do you think of this name? :D", delay=2, font="-family {Comic Sans MS} -size 9")

        # Sort Info ===================================================================================================
        self.are_notes_sorted = True
        self.sort_notes_by = "modified date"
        self.sort_notes_type = "desc"
        # End Sort Info ===============================================================================================

        # Categories Info =============================================================================================
        self.is_category_filtered = False
        self.categories = ndb.get_categories()
        self.current_category = self.categories[0][1]
        self.category_label = tk.Label(self.main_frame)
        self.cat_label_text = f"Category: {self.current_category}"
        self.category_label.configure(text=self.cat_label_text, font="-family {Comic Sans MS} -size 10 -weight bold")
        self.category_label.configure(bg="#d9d9d9")
        self.category_label.place(x=2, y=75)
        ToolTip(self.category_label, "Current category filter :P", font="-family {Comic Sans MS} -size 9")
        # End Categories Info =========================================================================================

        # Delete Mode =================================================================================================
        self.delete_mode = False
        self.delete_mode_label = tk.Label(self.main_frame)
        self.delete_mode_label.configure(text="Delete Mode", font="-family {Comic Sans MS} -size 10 -weight bold")
        self.delete_mode_label.configure(bg="#d9d9d9")
        # End Delete Mode =============================================================================================

        # Buttons Info ================================================================================================
        """ self.buttons_info -> List of tuples of information for the function buttons. Includes their name and their
                                 command method.
            self.button_list_height -> The height of the frame where the buttons are displayed. Adjusts based on the
                                       number of buttons available. """

        self.buttons_info = [("Create", self.create_new, "Create a new note :)"),
                             ("Sort", self.sort_notes, "Choose how you want to sort your notes!"),
                             ("Category", self.filter_categories, "Filter notes based on their category :O"),
                             ("Delete", self.delete_notes, "Enabling lets you delete notes XD!"),
                             ("Settings", self.app_settings, "See what else you can do...")]
        self.buttons_list: list[tk.Button] = []
        self.button_list_height = len(self.buttons_info) * 70
        # End Buttons Info ============================================================================================

        # Notes Info ==================================================================================================
        """ self.notes_info -> List of all available notes from the database, used to create self.notes_list.
            self.notes_list -> List of Note objects, might be used for note deletion.
            self.notes_list_height -> The height of the frame where the notes are displayed. Adjusts based on the
                                      number of notes available. """

        self.notes_info: list = ndb.get_all_notes()
        self.notes_list: list = []
        self.notes_list_height: int = len(self.notes_info) * 100
        # End Notes Info ==============================================================================================

        # Notes Field =================================================================================================
        self.enable_notes_scroll = False
        self.notes_base_frame = tk.Frame(master=self.main_frame, relief="ridge", borderwidth=3)
        self.notes_base_frame.place(x=2, y=100, relheight=0.774, relwidth=0.86)

        self.notes_canvas = tk.Canvas(self.notes_base_frame)
        self.notes_canvas.configure(scrollregion=(0, 0, 443, self.notes_list_height))
        self.notes_canvas.configure(insertbackground="black")
        self.notes_canvas.configure(selectbackground="#c4c4c4")
        self.notes_canvas.configure(selectforeground="black")
        self.notes_canvas.pack(expand=True, fill="both")

        self.notes_frame = tk.Frame(master=self.notes_canvas)
        self.notes_canvas.bind("<Configure>", self.update_size)

        self.notes_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        # End Notes Field =============================================================================================

        # Buttons Field ===============================================================================================
        self.enable_buttons_scroll = False
        self.buttons_base_frame = tk.Frame(master=self.main_frame, relief="ridge", borderwidth=3)
        self.buttons_base_frame.place(relx=0.856, y=100, relheight=0.774, width=73)

        self.buttons_canvas = tk.Canvas(self.buttons_base_frame)
        self.buttons_canvas.configure(scrollregion=(0, 0, 73, self.button_list_height))
        self.buttons_canvas.configure(insertbackground="black")
        self.buttons_canvas.configure(selectbackground="#c4c4c4")
        self.buttons_canvas.configure(selectforeground="black")
        self.buttons_canvas.pack(expand=True, fill="both")

        self.buttons_frame = tk.Frame(master=self.buttons_canvas)
        self.buttons_canvas.bind("<Configure>", self.update_size)

        self.buttons_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        # End Buttons Field ===========================================================================================

        ndb.initialize_database()  # Initializes the database on first setup
        self.initialize_settings()  # Initializes app configurations
        self.create_buttons()  # Displays all available function buttons
        self.sort()  # Sorts the notes immediately
        self.display_all_notes()  # Displays all the notes found in the database
        self.main_window.mainloop()  # Starts the program

    def display_all_notes(self) -> None:
        """ This method displays all queried notes from the database stored in self.notes_info variable
            by creating a Note object. """
        for note in self.notes_info:
            note = Note(note, self.notes_frame, self)
            note.frame.pack(expand=True, fill="both")
            self.notes_list.append(note)

    def on_mousewheel(self, event):
        """ This method is bound to canvas' MouseWheel event. This method checks where the
            user cursor is currently placed at and only scroll the canvas hovered by the cursor. """

        # Get the mouse position relative to the root window
        x, y = self.main_window.winfo_pointerx(), self.main_window.winfo_pointery()

        # Check if the cursor is over Canvas A or Canvas B
        if self.notes_canvas.winfo_rootx() <= x < self.notes_canvas.winfo_rootx() + self.notes_canvas.winfo_width():
            if self.notes_canvas.winfo_rooty() <= y < self.notes_canvas.winfo_rooty() + self.notes_canvas.winfo_height():
                if self.enable_notes_scroll:
                    self.notes_canvas.yview_scroll(-1 * (event.delta // 120), "units")  # Scroll Frame A
                    # print("Scrolling Notes")
        elif self.buttons_canvas.winfo_rootx() <= x < self.buttons_canvas.winfo_rootx() + self.buttons_canvas.winfo_width():
            if self.buttons_canvas.winfo_rooty() <= y < self.buttons_canvas.winfo_rooty() + self.buttons_canvas.winfo_height():
                if self.enable_buttons_scroll:
                    self.buttons_canvas.yview_scroll(-1 * (event.delta // 120), "units")  # Scroll Frame B
                    # print("Scrolling Buttons")

    def update_size(self, event=None):
        """ This method updates the size of the frames based on the current height of the program window.
            This method also check if the items from self.notes_canvas and self.buttons_canvas fit in the
            display and will only allow scrolling to the canvas that cannot fit all items. """

        _ = event
        # Checks if the items on the buttons does not fit
        if self.button_list_height >= self.buttons_canvas.winfo_height():
            # If all items do not fit in the canvas, allow scrolling
            self.enable_buttons_scroll = True
        else:
            # If all items fit in the canvas, stops the scrolling
            self.enable_buttons_scroll = False

        self.buttons_canvas.create_window((0, 0), window=self.buttons_frame, anchor=tk.NW,
                                          width=self.buttons_canvas.winfo_width(),
                                          height=self.button_list_height)

        # Checks if the items on notes does not fit
        if self.notes_list_height >= self.notes_canvas.winfo_height():
            # Checks if the items on the notes does not fit
            self.enable_notes_scroll = True
        else:
            # If all items fit in the canvas, stops the scrolling
            self.enable_notes_scroll = False

        self.notes_canvas.create_window((0, 0), window=self.notes_frame, anchor=tk.NW,
                                        width=self.notes_canvas.winfo_width(),
                                        height=self.notes_list_height)

        # Adjusts the scrollregion if new item is added
        self.notes_canvas.configure(scrollregion=(0, 0, 443, self.notes_list_height))
        self.buttons_canvas.configure(scrollregion=(0, 0, 73, self.button_list_height))

    def create_buttons(self) -> None:
        """ Creates and displays function buttons found in the right sidebar of the app. """

        for button in self.buttons_info:
            message = button[2]

            frame = tk.Frame(self.buttons_frame)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)

            button = tk.Button(master=frame, text=button[0], command=button[1], activebackground="#b5b5b5")
            button.configure(disabledforeground="#a3a3a3")
            button.grid(row=0, column=0, sticky="nsew")
            frame.pack(expand=True, fill="both")
            ToolTip(button, message, font="-family {Comic Sans MS} -size 10")

            self.buttons_list.append(button)

    # Legacy function code for the Create button
    #
    # def create_new(self):
    #     """ Command function for the Create button found in the right sidebar of the app. """
    #
    #     note_title = simpledialog.askstring("Title", "Enter a title. You can change"
    #                                                  " it later.")
    #
    #     category = simpledialog.askstring("Select category", "Enter category (insert int, "
    #                                                          "cancel if none): ") if note_title else None
    #     category = 0 if not category else category
    #     note_text = simpledialog.askstring("Note", "Enter your note. *This is just a sample*") if note_title else None
    #
    #     if note_text:
    #         current_date = datetime.datetime.now().strftime("%B %d %Y")
    #         ndb.add_note(note_category=category, note_title=note_title, note_text=note_text, creation_date=current_date)
    #         self.notes_info = ndb.get_all_notes()
    #         note_info = self.notes_info[-1]
    #         self.notes_list.append(Note(note_info, self.notes_frame, self))
    #         self.notes_list_height += 70
    #         self.update_size(None)
    #
    #         self.notes_canvas.yview_moveto(999)
    #
    #         self.main_frame.pack_forget()
    #         EditorInterface(self.notes_list[-1], self).editor_frame.pack(expand=True, fill="both")
    #     else:
    #         messagebox.showinfo("Cancelled", "Cancelled :(", master=self.main_frame)

    def create_new(self):
        """ This method creates a new instance of Note class and pass it to the EditorInterface class. """
        new_note = (None, 0, "", "", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        self.main_frame.pack_forget()
        new_note_object = Note(new_note, self.notes_frame, self)
        EditorInterface(new_note_object, self).editor_frame.pack(expand=True, fill="both")

    def delete_notes(self):
        """ This method enables deletion mode. It works by changing the command values of each
            Note object's button. When disabled, Note object's button's command will
            return to its original value. """

        if len(self.notes_list) == 0:
            return

        delete_button = self.find_function_button("Delete")
        self.delete_mode = True if not self.delete_mode else False

        if self.delete_mode:
            delete_button.configure(relief="sunken", bg="#b5b5b5")
            self.delete_mode_label.place(x=428, y=75)
            for note in self.notes_list:
                note.button.configure(command=note.delete_mode)
        else:
            self.delete_mode_label.place_forget()
            delete_button.configure(relief="raised", bg="SystemButtonFace")

            for note in self.notes_list:
                note.button.configure(command=note.show_note_text)

    def filter_categories(self):
        self.categories = ndb.get_categories()
        cat_window = CategoryListInterface(self, self.main_window)
        cat_window.category_window.wait_window()
        selected_category = cat_window.category_id

        if selected_category:
            if selected_category[1] != "None":
                self.is_category_filtered = True
                self.current_category = selected_category
                self.notes_info = ndb.get_filtered_notes(selected_category[0])
            else:
                self.is_category_filtered = False
                self.current_category = selected_category
                self.notes_info = ndb.get_all_notes()

            self.category_label.configure(text=f"Category: {self.current_category[1]}")
            self.update_notes()
            self.notes_canvas.yview_moveto(0)

    def sort(self):
        if self.are_notes_sorted:
            sorting_info = (self.sort_notes_by, self.sort_notes_type)
            self.notes_info = ndb.sort_notes(self.notes_info, sorting_info)
        elif self.is_category_filtered:
            self.notes_info = ndb.get_filtered_notes(self.categories[0])
        else:
            self.notes_info = ndb.get_all_notes()

    def sort_notes(self):
        try:
            sort_button = self.find_function_button("Sort")
            sort_button.configure(state="disabled")
            sort_window = SortNotesInterface(self, self.main_window)
            sort_window.sort_window.wait_window()
            sort_button.configure(state="normal")

            if not sort_window.is_returned:
                self.sort_notes_by = sort_window.sort_by
                self.sort_notes_type = sort_window.sort_type
                sorting_info = (self.sort_notes_by, self.sort_notes_type)

                self.notes_info = ndb.sort_notes(self.notes_info, sorting_info)
                self.are_notes_sorted = True
                self.update_notes()
                self.notes_canvas.yview_moveto(0)
        except _tkinter.TclError as error:
            print("\nMain window was closed while the sorting window is open. No need to worry.\n"
                  f"Error message: {str(error).capitalize()}")

    def update_notes(self):
        self.sort()

        for note in self.notes_list:
            note.frame.pack_forget()
        self.notes_list = []
        self.notes_list_height = len(self.notes_info) * 100
        self.display_all_notes()
        self.update_size()

    def app_settings(self):
        try:
            settings_button = self.find_function_button("Settings")

            settings_button.configure(state="disabled")
            settings = SettingsInterface(self, self.main_window)
            settings.settings_window.wait_window()
            settings_button.configure(state="normal")
        except _tkinter.TclError as error:
            print("\nMain window was closed while the settings is open. No need to worry.\n"
                  f"Error message: {str(error).capitalize()}")

    def initialize_settings(self):
        _ = self  # Ignore
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings:
                settings_data = json.load(settings)
                settings_data["version"] = APP_VERSION
            with open("settings.json", "w") as settings:
                json.dump(settings_data, settings)
        else:
            # This initializes the default settings on first setup or when the settings where missing
            with open("settings.json", "w") as settings:
                settings_data = {
                    "version": APP_VERSION,
                    "autosave": 1
                }
                json.dump(settings_data, settings)

    def find_function_button(self, to_find: str):
        """ Finds the specified button in the buttons info list based on its name. """
        for index, button_info in enumerate(self.buttons_info):
            if button_info[0] == to_find:
                return self.buttons_list[index]


class Note:
    def __init__(self, note_info, parent_window, parent_object):
        self.parent_window = parent_window
        self.parent_object: MainInterface = parent_object

        # Note's basic information ====================================================================================
        self.note_id: int = note_info[0]
        self.note_category_id: int = note_info[1]
        self.note_category = self.get_category_name()  # ex: (0, "None") where [0] is id and [1] is the name
        self.note_title: str = note_info[2]
        self.note_text: str = note_info[3]
        self.note_creation_date: datetime.datetime = datetime.datetime.strptime(note_info[4], "%Y-%m-%d %H:%M:%S.%f")
        # End note's basic information ================================================================================

        self.button = self.frame = None
        button_text = f"{self.note_title}\nCategory: {self.note_category[1]}\n" \
                      f"Last Modified: {self.note_creation_date.strftime('%B %d, %Y %I:%M:%S %p')}"

        style = ttk.Style()
        style.layout("Left.TButton", [
            ("Button.button", {"sticky": "nswe", "children": [
                ("Button.focus", {"sticky": "nswe", "children": [
                    ("Button.padding", {"sticky": "nswe", "children": [
                        ("Button.label", {"sticky": "w"})
                    ]})
                ]})
            ]})
        ])
        style.configure("Left.TButton", font="-family {Comic Sans MS} -size 12")

        self.frame = tk.Frame(self.parent_window)
        self.frame.configure(borderwidth=3, relief="ridge")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.button = ttk.Button(master=self.frame, text=button_text, takefocus=False, style="Left.TButton",
                                 command=self.show_note_text)
        self.button.grid(row=0, column=0, columnspan=2, sticky="nsew")
        # self.frame.pack(expand=True, fill="both") if self.note_id is not None else None

    def get_category_name(self):
        for category in self.parent_object.categories:
            if self.note_category_id == category[0]:
                return category

    def show_note_text(self) -> None:
        """ This method hides the main_frame (home) and creates an EditorInterface object to display
            the Note Editor interface. """

        self.parent_object.main_frame.pack_forget()
        EditorInterface(self, self.parent_object).editor_frame.pack(expand=True, fill="both")

    def delete_mode(self) -> None:
        def find_note_in_list() -> int:
            for index, note in enumerate(self.parent_object.notes_list):  # Finds the note in the list and pop it based on note id
                if self.note_id == note.note_id:
                    return index

        """ This method is set as the command value when deletion mode is enabled. This method works by
            first finding a matching note id from the notes_list in the MainInterface and then removing it
            using the pop() method of list. The returned value from pop() will then be forgotten using
            pack_forget(). A size adjustment method will be called to take into account the removal of a note.
            Finally, the note's data will be deleted from the database. Additional condition is set for when
            there is no notes left, deletion mode will be disabled. """

        choice = messagebox.askyesno(f"Delete {self.note_title}", f"Proceed deleting {self.note_title}?",
                                     parent=self.parent_window)
        if choice:
            list_index = find_note_in_list()
            this_note = self.parent_object.notes_list.pop(list_index)
            self.parent_object.notes_info.pop(list_index)
            this_note.frame.pack_forget() if this_note else None

            self.parent_object.notes_list_height -= 100  # Reduces the height of the frame
            self.parent_object.update_size(None)  # Updates the display
            ndb.delete_note(self.note_id)  # Deletes note in the database

            if len(self.parent_object.notes_list) == 0:
                # Disables deletion mode when no notes are left
                self.parent_object.delete_mode_label.place_forget()
                delete_button = self.parent_object.find_function_button("Delete")
                delete_button.configure(relief="raised", bg="SystemButtonFace")


def main():
    MainInterface()


if __name__ == '__main__':
    main()
