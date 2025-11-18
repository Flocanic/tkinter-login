#hier importiere ich nötige (oder auch nicht) Module /Bibliotheken
import tkinter as tk
import sqlite3 as sq
import datetime as dt
from tkinter import Toplevel
from tkinter.messagebox import showinfo
import bcrypt
import os
price_cent_per_minute = float(20)
price_cent_per_meter = float(0.2)

choose = False
pad = 10
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
    email_input = entry_email.get()
    password_raw = entry_password.get()
    pw_bytes = password_raw.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

    if not name or not password_raw:
        debug_label.config(text="Bitte Name und Passwort angeben", fg="red")
    else:
        try:
            global account_id, username, email, is_admin
            with sq.connect("main.db") as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, passwordhash, created_at, email) VALUES (?, ?, datetime('now'), ?)", (name, hashed, email_input))
                cursor.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
                user_data = cursor.fetchone()
                account_id.set(user_data[0])
                username.set(user_data[1])
                email.set(user_data[2])

                #Admin check
                if account_id.get() == 1:
                    cursor.execute("UPDATE users SET is_admin = 1 WHERE id = 1")
                    is_admin.set(True)
                else:
                    is_admin.set(False)

                show_frame(main_frame)
                account_menu.entryconfig(ACCOUNT_ID_INDEX, label=f"Account ID: {account_id.get()}")
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
        cursor.execute("SELECT id, name, email, passwordhash, is_admin FROM users WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result is None:
            debug_label.config(text="Benutzer nicht gefunden!", fg="red")
            return

        user_id, user_name_db, user_email_db, stored_hash, admin_flag = result

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        account_id.set(user_id)
        username.set(user_name_db)
        email.set(user_email_db)
        is_admin.set(bool(admin_flag))
        account_menu.entryconfig(ACCOUNT_ID_INDEX, label=f"Account ID: {user_id}")

        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user_id,))

        debug_label.config(text=f"Willkommen zurück, {name}!", fg="green")
        show_frame(main_frame)
    else:
        debug_label.config(text="Falsches Passwort!", fg="red")

#bis hier login-Funktion
##############################################################################################################################
def show_usage_stats():
    showinfo("Verbrauch", "Diese Funktion wird später noch entwickelt.")

def true_change():
    global choose
    choose = True

def false_change():
    global choose
    choose = False

def delete_current_user_q():
    warning_frame = tk.Toplevel()
    warning_frame.title("Warning")
    warning_label = tk.Label(warning_frame, text="Das löscht den aktuellen User, einverstanden?")
    warning_label.grid(row=0, column=1)
    yes_warning_button = tk.Button(
        warning_frame,
        text="JA",
        bg="red",
        command=lambda: (true_change(), delete_final(), warning_frame.destroy())
    )
    yes_warning_button.grid(row=1, column=1)
    no_warning_button = tk.Button(warning_frame, text="NO", command=false_change, bg="green")
    no_warning_button.grid(row=1, column=0)

def delete_final():
    global choose
    if choose:
        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (account_id.get(),))
        account_id.set(-1)
        account_menu.entryconfig(ACCOUNT_ID_INDEX, label="Account ID: -")
        show_frame(register_frame)
    else:
        exit()

def _exit():
    root.destroy()

def show_frame(frame):
    frame.lift()

def calc():
    u = float(entry_u.get())
    a = float(entry_a.get())
    tm = float(entry_tm.get())
    p = float(entry_preis_cent.get())
    result = u*a*tm/60*365*p/1000/100
    label_kwhy.config(text=f"Das Laden deines Geräts kosten im Jahr {result:.2f} €")

def calc2():
    mi = float(entry_mi.get())
    me = float(entry_me.get())

    global price_cent_per_minute
    global price_cent_per_meter

    if entry_preis_minute_cent.get():
        price_cent_per_minute = float(entry_preis_minute_cent.get())
    else:
        price_cent_per_minute = 20

    if entry_preis_meter_cent.get():
        price_cent_per_meter = float(entry_preis_meter_cent.get())
    else:
        price_cent_per_meter = 0.2

    result = mi * price_cent_per_minute + me * price_cent_per_meter
    tk.Label(calc_price_frame, text=f"Der zu zahlende Betrag wäre: {result:.2f} €").grid(row=5, column=0, padx=pad, pady=pad)

def save_price():
    global price_cent_per_minute, price_cent_per_meter

    try:
        if entry_preis_minute_cent.get():
            price_cent_per_minute = float(entry_preis_minute_cent.get())
        if entry_preis_meter_cent.get():
            price_cent_per_meter = float(entry_preis_meter_cent.get())
    except ValueError:
        showinfo("Fehler", "Bitte gültige Zahlen eingeben!")
        return

    with sq.connect("main.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cent_per_minute REAL,
                cent_per_meter REAL,
                updated_at TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO prices (cent_per_minute, cent_per_meter, updated_at) VALUES (?, ?, datetime('now'))",
            (price_cent_per_minute, price_cent_per_meter)
        )

    showinfo("Erfolg", f"Preis gespeichert!\nMinute: {price_cent_per_minute} Cent\nMeter: {price_cent_per_meter} Cent")
    show_frame(calc_price_frame)

def toggle_darkmode():
    new_color = "#333333" if root["bg"] == "SystemButtonFace" else "SystemButtonFace"
    root.config(bg=new_color)
    for widget in root.winfo_children():
        try:
            widget.config(bg=new_color)
        except:
            pass

def change_name():
    def apply_name_change():
        new_name = entry_new_name.get().strip()
        if not new_name:
            showinfo("Fehler", "Name darf nicht leer sein!")
            return

        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, account_id.get()))
                connection.commit()
                showinfo("Erfolg", f"Name erfolgreich geändert zu: {new_name}")
                account_menu.entryconfig(ACCOUNT_ID_INDEX, label=f"Account ID: {account_id.get()}")
            except sq.IntegrityError:
                showinfo("Fehler", "Name existiert bereits!")
        window.destroy()

    window = Toplevel(root)
    window.title("Namen ändern")
    tk.Label(window, text="Neuer Name:").pack(pady=5)
    entry_new_name = tk.Entry(window)
    entry_new_name.pack(pady=5)
    tk.Button(window, text="Speichern", command=apply_name_change).pack(pady=5)

def change_password():
    def apply_password_change():
        old_pw = entry_old_pw.get().strip()
        new_pw = entry_new_pw.get().strip()

        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT passwordhash FROM users WHERE id = ?", (account_id.get(),))
            result = cursor.fetchone()

        if not bcrypt.checkpw(old_pw.encode("utf-8"), result[0]):
            showinfo("Fehler", "Altes Passwort ist falsch!")
            return

        if not new_pw:
            showinfo("Fehler", "Neues Passwort darf nicht leer sein!")
            return

        hashed = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt())

        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET passwordhash = ? WHERE id = ?", (hashed, account_id.get()))
            connection.commit()

        showinfo("Erfolg", "Passwort erfolgreich geändert!")
        window.destroy()

    window = Toplevel(root)
    window.title("Passwort ändern")
    tk.Label(window, text="Altes Passwort:").pack(pady=5)
    entry_old_pw = tk.Entry(window, show="*")
    entry_old_pw.pack(pady=5)
    tk.Label(window, text="Neues Passwort:").pack(pady=5)
    entry_new_pw = tk.Entry(window, show="*")
    entry_new_pw.pack(pady=5)
    tk.Button(window, text="Speichern", command=apply_password_change).pack(pady=5)

def change_email():
    def apply_email_change():
        new_email = entry_new_email.get().strip()
        if not new_email:
            showinfo("Fehler", "E-Mail darf nicht leer sein!")
            return

        with sq.connect("main.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, account_id.get()))
            connection.commit()

        showinfo("Erfolg", "E-Mail erfolgreich geändert!")
        window.destroy()

    window = Toplevel(root)
    window.title("E-Mail ändern")
    tk.Label(window, text="Neue E-Mail:").pack(pady=5)
    entry_new_email = tk.Entry(window)
    entry_new_email.pack(pady=5)
    tk.Button(window, text="Speichern", command=apply_email_change).pack(pady=5)

# ==========================================================
# ===================== TKINTER SETUP =======================
# ==========================================================

root = tk.Tk()
# TODO: größe beschränken
root.title("Scooteq - Datox")
root.geometry("500x500")
logged_in = tk.BooleanVar(value=False)
account_id = tk.IntVar(value=-1)
account_id_var = tk.StringVar(value="Account ID: -")
username = tk.StringVar(value="")
email = tk.StringVar(value="")
is_admin = tk.BooleanVar(value=False)

# ==========================================================
# ==================== FRAME DEFINITIONS ===================
# ==========================================================

register_frame = tk.Frame()
main_frame = tk.Frame()
settings_frame = tk.Frame()
calc_price_frame = tk.Frame()
strom_frame = tk.Frame()
price_frame = tk.Frame()
profile_frame = tk.Frame()

# Alle Frames platzieren
for frame in (register_frame, main_frame, settings_frame, strom_frame, calc_price_frame, price_frame, profile_frame):
    frame.place(relwidth=1, relheight=1)

# Start bei Login
show_frame(register_frame)

# ==========================================================
# ==================== MENUBAR =============================
# ==========================================================
menu_bar = tk.Menu(root)
account_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Account", menu=account_menu)
ACCOUNT_ID_INDEX = 0
account_menu.add_command(label="Account ID: -")
menu_bar.add_command(label="Einstellung", command=lambda: show_frame(settings_frame))
menu_bar.add_command(label="Zeige Profilinformation", command=lambda: show_frame(profile_frame))
menu_bar.add_command(label="Zurück zur Anmeldung", command=lambda: show_frame(register_frame))
menu_bar.add_separator()
menu_bar.add_command(label="EXIT", command=lambda: root.destroy())
root.config(menu=menu_bar)

# ==========================================================
# ==================== LOGIN/REGISTER FRAME ================
# ==========================================================

tk.Label(register_frame, text="Willkommen bei der Anmeldung").grid(row=0, columnspan=2, pady=pad)
tk.Label(register_frame, text="Name(Pflichtfeld):").grid(row=1, column=0, padx=pad, pady=pad)
tk.Label(register_frame, text="Passwort(Pflichtfeld):").grid(row=2, column=0, padx=pad, pady=pad)
tk.Label(register_frame, text="Email (Freiwillige Angabe):").grid(row=3, column=0, padx=pad, pady=pad)
entry_name = tk.Entry(register_frame)
entry_name.grid(row=1, column=1, padx=pad, pady=pad)
entry_password = tk.Entry(register_frame, show="*")
entry_password.grid(row=2, column=1, padx=pad, pady=pad)
entry_email = tk.Entry(register_frame)
entry_email.grid(row=3, column=1, padx=pad, pady=pad)
tk.Button(register_frame, text="Login", command=sign_in).grid(row=4, column=0, pady=pad)
tk.Button(register_frame, text="Registrieren", command=register_from_ui).grid(row=4, column=1, pady=pad)
tk.Button(register_frame, text="Überspringen", command=lambda: show_frame(main_frame)).grid(row=4, column=2, pady=pad)
debug_label = tk.Label(register_frame, text="debug")
debug_label.grid(row=5, columnspan=2, pady=pad)
entry_name.bind("<FocusIn>", lambda e: debug_label.config(text="Gib einen Namen ein(Pflichtfeld)", fg="grey"))
entry_password.bind("<FocusIn>", lambda e: debug_label.config(text="Gib ein Passwort ein (Pflichtfeld)", fg="grey"))
entry_email.bind("<FocusIn>", lambda e: debug_label.config(text="Gib deine Email ein (Freiwillige Angabe)", fg="grey"))
register_frame.bind("<Return>", lambda event: sign_in())

# ==========================================================
# ======================== MAIN FRAME ======================
# ==========================================================

tk.Label(main_frame, text="Willkommen im Hauptmenü").grid(row=0, column=2, padx=pad, pady=pad)
tk.Label(main_frame, text="Wählen Sie eine Option aus").grid(row=1, column=2, padx=pad, pady=pad)
calc_price_button = tk.Button(main_frame, text="Nutzpreis Rechner", command=lambda: show_frame(calc_price_frame))
calc_price_button.grid(row=2, column=1, padx=pad, pady=pad)
strom_button = tk.Button(main_frame, text="stromrechner", command=lambda: show_frame(strom_frame))
strom_button.grid(row=2, column=2, padx=pad, pady=pad)
delete_user_button = tk.Button(main_frame, text="DELETE USER", command=delete_current_user_q, bg="red")
delete_user_button.grid(row=5, column=2, padx=pad, pady=pad)

# ==========================================================
# ====================== PROFILE FRAME =====================
# ==========================================================

profile_label = tk.Label(profile_frame, text="Profil Übersicht", font=("Arial", 14))
profile_label.grid(row=0, column=0, columnspan=2, pady=10)
tk.Label(profile_frame, textvariable=username, font=("Arial", 11), text=f"Benutzername: {username.get()}").grid(row=1, column=0, columnspan=2, pady=5)
tk.Label(profile_frame, textvariable=account_id, font=("Arial", 11), text=f"Account ID: {account_id.get()}").grid(row=2, column=0, columnspan=2, pady=5)
tk.Label(profile_frame, textvariable=email, font=("Arial", 11), text=f"E-Mail: {email.get()}").grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(profile_frame, text="Verbrauch anzeigen", command=show_usage_stats).grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(profile_frame, text="Einstellungen", command=lambda: show_frame(settings_frame)).grid(row=6, column=0, columnspan=2, pady=5)
tk.Button(profile_frame, text="Zurück", command=lambda: show_frame(main_frame)).grid(row=7, column=0, columnspan=2, pady=10)

# ==========================================================
# ====================== SETTINGS FRAME ====================
# ==========================================================

tk.Label(settings_frame, text="Einstellungen", font=("Arial", 14)).pack(pady=10)
tk.Button(settings_frame, text="Namen ändern", command=change_name).pack(pady=5)
tk.Button(settings_frame, text="Passwort ändern", command=change_password).pack(pady=5)
tk.Button(settings_frame, text="E-Mail ändern", command=change_email).pack(pady=5)
tk.Button(settings_frame, text="Dark Mode aktivieren", command=toggle_darkmode).pack(pady=5)
tk.Button(settings_frame, text="Zurück", command=lambda: show_frame(main_frame)).pack(pady=20)

# ==========================================================
# ====================== NUTZPREIS FRAME ===================
# ==========================================================

tk.Label(calc_price_frame, text="Nutzpreis berechnen").grid(row=0, column=1, pady=pad)
tk.Label(calc_price_frame, text="Wie viel wurden gefahren? (Meter)").grid(row=1, column=0, padx=pad, pady=pad)
entry_me = tk.Entry(calc_price_frame)
entry_me.grid(row=1, column=1, padx=pad, pady=pad)
tk.Label(calc_price_frame, text="Wie lange wurde der Scooter benutzt? (Minuten)").grid(row=2, column=0, padx=pad, pady=pad)
entry_mi = tk.Entry(calc_price_frame)
entry_mi.grid(row=2, column=1, padx=pad, pady=pad)
tk.Button(calc_price_frame, text="ausrechnen", command=calc2).grid(row=5, column=1, padx=pad, pady=pad)
tk.Button(calc_price_frame, text="Preis festlegen", command=lambda: show_frame(price_frame)).grid(row=6, column=1, padx=pad, pady=pad)
tk.Button(calc_price_frame, text="Zurück", command=lambda: show_frame(main_frame)).grid(row=7, column=1, padx=pad, pady=pad)

# ==========================================================
# ==================== PREISFESTLEGUNG FRAME ===============
# ==========================================================

tk.Label(price_frame, text="Hier kann ein Admin den Preis festlegen")
tk.Label(price_frame, text=f"Neuer Preis pro Minute in Cent (Default {price_cent_per_minute})").grid(row=1, column=1, padx=pad, pady=pad)
tk.Label(price_frame, text=f"Neuer Preis pro Meter in Cent (Default {price_cent_per_meter})").grid(row=2, column=1, padx=pad, pady=pad)
entry_preis_meter_cent = tk.Entry(price_frame)
entry_preis_meter_cent.grid(row=1, column=2, padx=pad, pady=pad)
entry_preis_minute_cent = tk.Entry(price_frame)
entry_preis_minute_cent.grid(row=2, column=2, padx=pad, pady=pad)
tk.Button(price_frame, text="Preis speichern", bg="lightgreen", command=save_price).grid(row=6, column=1, padx=pad, pady=pad)
tk.Button(price_frame, text="Zurück", command=lambda: show_frame(calc_price_frame)).grid(row=7, column=1, padx=pad, pady=pad)

# ==========================================================
# ==================== STROMRECHNER FRAME ==================
# ==========================================================

tk.Label(strom_frame, text="Wie viel Spannung (V) hat das Ladegerät?").grid(row=1, column=0, padx=pad, pady=pad)
entry_u = tk.Entry(strom_frame)
entry_u.grid(row=1, column=1, padx=pad, pady=pad)
tk.Label(strom_frame, text="Wie viel Strom (A) hat das Ladegerät?").grid(row=2, column=0, padx=pad, pady=pad)
entry_a = tk.Entry(strom_frame)
entry_a.grid(row=2, column=1, padx=pad, pady=pad)
tk.Label(strom_frame, text="Wie ist das Gerät täglich am Ladegerät? (in Minuten)").grid(row=3, column=0, padx=pad, pady=pad)
entry_tm = tk.Entry(strom_frame)
entry_tm.grid(row=3, column=1, padx=pad, pady=pad)
entry_preis_cent = tk.Entry(strom_frame)
entry_preis_cent.grid(row=4, column=1, padx=pad, pady=pad)
entry_preis_cent.insert(0, "40")
tk.Label(strom_frame, text="Wie teuer (Cent) ist dein Strom pro Kw/h? (Default 40)").grid(row=4, column=0, padx=pad, pady=pad)
button_calc = tk.Button(strom_frame, text="Ausrechnen", command=calc)
button_calc.grid(row=5, column=0, padx=pad, pady=pad)
label_kwhy = tk.Label(strom_frame, text="Bitte erst \"Ausrechnen\" klicken")
label_kwhy.grid(row=5, column=1, padx=pad, pady=pad)
tk.Button(strom_frame, text="Zurück", command=lambda: show_frame(main_frame)).grid(row=7, column=1, padx=pad, pady=pad)

root.mainloop()