from datetime import datetime
from tkinter import messagebox
import sqlite3 as sql
import json
import os


def initialize_database() -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    # Create Categories Table
    sql_query = "CREATE Table IF NOT EXISTS Categories (" \
                "category_id integer PRIMARY KEY AUTOINCREMENT NOT NULL," \
                "category_name text NOT NULL" \
                ")"
    script.execute(sql_query)

    sql_query = "INSERT INTO Categories (category_id, category_name) " \
                "VALUES (0, \"None\")"
    script.execute(sql_query)

    # Create Notes Table
    sql_query = "CREATE Table IF NOT EXISTS Notes (" \
                "note_id integer PRIMARY KEY AUTOINCREMENT NOT NULL," \
                "note_category integer," \
                "note_title text NOT NULL," \
                "note_text text," \
                "creation_date text NOT NULL," \
                "FOREIGN KEY (note_category) REFERENCES Categories(category_id)" \
                ")"
    script.execute(sql_query)

    db.commit()
    script.close()
    db.close()


def get_all_notes() -> list:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = "select * from Notes"

    script.execute(sql_query)
    requests = script.fetchall()

    script.close()
    db.close()
    return requests


def get_filtered_notes(category: int) -> list:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = f"select * from Notes where note_category = {category}"

    script.execute(sql_query)
    requests = script.fetchall()

    script.close()
    db.close()
    return requests


def add_note(**kwargs) -> int:
    note_category = kwargs["note_category"]
    note_title = kwargs["note_title"]
    note_text = kwargs["note_text"]
    creation_date = kwargs["creation_date"]

    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = "insert into Notes (note_category, note_title, note_text, creation_date)" \
                f"values ({note_category[0]}, \"{note_title}\", \"{note_text}\", \"{creation_date}\")"
    script.execute(sql_query)
    note_id = script.lastrowid

    db.commit()
    script.close()
    db.close()
    return note_id


def save_note(note_id: int, note_title: str, note_text: str, category_id: int, creation_date: datetime) -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = "update Notes " \
                f"set note_category = {category_id}, note_title = \"{note_title}\", note_text = \"{note_text}\"," \
                f" creation_date = \"{creation_date}\" " \
                f"where note_id = {note_id}"
    script.execute(sql_query)

    db.commit()
    script.close()
    db.close()


def delete_note(note_id: int) -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = f"delete from Notes where note_id = {note_id}"
    script.execute(sql_query)

    db.commit()
    script.close()
    db.close()


def sort_notes(notes_info: list, sort_mode: tuple | None = None):
    sort_by, sort_type = sort_mode[0].lower(), sort_mode[1]
    sorted_list = None

    if sort_by == "category":
        category_map = get_categories()
        category_map = {k: v for k, v in category_map}
        sorted_list = sorted(notes_info, key=lambda x: category_map.get(x[1], ""))
    elif sort_by == "note title":
        sorted_list = sorted(notes_info, key=lambda x: x[2])
    elif sort_by == "modified date":
        sorted_list = sorted(notes_info, key=lambda x: x[-1])

    if sort_type == "desc":
        sorted_list.reverse()

    return sorted_list


def get_categories() -> list:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = "select * from Categories"
    script.execute(sql_query)
    requests = script.fetchall()

    script.close()
    db.close()
    return requests


def change_note_category(category_id: int, note_id: int) -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = "update Notes " \
                f"set note_category = {category_id} " \
                f"where note_id = {note_id}"
    script.execute(sql_query)

    db.commit()
    script.close()
    db.close()


def create_category(category_name: str) -> tuple:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = f"insert into Categories (category_name) values (\"{category_name}\")"
    script.execute(sql_query)
    category_id = script.lastrowid
    category_info = (category_id, category_name)

    db.commit()
    script.close()
    db.close()
    return category_info


def delete_category(category_id: int) -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    sql_query = f"delete from Categories where category_id = {category_id}"
    script.execute(sql_query)

    db.commit()
    script.close()
    db.close()


def export_to_json(app_version: str, filename: str) -> None:
    db = sql.connect("notes.db")
    script = db.cursor()

    notes_list: list[dict] = []
    all_notes: list = get_all_notes()
    for note in all_notes:
        note_dict = {
            "note_id": note[0],
            "note_category": note[1],
            "note_title": note[2],
            "note_text": note[3],
            "creation_date": note[4],
        }
        notes_list.append(note_dict)

    categories_list: list[dict] = []
    all_categories: list = get_categories()
    for category in all_categories:
        category_dict = {
            "category_id": category[0],
            "category_name": category[1]
        }
        categories_list.append(category_dict)

    file_directory = filename + ".json"
    with open(file_directory, "w") as export_file:
        values: dict = {
            "AppVersion": app_version,
            "Notes": notes_list,
            "Categories": categories_list
        }
        json.dump(values, export_file)

    script.close()
    db.close()


def import_from_json(file_name: str, app_version: str) -> bool:
    db = sql.connect("notes.db")
    script = db.cursor()

    with open(file_name, "r") as file:
        import_file: dict = json.load(file)
        if not import_file.get("AppVersion") == app_version:
            messagebox.showwarning("Import failed", "The provided json file is not supported in this version. "
                                                    "To prevent any issue, importing will not continue :)")
            return False

    if not os.path.exists("notes.db"):
        initialize_database()

    current_categories: list = get_categories()
    current_categories: list = [category[1].lower() for category in current_categories]
    imported_categories: list[dict] = import_file["Categories"]

    for imported_category in imported_categories:
        category_name = imported_category["category_name"]
        if not (category_name.lower() in current_categories):
            create_category(category_name)

    imported_notes: list = import_file["Notes"]
    all_categories: list = get_categories()

    for imported_note in imported_notes:
        title = imported_note["note_title"]
        text = imported_note["note_text"]
        date = imported_note["creation_date"]
        category_name = "None"
        category_id = (0, "None")

        # This loop takes the category name of the imported note based on the backed up Categories for synchronization
        for imported_category in imported_categories:
            if imported_category["category_id"] == imported_note["note_category"]:
                category_name = imported_category["category_name"]

        # This loop takes the category id of the category name from the current categories in the app
        for category in all_categories:
            if category[1].lower() == category_name.lower():
                category_id = category

        add_note(note_category=category_id, note_title=title, note_text=text, creation_date=date)

    db.commit()
    script.close()
    db.close()
    return True


if __name__ == "__main__":
    pass
    # notes = get_all_notes()
    # for note in notes:
    #     print(f"Title: {note[2].ljust(20)} | Text: {note[3]}")

    # delete_note(2)
    # print("Deleted")
    # notes = get_all_notes()
    # for note in notes:
    #     print(f"Title: {note[2].ljust(20)} | Text: {note[3]}")

    # categories = get_categories()
    # print(categories)

    # export_to_json("1.0.0")
    # import_from_json("notes_exported.json", "1.0.0")

    print(f"Unsorted: {get_all_notes()}")
    print(f'Sorted: {sort_notes(get_all_notes(), ("modified date", "asc"))}')