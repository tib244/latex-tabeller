import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import requests
import os
import sys
import subprocess
import webbrowser

class LatexTabellerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX Tabeller")
        self.root.geometry("900x700")
        self.style = ttk.Style()
        self.apply_styles()

        self.file_name = None
        self.df = None
        self.latex_code = ""
        self.formelzeichen = []
        self.formel_input_fields = []
        self.latex_template = ""
        self.latex_window = None

        # UI Elemente
        self.create_widgets()

        # Check for updates
        self.check_for_updates()

    def apply_styles(self):
        # Setze den Stil für eine modernere Oberfläche
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

        # Button zum Abspielen des Erklärungsvideos
        self.video_button = ttk.Button(main_frame, text="Erklärungsvideo", command=self.open_video)
        self.video_button.grid(row=0, column=1, pady=10, padx=10, sticky="w")

        # Label zur Anzeige des Dateinamens
        self.file_label = ttk.Label(main_frame, text="Keine Datei ausgewählt")
        self.file_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        # Tabelle (Treeview Widget) zur Anzeige der Excel-Daten
        self.tree = ttk.Treeview(main_frame, columns=(), show="headings", style="mystyle.Treeview")
        self.tree.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        # Scrollbar für die Tabelle
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=2, sticky="ns")

        # Vorlage-Download-Button
        self.download_template_button = ttk.Button(main_frame, text="Vorlage herunterladen", command=self.download_template)
        self.download_template_button.grid(row=3, column=0, pady=10, padx=10, sticky="w")

        # Eingabefeld für allgemeine Beschreibung
        self.general_desc_label = ttk.Label(main_frame, text="Allgemeine Beschreibung:")
        self.general_desc_label.grid(row=4, column=0, pady=10, padx=10, sticky="w")
        self.general_desc_input = ttk.Entry(main_frame, width=80)
        self.general_desc_input.grid(row=4, column=1, pady=10, padx=10, sticky="w")

        # Eingabefeld für Label der Tabelle
        self.label_desc_label = ttk.Label(main_frame, text="Tabelle Label:")
        self.label_desc_label.grid(row=5, column=0, pady=10, padx=10, sticky="w")
        self.label_desc_input = ttk.Entry(main_frame, width=80)
        self.label_desc_input.grid(row=5, column=1, pady=10, padx=10, sticky="w")

        # Dynamischer Frame für die Formelzeichen-Eingabefelder
        self.formel_input_frame = tk.Frame(main_frame, bg="#ecf0f1")
        self.formel_input_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="w")

        # Latex-Code in separatem Fenster öffnen Button
        self.show_latex_button = ttk.Button(main_frame, text="LaTeX Code anzeigen", command=self.show_latex_code)
        self.show_latex_button.grid(row=7, column=0, pady=10, padx=10, sticky="w")

        # Latex-Code kopieren Button
        self.copy_button = ttk.Button(main_frame, text="LaTeX Code kopieren", command=self.copy_to_clipboard)
        self.copy_button.grid(row=7, column=1, pady=10, padx=10, sticky="e")

        # Latex-Code speichern Button
        self.save_button = ttk.Button(main_frame, text=".tex Datei speichern", command=self.save_as_tex)
        self.save_button.grid(row=8, column=0, pady=10, padx=10, sticky="w")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.file_name = os.path.basename(file_path)
            self.file_label.config(text=self.file_name)
            self.load_excel_data(file_path)

    def open_video(self):
        video_url = "https://www.dropbox.com/scl/fi/67ze05xhrsegkxg5sm1p1/Erklaerung_Tabeller.mp4?rlkey=r1aqyj8hh8stz52agz92tpx3h&st=h8zpitx9&dl=0"
        webbrowser.open(video_url)

    def load_excel_data(self, file_path):
        try:
            # Lese die Datei ein und setze die erste Zeile als Header
            self.df = pd.read_excel(file_path, header=0)
        
            # Wähle alle Spalten für die Tabelle
            headers = self.df.columns
            data = self.df

            # Aktualisiere die Anzeige in der GUI und erstelle den LaTeX-Code
            self.update_table(headers, data)
            self.extract_formula_from_headers(headers)
            self.generate_latex_code(headers, data)

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Excel-Datei: {str(e)}")


    def update_table(self, headers, data):
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")

        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(headers)
        for header in headers:
            self.tree.heading(header, text=header)

        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def extract_formula_from_headers(self, headers):
        self.formelzeichen = []
        self.formel_input_fields = []

        # Vorherige Eingabefelder entfernen
        for widget in self.formel_input_frame.winfo_children():
            widget.destroy()

        for header in headers[1:]:
            header = str(header)
            if "\\" in header:
                # Alles bis zur schließenden geschweiften Klammer übernehmen und ein abschließendes $ hinzufügen
                header_part = header.split("}")[0] + "}"
                header_with_backslash = f"{header_part}$"
                self.formelzeichen.append(header_with_backslash)
            else:
                # Falls kein \ vorhanden ist, wird der Header normal formatiert und ein $ am Ende hinzugefügt
                header_clean = header + "$"
                self.formelzeichen.append(header_clean.strip())

        # Dynamisch Eingabefelder für Formelzeichen erstellen
        for i, formel in enumerate(self.formelzeichen):
            label = ttk.Label(self.formel_input_frame, text=formel)
            label.grid(row=i, column=0, pady=5, padx=10, sticky="w")
            entry = ttk.Entry(self.formel_input_frame, width=50)
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="w")
            self.formel_input_fields.append(entry)




    def update_caption(self):
        general_description = self.general_desc_input.get()
        table_label = self.label_desc_input.get()

        updated_caption_parts = []
        for i, entry in enumerate(self.formel_input_fields):
            additional_text = entry.get()
            formula_sign = self.formelzeichen[i]
            updated_caption_parts.append(f"{formula_sign}: {additional_text}")

        updated_caption = general_description + " \\\\\n" + ", ".join(updated_caption_parts)

        self.latex_code = self.latex_template.replace("CAPTION_PLACEHOLDER", updated_caption).replace("LABEL_PLACEHOLDER", table_label)

    def generate_latex_code(self, headers, data):
        table_caption = "CAPTION_PLACEHOLDER"
        table_label = "LABEL_PLACEHOLDER"

        # Beginne mit der LaTeX-Tabellenstruktur
        self.latex_template = "\\begin{table}[H]\n\\caption{" + table_caption + "}\n\\label{" + table_label + "}\n\\centering\n\\begin{tabular}{" + "c" * len(headers) + "}\n\\toprule\n"

        # Kopfzeile: Erster Header fett mit \textbf, mathematische Symbole (Formelzeichen) mit \boldmath
        header_row = []
        for col_index, header in enumerate(headers):
            if col_index == 0:  # Erste Spalte immer fett mit \textbf
                header_row.append(f"\\textbf{{{header}}}")
            elif "\\" in str(header):  # Wenn das Header-Feld ein Formelzeichen enthält (z.B. enthält "\")
                header_row.append(f"\\boldmath{{{header}}}")
            else:  # Normale Header
                header_row.append(f"{header}")

        # Füge die Kopfzeile zur LaTeX-Tabelle hinzu
        self.latex_template += " & ".join(header_row) + " \\\\ \n\\midrule\n"

        # Füge die Datenzeilen hinzu (erste Spalte immer fett, restliche Zellen wie zuvor)
        for row_index, row in data.iterrows():
            row_data = []
            for col_index, value in enumerate(row):
                if col_index == 0:  # Erste Spalte immer fett
                    row_data.append(f"\\textbf{{{value}}}")
                else:
                    row_data.append(str(value))
            data_row = " & ".join(row_data) + " \\\\ \n"
            self.latex_template += data_row

        # Schließe die LaTeX-Tabelle
        self.latex_template += "\\bottomrule\n\\end{tabular}\n\\end{table}"

        # LaTeX-Code aktualisieren
        self.latex_code = self.latex_template

    def show_latex_code(self):
        self.update_caption()

        if self.latex_window is None or not self.latex_window.winfo_exists():
            self.latex_window = tk.Toplevel(self.root)
            self.latex_window.title("LaTeX Code")
            self.latex_window.geometry("600x400")
            self.latex_window.configure(bg="#ecf0f1")

            latex_textbox = tk.Text(self.latex_window, wrap=tk.WORD, font=("Helvetica", 12), bg="#ffffff", fg="#2c3e50")
            latex_textbox.insert(tk.END, self.latex_code)
            latex_textbox.pack(expand=True, fill=tk.BOTH)

            latex_textbox.config(state=tk.NORMAL)

            close_button = ttk.Button(self.latex_window, text="Schließen", command=self.latex_window.destroy)
            close_button.pack(pady=10)
        else:
            self.latex_window.deiconify()

    def copy_to_clipboard(self):
        self.update_caption()
        self.root.clipboard_clear()
        self.root.clipboard_append(self.latex_code)
        messagebox.showinfo("Info", "LaTeX Code wurde kopiert!")

    def save_as_tex(self):
        if self.latex_code:
            self.update_caption()
            save_path = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=[("TeX files", "*.tex")])
            if save_path:
                with open(save_path, "w") as file:
                    file.write(self.latex_code)
                messagebox.showinfo("Info", ".tex Datei wurde gespeichert!")

    def download_template(self):
        url = "https://www.dropbox.com/scl/fi/dw5ai6r87v28egjuokiqy/Tabeller_Vorlage_v3.xlsx?rlkey=lynoynuy759a8zz0lrr0m6rb6&st=mt0bgmzd&dl=1"

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            try:
                response = requests.get(url)
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                messagebox.showinfo("Erfolg", "Vorlage erfolgreich heruntergeladen!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Herunterladen der Vorlage: {str(e)}")

    def check_for_updates(self):
        version_url = "https://www.dropbox.com/scl/fi/64o2ji88ugdz892w5adx3/version.txt?rlkey=z5izibbqzz6rlpw6xofsmi654&st=tq1m73zo&dl=1"
        exe_url = "https://www.dropbox.com/scl/fi/2h3r0s5na4r3x0ez6yx6m/tabeller_1_0_1.exe?rlkey=lau0vubntjm4i7u3xzpp2j8wi&st=23agbbud&dl=1"

        current_version = "1.0.8"

        try:
            response = requests.get(version_url)
            lines = response.text.strip().splitlines()
            latest_version = lines[0].strip()
            improvements = "\n".join(lines[1:])

            if latest_version != current_version:
                update_message = f"Version {latest_version} ist verfügbar mit folgenden Verbesserungen:\n{improvements}\n\nMöchtest du das Update herunterladen?"
                if messagebox.askyesno("Update verfügbar", update_message):
                    self.download_update(exe_url, latest_version)
            else:
                messagebox.showinfo("Info", "Du hast bereits die neueste Version.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Überprüfen auf Updates: {str(e)}")

    def download_update(self, url, version):
        try:
            # Legt den temporären Pfad und den endgültigen Zielnamen mit Versionsnummer fest
            temp_path = os.path.join(os.getcwd(), "tabeller_update.exe")
            destination_path = os.path.join(os.getcwd(), f"tabeller_{version}.exe")

            # Update-Datei herunterladen
            response = requests.get(url, stream=True)
            with open(temp_path, 'wb') as exe_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        exe_file.write(chunk)

            # Datei umbenennen, um die Versionsnummer einzuschließen
            os.rename(temp_path, destination_path)

            # Nachricht an den Benutzer
            messagebox.showinfo("Update", f"Das Update wurde erfolgreich als {destination_path} heruntergeladen. Bitte starten Sie das Programm manuell neu, um die neue Version zu verwenden.")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Herunterladen des Updates: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexTabellerApp(root)
    root.mainloop()