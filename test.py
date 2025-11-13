import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Hier steht der Titel")
    root.geometry("400x400")

    text_var = tk.StringVar(value="Hallo")

    def verändere():
        text_var.set("verändert")

    label1 = ttk.Label(root, textvariable=text_var)
    label1.pack(pady=5)

    button1 = ttk.Button(root, text="Klick mich", command=verändere)
    button1.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
