import os
import sys
from importlib import import_module

# 1. Importar la función del script de simulación (sin copiar su código)
RUTA_SIMULACIONES = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "simulaciones")
)
sys.path.append(RUTA_SIMULACIONES)

simulacion = import_module("simulacion_prioridades")
generar_prioridades = simulacion.generar_prioridades

# 2. Rutas de salida (se ejecuta desde la raíz del repositorio)
CARPETA = "data/crudo"
RUTA_CSV = f"{CARPETA}/prioridades_sucio.csv"
RUTA_XLSX = f"{CARPETA}/prioridades_sucio.xlsx"
RUTA_JSON = f"{CARPETA}/prioridades_sucio.json"


# 3. Función principal: genera los datos sucios y los guarda en 3 formatos
def exportar_prioridades():
    df = generar_prioridades()

    # La carpeta se crea sola si no existe
    os.makedirs(CARPETA, exist_ok=True)

    df.to_csv(RUTA_CSV, index=False, encoding="utf-8")
    df.to_excel(RUTA_XLSX, index=False, sheet_name="prioridades")
    df.to_json(RUTA_JSON, orient="records", force_ascii=False, indent=2)

    # 4. Mostrar la ruta, el tamaño de la tabla y el peso de cada archivo
    for ruta in (RUTA_CSV, RUTA_XLSX, RUTA_JSON):
        print(f"{ruta} -> filas y columnas: {df.shape}, peso: {os.path.getsize(ruta)} bytes")

    return df


if __name__ == "__main__":
    exportar_prioridades()