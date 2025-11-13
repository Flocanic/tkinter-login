import tkinter as tk


def sign_in():
    name = entry_name.get()
    password = entry_password.get()
    fav_color = entry_color.get()
    if name == "" or password == "" or fav_color == "":
        debug_label.config(text=f"bitte fülle alles aus", fg="red")
    else:
        debug_label.config(text=f"Willkommen {name} deine Lieblingsfarbe ist {fav_color}!", fg=fav_color)
#initialisierung des Fensters mit fester Größe (500px x 500px)
root = tk.Tk()
root.title("Anmeldung")
root.geometry("500x500")

tk.Label(root, text="Willkommen bei der Anmeldung").grid(row=0, columnspan=2, pady=10)
tk.Label(root, text="Name:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(root, text="Passwort:").grid(row=2, column=0, padx=5, pady=5)
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

entry_name.bind("<FocusIn>", lambda e: debug_label.config(text="Gib einen Namen ein", fg="grey"))
entry_password.bind("<FocusIn>", lambda e: debug_label.config(text="Gib ein Passwort ein", fg="grey"))
entry_color.bind("<FocusIn>", lambda e: debug_label.config(text="Gib deine Lieblingsfarbe ein", fg="grey"))

root.bind("<Return>", sign_in())
#immer der Mainloop als dauerschleife um das Fenster offenzuhalten
root.mainloop()
