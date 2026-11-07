import os

from simular_empresas import generar_empresas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA = os.path.join(RAIZ, "data", "crudo")


def main():
    os.makedirs(CARPETA, exist_ok=True)

    df = generar_empresas()

    ruta_csv = os.path.join(CARPETA, "empresas_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "empresas_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "empresas_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    main()