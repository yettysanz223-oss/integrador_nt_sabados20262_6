import os
import sys
from pathlib import Path

# Para poder importar la carpeta simulaciones/ sin importar desde dónde se ejecute
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulaciones.simular_empresas import generar_empresas

# Raíz del proyecto: exportaciones -> Notebook -> src -> raíz
RAIZ = Path(__file__).resolve().parents[3]
CARPETA = os.path.join(RAIZ, "data", "crudo")


def exportar(df):
    """Guarda el DataFrame como empresas_sucio.csv, .xlsx y .json en data/crudo/."""
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "empresas_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "empresas_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "empresas_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


def main():
    df = generar_empresas()
    exportar(df)


if __name__ == "__main__":
    main()
