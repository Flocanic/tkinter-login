#hier importiere ich nötige (oder auch nicht) Module
import tkinter as tk
import sqlite3 as sq
import datetime as dt
import bcrypt
import os

#SQLITE3--------------------------------------------------------
#hier erstelle ich eine Datenbank, falls sie nicht existiert
with sq.connect("main.db") as connection:
    cursor = connection.cursor()
    cursor.execute("""                                              
    CREATE TABLE IF NOT EXISTS users (                              
        id INTEGER PRIMARY KEY AUTOINCREMENT,                        
        name TEXT NOT NULL UNIQUE, 
        email TEXT,
        passwordhash BLOB NOT NULL,
        created_at TEXT,
        last_login TEXT,
        is_admin INTEGER
        )    
    """)
################################################################
#hier ist die Funktion zum Registrieren von Nutzern
def register_from_ui():
    name = entry_name.get()
    email = entry_email.get()
    password_raw = entry_password.get()
    pw_bytes = password_raw.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

    if not name or not password_raw:
        debug_label.config(text="Bitte Name und Passwort angeben", fg="red")
    else:
        try:
            global account_id
            with sq.connect("main.db") as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, passwordhash, created_at, email) VALUES (?, ?, datetime('now'), ?)", (name, hashed, email))
                cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
                account_id.set(cursor.fetchone()[0])
        except sq.IntegrityError:
            debug_label.config(text="Fehler bei Kontoanlegung (Name bereits vergeben)", fg="red")
    entry_name.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_email.delete(0, tk.END)
#############################################################################################################################
#hier ist die Funktion zum Einloggen von Nutzern
def sign_in():
    name = entry_name.get().strip()
    password = entry_password.get().strip()

    if not name or not password:
        debug_label.config(text="Bitte Name und Passwort ausfüllen", fg="red")
        return

    with sq.connect("main.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
            account_id.set(cursor.fetchone()[0])
        cursor.execute("SELECT id, passwordhash FROM users WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result is None:
            debug_label.config(text="Benutzer nicht gefunden!", fg="red")
            return

        account_id.set(result[0])
        stored_hash = result[1]

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users set last_login = datetime('now') where name = ?", (name,))
            global logged_in
            logged_in.set(True)
        if logged_in.get():
            debug_label.config(text=f"Willkommen zurück, {name}!", fg="green")
            print("Eingeloggt als ID:", account_id.get())

    else:
        debug_label.config(text="Falsches Passwort!", fg="red")
    entry_name.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_email.delete(0, tk.END)
#bis hier login-Funktion
##############################################################################################################################
#initialisierung des Fensters mit fester Größe (500px x 500px)
root = tk.Tk()
root.title("Anmeldung")
root.geometry("500x500")
##############################################################################################################################
#Globale Variablen
logged_in = tk.BooleanVar(value=False)
account_id = tk.IntVar(value=-1)
##############################################################################################################################
#Widgets anlegen, alles mögliche
tk.Label(root, text="Willkommen bei der Anmeldung").grid(row=0, columnspan=2, pady=10)
tk.Label(root, text="Name(Pflichtfeld):").grid(row=1, column=0, padx=5, pady=5)
tk.Label(root, text="Passwort(Pflichtfeld):").grid(row=2, column=0, padx=5, pady=5)
tk.Label(root, text="Email (Freiwillige Angabe):").grid(row=3, column=0, padx=5, pady=5)

entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1, padx=5, pady=5)

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=2, column=1, padx=5, pady=5)

entry_email = tk.Entry(root)
entry_email.grid(row=3, column=1, padx=5, pady=5)

tk.Button(root, text="Login", command=sign_in).grid(row=4, column=0, pady=5)
tk.Button(root, text="Registrieren", command=register_from_ui).grid(row=4, column=1, pady=5)

debug_label = tk.Label(root, text="debug")
debug_label.grid(row=5, columnspan=2, pady=5)

entry_name.bind("<FocusIn>", lambda e: debug_label.config(text="Gib einen Namen ein(Pflichtfeld)", fg="grey"))
entry_password.bind("<FocusIn>", lambda e: debug_label.config(text="Gib ein Passwort ein (Pflichtfeld)", fg="grey"))
entry_email.bind("<FocusIn>", lambda e: debug_label.config(text="Gib deine Email ein (Freiwillige Angabe)", fg="grey"))

root.bind("<Return>", lambda event: sign_in())

#immer der Mainloop als dauerschleife um das Fenster offenzuhalten
root.mainloop()
