from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Mount der statischen Dateien für die Homepage
# Dadurch wird index.html im gleichen Verzeichnis als Startseite bereitgestellt
app.mount("/", StaticFiles(directory=".", html=True), name="static")

class LatexTableData(BaseModel):
    headers: list[str]
    general_description: str
    header_descriptions: list[str]
    data_rows: list[list[str]]

@app.post("/upload_excel/")
async def upload_excel(file: UploadFile):
    # Überprüfen, ob die Datei eine Excel-Datei ist
    if file.filename.endswith(('.xlsx', '.xls')):
        # Lesen der Excel-Datei
        df = pd.read_excel(file.file)
        headers = df.columns.tolist()
        data_rows = df.values.tolist()
        return JSONResponse({
            "headers": headers,
            "data_rows": data_rows
        })
    else:
        return JSONResponse({"error": "Bitte eine gültige Excel-Datei hochladen"}, status_code=400)

@app.post("/generate_latex/")
async def generate_latex(data: LatexTableData):
    headers = data.headers
    general_description = data.general_description
    header_descriptions = data.header_descriptions
    data_rows = data.data_rows

    # Generieren der Tabellenkopfzeile
    header_row = " & ".join(headers) + " \\\\ \\midrule\n"
    # Generieren der Datenzeilen
    rows = "\n".join(" & ".join(map(str, row)) + " \\\\" for row in data_rows)
    
    # Aufbau des LaTeX-Tabellenkörpers
    table_body = f"\\begin{{tabular}}{{{'c' * len(headers)}}}\n\\toprule\n{header_row}{rows}\n\\bottomrule\n\\end{{tabular}}"

    # Beschreibung und Beschriftung der Tabelle
    description_text = f"{general_description} \\\\ {', '.join(header_descriptions)}" if header_descriptions else ""
    caption_text = f"\\caption{{{description_text}}}\n"
    latex_code = f"\\begin{{table}}[H]\n\\centering\n{caption_text}{table_body}\n\\end{{table}}"

    return {"latex_code": latex_code}

@app.post("/save_tex/")
async def save_tex(data: LatexTableData, filename: str = Form(...)):
    # Generieren des LaTeX-Codes
    latex_code = (await generate_latex(data))["latex_code"]
    # Speichern des LaTeX-Codes in einer Datei
    with open(f"{filename}.tex", "w") as file:
        file.write(latex_code)
    return JSONResponse({"message": f"LaTeX-Datei '{filename}.tex' erfolgreich gespeichert."})
