import os
import sys
from importlib import import_module
from pathlib import Path

# Rutas calculadas desde la ubicación de este archivo (funcionan sin importar
# desde qué carpeta se ejecute):
#   <raíz>/src/Notebook/exportaciones/exportar_registros.py
CARPETA_NOTEBOOK = Path(__file__).resolve().parents[1]  # <raíz>/src/Notebook
RAIZ = Path(__file__).resolve().parents[3]              # <raíz> del proyecto
CARPETA_CRUDO = RAIZ / "data" / "crudo"

# Para poder importar "simulaciones" aunque se ejecute este archivo solo
if str(CARPETA_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(CARPETA_NOTEBOOK))

# Se importa la función del script anterior; no se copia el código de generación
generar_registros = import_module("simulaciones.simular_registros").generar_registros


def exportar(df=None):
    """Guarda el DataFrame sucio en CSV, Excel y JSON dentro de data/crudo/.

    Si no se pasa un DataFrame, lo genera con generar_registros().
    """
    if df is None:
        df = generar_registros()
    os.makedirs(CARPETA_CRUDO, exist_ok=True)

    ruta_csv = CARPETA_CRUDO / "registros_sucio.csv"
    ruta_xlsx = CARPETA_CRUDO / "registros_sucio.xlsx"
    ruta_json = CARPETA_CRUDO / "registros_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(ruta.relative_to(RAIZ), df.shape)


if __name__ == "__main__":
    exportar()