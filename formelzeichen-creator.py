import tkinter as tk
from tkinter import ttk, messagebox

class LatexFormulaCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX Formelzeichen-Creator")
        self.root.geometry("500x600")
        self.root.configure(bg="#333")

        # Haupttitel
        title = tk.Label(root, text="LaTeX Formelgenerator", font=("Arial", 16), fg="#ffffff", bg="#333")
        title.pack(pady=10)

        # Eingabefelder für Formelaufbau
        symbol_frame = tk.Frame(root, bg="#333")
        symbol_frame.pack(pady=10)

        # Sup- und Subskriptfelder
        self.sup_before = self.create_entry(symbol_frame, "Hochgestellt Links", 0, 0)
        self.sub_before = self.create_entry(symbol_frame, "Tiefgestellt Links", 1, 0)
        self.main_symbol = self.create_entry(symbol_frame, "Symbol", 0, 1, width=20)
        self.sup_after = self.create_entry(symbol_frame, "Hochgestellt Rechts", 0, 2)
        self.sub_after = self.create_entry(symbol_frame, "Tiefgestellt Rechts", 1, 2)

        # Auswahl für Sonderzeichen
        symbol_options = ["Kein Symbol", "\\tilde (~)", "\\bar (¯)", "\\dot (•)", "\\hat (^)", "\\vec (→)", 
                          "\\ddot (¨)", "\\breve (˘)", "\\check (ˇ)", "\\acute (´)", "\\grave (`)", "\\mathring (°)", 
                          "\\overline (¯)", "\\underline (_)"]
        tk.Label(root, text="Sonderzeichen:", bg="#333", fg="#f0f0f0").pack(pady=5)
        self.symbol_select = ttk.Combobox(root, values=symbol_options, width=30)
        self.symbol_select.set("Kein Symbol")
        self.symbol_select.pack(pady=5)

        # Griechische Buchstaben-Tastatur
        self.greek_keyboard(root)

        # Button zum Generieren des LaTeX-Codes
        generate_button = tk.Button(root, text="Generate LaTeX Code", command=self.generate_latex_code, 
                                    bg="#5a8ff0", fg="#fff", font=("Arial", 12), padx=10, pady=5)
        generate_button.pack(pady=20)

        # Felder für die Ausgabe
        self.output = tk.Text(root, height=3, font=("Arial", 12), bg="#444", fg="#f0f0f0", wrap="word")
        self.output.pack(pady=10, padx=20, fill="x")

    def create_entry(self, parent, placeholder, row, col, width=10):
        entry = tk.Entry(parent, font=("Arial", 12), width=width, bg="#444", fg="#888888", justify="center")
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self.on_focus_in(event, e, p))
        entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self.on_focus_out(event, e, p))
        entry.grid(row=row, column=col, padx=5, pady=5)
        return entry

    def on_focus_in(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#f0f0f0")

    def on_focus_out(self, event, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="#888888")

    def greek_keyboard(self, parent):
        greek_symbols = [
            "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ", 
            "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω", "Γ", "Δ", "Θ", "Λ", "Ξ", "Π", "Σ", "Υ", "Φ", "Ψ", "Ω"
        ]
        keyboard_frame = tk.Frame(parent, bg="#333")
        keyboard_frame.pack(pady=10)
        for symbol in greek_symbols:
            button = tk.Button(keyboard_frame, text=symbol, width=3, command=lambda s=symbol: self.insert_symbol(s),
                               bg="#555", fg="#f0f0f0", font=("Arial", 12))
            button.pack(side="left", padx=2, pady=2)

    def insert_symbol(self, symbol):
        if self.main_symbol.get() == "Symbol":
            self.main_symbol.delete(0, tk.END)
        self.main_symbol.insert(tk.END, symbol)

    def generate_latex_code(self):
        main_symbol = self.main_symbol.get()
        sup_before = self.sup_before.get() if self.sup_before.get() != "Hochgestellt Links" else ""
        sub_before = self.sub_before.get() if self.sub_before.get() != "Tiefgestellt Links" else ""
        sup_after = self.sup_after.get() if self.sup_after.get() != "Hochgestellt Rechts" else ""
        sub_after = self.sub_after.get() if self.sub_after.get() != "Tiefgestellt Rechts" else ""
        selected_symbol = self.symbol_select.get().split()[0] if self.symbol_select.get() != "Kein Symbol" else ""

        # Generiere den LaTeX-Code nur für nicht-leere Felder
        latex_code = "$"
        if sub_before or sup_before:
            latex_code += f"_{{{sub_before}}}^{{{sup_before}}}"
        
        # Falls ein Sonderzeichen gewählt ist, formatiere das Hauptsymbol entsprechend
        if main_symbol and main_symbol != "Symbol":
            latex_code += f"{selected_symbol}{{{main_symbol}}}" if selected_symbol else main_symbol

        if sub_after or sup_after:
            latex_code += f"_{{{sub_after}}}^{{{sup_after}}}"
        
        latex_code += "$"

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, latex_code)
        self.copy_to_clipboard(latex_code)

    def copy_to_clipboard(self, latex_code):
        self.root.clipboard_clear()
        self.root.clipboard_append(latex_code)
        messagebox.showinfo("LaTeX Code", "LaTeX-Code wurde kopiert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexFormulaCreatorApp(root)
    root.mainloop()
