import tkinter as tk
import sqlite3 as sq
import datetime as dt
import bcrypt
#SQLITE3--------------------------------------------------------
connection = sq.connect("main.db")
cursor = connection.cursor()
cursor.execute("""                                              
CREATE TABLE IF NOT EXISTS users (                              
    id INTEGER PRIMARY KEY AUTOINCREMENT,                        
    name TEXT NOT NULL, 
    email TEXT,
    passwordhash TEXT NOT NULL,
    created_at TEXT,
    last_login TEXT,
    is_admin INTEGER
    )    
""")
connection.commit()
connection.close()
################################################################
def register_from_ui():
    connection = sq.connect("main.db")
    cursor = connection.cursor()
    name = entry_name.get()
    password_raw = entry_password.get()
    pw_bytes = password_raw.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    if not name or not password_raw:
        print("Bitte Name und Password angeben")
    else:
        cursor.execute("INSERT INTO users (name, passwordhash, created_at) VALUES (?, ?, datetime('now'))", (name, hashed))
        connection.commit()
        connection.close()



def sign_in():
    name = entry_name.get()
    password = entry_password.get()
    fav_color = entry_color.get()
    if name == "" or password == "":
        debug_label.config(text=f"bitte fülle Name und Password aus", fg="red")
    elif not fav_color:
        debug_label.config(text=f"Willkommen {name} !")
    else:
        try:
            debug_label.config(text=f"Willkommen {name} deine Lieblingsfarbe ist {fav_color}!", fg=fav_color)
        except tk.TclError:
            debug_label.config(text=f"Willkommen {name} deine Lieblingsfarbe ist {fav_color}? Aber die gibt es garnicht :(", fg="Black")
    register_from_ui()
#initialisierung des Fensters mit fester Größe (500px x 500px)
root = tk.Tk()
root.title("Anmeldung")
root.geometry("500x500")

tk.Label(root, text="Willkommen bei der Anmeldung").grid(row=0, columnspan=2, pady=10)
tk.Label(root, text="Name(Pflichtfeld):").grid(row=1, column=0, padx=5, pady=5)
tk.Label(root, text="Passwort(Pflichtfeld):").grid(row=2, column=0, padx=5, pady=5)
tk.Label(root, text="Lieblingsfarbe:").grid(row=3, column=0, padx=5, pady=5)

entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1, padx=5, pady=5)

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=2, column=1, padx=5, pady=5)

entry_color = tk.Entry(root)
entry_color.grid(row=3, column=1, padx=5, pady=5)

tk.Button(root, text="Abschicken", command=sign_in).grid(row=4, columnspan=2, pady=5)

debug_label = tk.Label(root, text="debug")
debug_label.grid(row=5, columnspan=2, pady=5)

entry_name.bind("<FocusIn>", lambda e: debug_label.config(text="Gib einen Namen ein(Pflichtfeld)", fg="grey"))
entry_password.bind("<FocusIn>", lambda e: debug_label.config(text="Gib ein Passwort ein (Pflichtfeld)", fg="grey"))
entry_color.bind("<FocusIn>", lambda e: debug_label.config(text="Gib deine Lieblingsfarbe ein", fg="grey"))

root.bind("<Return>", lambda event: sign_in())
#immer der Mainloop als dauerschleife um das Fenster offenzuhalten
root.mainloop()
