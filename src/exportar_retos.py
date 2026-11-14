import os
from importlib import import_module

# Se reutiliza la funcion del script de simulacion (no se copia su codigo)
simular_retos = import_module("simular_retos")
generar_retos = simular_retos.generar_retos

CARPETA = "data/crudo"


def exportar():
    df = generar_retos()

    # La carpeta se crea sola si no existe
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "retos_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "retos_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "retos_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="retos")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    # Ruta y tamano (filas, columnas) de cada archivo generado
    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    exportar()