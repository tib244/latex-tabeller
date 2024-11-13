import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import os
import webbrowser

class LatexTabellerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX Tabeller")
        self.root.geometry("1000x700")
        self.style = ttk.Style()
        self.apply_styles()

        self.file_name = None
        self.df = None
        self.latex_code = ""
        self.header_labels = []  # Labels to display header names
        self.additional_entries = []  # List to store additional Entry widgets for each header
        self.header_descriptions = []  # Store descriptions for each header
        self.general_description_entry = None  # Entry for general table description
        self.latex_window = None

        # UI Elemente
        self.create_widgets()

    def apply_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Helvetica", 12), padding=6, relief="flat", foreground="#ffffff", background="#3498db")
        self.style.map("TButton", background=[("active", "#2980b9")])
        self.style.configure("TLabel", font=("Helvetica", 11), foreground="#2c3e50")
        self.style.configure("TEntry", padding=5)
        self.root.configure(bg="#ecf0f1")

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20)

        # Datei öffnen Button
        self.open_file_button = ttk.Button(main_frame, text="Datei auswählen", command=self.open_file)
        self.open_file_button.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        # Label zur Anzeige des Dateinamens
        self.file_label = ttk.Label(main_frame, text="Keine Datei ausgewählt")
        self.file_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        # Allgemeine Beschreibung Eingabefeld
        ttk.Label(main_frame, text="Allgemeine Beschreibung:").grid(row=2, column=0, sticky="w")
        self.general_description_entry = tk.Entry(main_frame, font=("Helvetica", 10), width=80)
        self.general_description_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        # Button zur Öffnung der HTML-Dateien für Formelzeichen und Einheiten
        self.formula_button = ttk.Button(main_frame, text="Formelzeichen einfügen", command=self.open_formula_html)
        self.formula_button.grid(row=3, column=0, pady=10, padx=10, sticky="w")

        self.unit_button = ttk.Button(main_frame, text="Einheit einfügen", command=self.open_unit_html)
        self.unit_button.grid(row=3, column=1, pady=10, padx=10, sticky="w")

        # Tabelle (Treeview Widget) zur Anzeige der Excel-Daten
        self.tree = ttk.Treeview(main_frame, columns=(), show="headings", style="mystyle.Treeview")
        self.tree.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        # Scrollbar für die Tabelle
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=4, column=3, sticky="ns")

        # Frame für zusätzliche Eingabefelder unterhalb der Tabelle und oberhalb der Beschreibungstitel
        self.additional_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.additional_frame.pack(fill=tk.X, padx=20, pady=(20, 5))  # Extra Padding zum Verschieben

        # Titel für die Eingabefelder unterhalb der Tabelle
        title_label_formula = tk.Label(self.additional_frame, text="Formelzeichen", font=("Helvetica", 10, "bold"), bg="#ecf0f1")
        title_label_formula.grid(row=0, column=1, sticky="w", padx=5, pady=(10, 5))

        title_label_unit = tk.Label(self.additional_frame, text="Einheit", font=("Helvetica", 10, "bold"), bg="#ecf0f1")
        title_label_unit.grid(row=0, column=2, sticky="w", padx=5, pady=(10, 5))

        title_label_description = tk.Label(self.additional_frame, text="Beschreibung", font=("Helvetica", 10, "bold"), bg="#ecf0f1")
        title_label_description.grid(row=0, column=3, sticky="w", padx=5, pady=(10, 5))

        # Buttons unterhalb der Eingabefelder
        self.show_latex_button = ttk.Button(main_frame, text="LaTeX Code anzeigen", command=self.show_latex_code)
        self.show_latex_button.grid(row=6, column=0, pady=10, padx=10, sticky="w")

        self.copy_button = ttk.Button(main_frame, text="LaTeX Code kopieren", command=self.copy_to_clipboard)
        self.copy_button.grid(row=6, column=1, pady=10, padx=10, sticky="e")

        self.save_button = ttk.Button(main_frame, text=".tex Datei speichern", command=self.save_as_tex)
        self.save_button.grid(row=7, column=0, pady=10, padx=10, sticky="w")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.file_name = os.path.basename(file_path)
            self.file_label.config(text=self.file_name)
            self.load_excel_data(file_path)

    def load_excel_data(self, file_path):
        try:
            # Lade die Excel-Datei
            self.df = pd.read_excel(file_path, header=0)
            # Wähle nur die Spalten aus, die ab der 2. Zeile Werte enthalten
            valid_columns = [col for col in self.df.columns if self.df[col].iloc[1:].notna().any()]
            self.df = self.df[valid_columns]

            headers = self.df.columns
            data = self.df

            self.update_table(headers, data)

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Excel-Datei: {str(e)}")

    def update_table(self, headers, data):
        # Leere die vorherigen Header-Labels und Eingabefelder
        for widget in self.additional_frame.winfo_children():
            widget.destroy()
        self.header_labels.clear()
        self.additional_entries.clear()
        self.header_descriptions.clear()

        # Aktualisiere Treeview mit den validen Spalten
        self.tree["columns"] = list(headers)

        # Header-Labels und Eingabefelder in zusätzlichem Frame hinzufügen
        for i, header in enumerate(headers):
            header_label = tk.Label(self.additional_frame, text=f"{header}:", font=("Helvetica", 10), bg="#ecf0f1")
            header_label.grid(row=i, column=0, sticky="w", padx=5)

            # Zwei Eingabefelder für jeden Header mit Platzhaltertext
            entry_1 = tk.Entry(self.additional_frame, font=("Helvetica", 10), width=20, fg="grey")
            entry_1.insert(0, "Formelzeichen")
            entry_1.bind("<FocusIn>", lambda e, entry=entry_1, placeholder="Formelzeichen": self.on_focus_in(entry, placeholder))
            entry_1.bind("<FocusOut>", lambda e, entry=entry_1, placeholder="Formelzeichen": self.on_focus_out(entry, placeholder))
            entry_1.grid(row=i, column=1, padx=5, pady=5)

            entry_2 = tk.Entry(self.additional_frame, font=("Helvetica", 10), width=20, fg="grey")
            entry_2.insert(0, "Einheit")
            entry_2.bind("<FocusIn>", lambda e, entry=entry_2, placeholder="Einheit": self.on_focus_in(entry, placeholder))
            entry_2.bind("<FocusOut>", lambda e, entry=entry_2, placeholder="Einheit": self.on_focus_out(entry, placeholder))
            entry_2.grid(row=i, column=2, padx=5, pady=5)

            # Eingabefeld für die Beschreibung jedes Formelzeichens mit Platzhaltertext
            desc_entry = tk.Entry(self.additional_frame, font=("Helvetica", 10), width=40, fg="grey")
            desc_entry.insert(0, "Beschreibung")
            desc_entry.bind("<FocusIn>", lambda e, entry=desc_entry, placeholder="Beschreibung": self.on_focus_in(entry, placeholder))
            desc_entry.bind("<FocusOut>", lambda e, entry=desc_entry, placeholder="Beschreibung": self.on_focus_out(entry, placeholder))
            desc_entry.grid(row=i, column=3, padx=5, pady=5)

            self.header_labels.append(header_label)
            self.additional_entries.append((entry_1, entry_2))
            self.header_descriptions.append(desc_entry)

        # Zeige die Daten in der Tabelle an
        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def on_focus_in(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def open_formula_html(self):
        formula_file_path = os.path.join(os.path.dirname(__file__), "latex-formelzeichen-creator.html")
        webbrowser.open(formula_file_path)

    def open_unit_html(self):
        unit_file_path = os.path.join(os.path.dirname(__file__), "latex-einheiten-creator.html")
        webbrowser.open(unit_file_path)

    def show_latex_code(self):
        self.generate_latex_code()
        if self.latex_code:
            if self.latex_window is None or not self.latex_window.winfo_exists():
                self.latex_window = tk.Toplevel(self.root)
                self.latex_window.title("LaTeX Code")
                self.latex_window.geometry("600x400")
                self.latex_window.configure(bg="#ecf0f1")

                latex_textbox = tk.Text(self.latex_window, wrap=tk.WORD, font=("Helvetica", 12), bg="#ffffff", fg="#2c3e50")
                latex_textbox.insert(tk.END, self.latex_code)
                latex_textbox.pack(expand=True, fill=tk.BOTH)

                close_button = ttk.Button(self.latex_window, text="Schließen", command=self.latex_window.destroy)
                close_button.pack(pady=10)
            else:
                self.latex_window.deiconify()
        else:
            messagebox.showinfo("Info", "Es wurde noch kein LaTeX-Code generiert.")

    def copy_to_clipboard(self):
        self.generate_latex_code()
        if self.latex_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.latex_code)
            messagebox.showinfo("Info", "LaTeX Code wurde kopiert!")
        else:
            messagebox.showinfo("Info", "Es wurde noch kein LaTeX-Code generiert.")

    def save_as_tex(self):
        self.generate_latex_code()
        if self.latex_code:
            save_path = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=[("TeX files", "*.tex")])
            if save_path:
                with open(save_path, "w") as file:
                    file.write(self.latex_code)
                messagebox.showinfo("Info", ".tex Datei wurde gespeichert!")
        else:
            messagebox.showinfo("Info", "Es wurde noch kein LaTeX-Code generiert.")

    def generate_latex_code(self):
        headers = [
            f"{formula_entry.get() if formula_entry.get() != 'Formelzeichen' else ''} / {unit_entry.get() if unit_entry.get() != 'Einheit' else ''}".strip(" /")
            for formula_entry, unit_entry in self.additional_entries
        ]
        
        general_description = self.general_description_entry.get()
        
        # Beschreibungen erstellen im Format "Formelzeichen: Beschreibung" nur wenn Beschreibung vorhanden ist
        header_descriptions = [
            f"{formula_entry.get()}: {desc_entry.get()}"
            for (formula_entry, unit_entry), desc_entry in zip(self.additional_entries, self.header_descriptions)
            if formula_entry.get() != "Formelzeichen" and desc_entry.get() != "Beschreibung" and desc_entry.get()
        ]

        # LaTeX-Struktur
        self.latex_code = "\\begin{table}[H]\n\\centering\n"
        
        # Einfache caption mit allgemeiner Beschreibung und detaillierter Beschreibung kombiniert
        if general_description or header_descriptions:
            caption_text = general_description
            if header_descriptions:
                caption_text += " \\\\ " + ", ".join(header_descriptions)
            self.latex_code += f"\\caption{{{caption_text}}}\n"
        else:
            self.latex_code += "\\caption{}\n"

        self.latex_code += "\\begin{tabular}{" + "c" * len(headers) + "}\\n\\toprule\n"
        
        # Header-Zeile in den LaTeX-Code einfügen
        header_row = " & ".join(header if header else "" for header in headers) + " \\\\ \n\\midrule\n"
        self.latex_code += header_row

        # Datenzeilen aus der Tabelle hinzufügen
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            row_data = " & ".join(str(value) for value in values) + " \\\\ \n"
            self.latex_code += row_data

        # Tabelle abschließen
        self.latex_code += "\\bottomrule\n\\end{tabular}\n\\end{table}"

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexTabellerApp(root)
    root.mainloop()
