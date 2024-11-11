import tkinter as tk
from tkinter import ttk, messagebox

class LatexUnitCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX Einheiten-Creator")
        self.root.geometry("600x600")
        self.root.configure(bg="#333")

        # Haupttitel
        title = tk.Label(root, text="LaTeX Einheiten-Creator", font=("Arial", 16), fg="#ffffff", bg="#333")
        title.pack(pady=10)

        # Container für die Einheitenzeilen
        self.unit_rows = []
        self.unit_frame = tk.Frame(root, bg="#333")
        self.unit_frame.pack(pady=10, fill="x")

        # Erste Zeile hinzufügen
        self.add_row()

        # Button zum Hinzufügen weiterer Zeilen
        add_row_button = tk.Button(root, text="Zeile hinzufügen", command=self.add_row, bg="#5a8ff0", fg="#fff", font=("Arial", 12), padx=10, pady=5)
        add_row_button.pack(pady=10)

        # Button zum Generieren des LaTeX-Codes
        generate_button = tk.Button(root, text="Generate LaTeX Code", command=self.generate_latex_code, bg="#5a8ff0", fg="#fff", font=("Arial", 12), padx=10, pady=5)
        generate_button.pack(pady=20)

        # Ausgabe des generierten LaTeX-Codes
        self.output = tk.Text(root, height=3, font=("Arial", 12), bg="#444", fg="#f0f0f0", wrap="word")
        self.output.pack(pady=10, padx=20, fill="x")

    def add_row(self):
        """Fügt eine neue Zeile für Präfix, Einheit und Exponent hinzu."""
        row_frame = tk.Frame(self.unit_frame, bg="#333")
        row_frame.pack(pady=5, padx=10, fill="x")

        # Präfixauswahl
        prefix_options = ["Kein Präfix", "\\nano", "\\micro", "\\milli", "\\centi", "\\deci", "\\deca", "\\hecto", "\\kilo", "\\mega",
                          "\\yocto", "\\zepto", "\\atto", "\\femto", "\\pico", "\\giga", "\\tera", "\\peta", "\\exa", "\\zetta", "\\yotta"]
        prefix_select = ttk.Combobox(row_frame, values=prefix_options, width=10)
        prefix_select.set("Kein Präfix")
        prefix_select.pack(side="left", padx=5)

        # Einheitsauswahl
        unit_options = ["\\meter", "\\gram", "\\liter", "\\second", "\\mole", "\\joule", "\\kelvin", "\\celsius", "\\pascal", "\\watt", 
                        "\\newton", "\\volt", "\\ampere", "\\ohm", "\\coulomb", "\\farad", "\\henry", "\\tesla", "\\becquerel", 
                        "\\gray", "\\sievert", "\\hertz", "\\lux", "\\lumen", "\\weber", "\\candela", "\\radian", "\\steradian", 
                        "\\minute", "\\hour", "\\day", "\\tonne"]
        unit_select = ttk.Combobox(row_frame, values=unit_options, width=10)
        unit_select.set("\\meter")
        unit_select.pack(side="left", padx=5)

        # Exponent-Eingabe
        exponent_entry = tk.Entry(row_frame, width=5, bg="#444", fg="#f0f0f0", font=("Arial", 12))
        exponent_entry.insert(0, "Potenz")
        exponent_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, exponent_entry, "Potenz"))
        exponent_entry.bind("<FocusOut>", lambda event: self.set_placeholder(event, exponent_entry, "Potenz"))
        exponent_entry.pack(side="left", padx=5)

        # Entfernen-Button für die Zeile
        remove_button = tk.Button(row_frame, text="Entfernen", command=lambda: self.remove_row(row_frame), bg="#555", fg="#fff")
        remove_button.pack(side="left", padx=5)

        # Speichere die Widgets in der Liste
        self.unit_rows.append((prefix_select, unit_select, exponent_entry))

    def remove_row(self, row_frame):
        """Entfernt eine Zeile."""
        row_frame.pack_forget()
        row_frame.destroy()
        # Entferne die Zeile aus der gespeicherten Liste
        self.unit_rows = [row for row in self.unit_rows if row[0].winfo_exists()]

    def clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#f0f0f0")

    def set_placeholder(self, event, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="#888888")

    def generate_latex_code(self):
        """Generiert den LaTeX-Code basierend auf den eingegebenen Präfixen, Einheiten und Exponenten."""
        units = ""

        for prefix_select, unit_select, exponent_entry in self.unit_rows:
            prefix = prefix_select.get() if prefix_select.get() != "Kein Präfix" else ""
            unit = unit_select.get()
            exponent = exponent_entry.get() if exponent_entry.get() != "Potenz" and exponent_entry.get() else ""

            # Füge Präfix und Einheit hinzu, wenn nicht leer
            if prefix or unit:
                units += f"{prefix}{unit}"
                if exponent and exponent != "1":
                    units += f"\\tothe{{{exponent}}} "
                else:
                    units += " "

        # Entferne doppelte Backslashes und generiere den finalen Code
        units = units.replace("\\\\", "\\").strip()
        latex_code = f"\\SI{{}}{{{units}}}"

        # Ausgabe und Kopieren in die Zwischenablage
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, latex_code)
        self.copy_to_clipboard(latex_code)

    def copy_to_clipboard(self, latex_code):
        self.root.clipboard_clear()
        self.root.clipboard_append(latex_code)
        messagebox.showinfo("LaTeX Code", "LaTeX-Code wurde kopiert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexUnitCreatorApp(root)
    root.mainloop()
