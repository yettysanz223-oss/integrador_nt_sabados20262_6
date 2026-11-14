#!/usr/bin/env python3
"""Revisa empresas_sucio (.csv, .xlsx o .json) contra las HU E6-EMP-F01 y E6-EMP-X01.

Uso:
    python revisar_datos.py data/crudo/empresas_sucio.csv

Imprime una tabla en Markdown con: Comprobación | Esperado | Encontrado | Estado.
Usa pandas solo porque hace falta para leer Excel (con openpyxl).
"""
import json
import sys
from pathlib import Path

import pandas as pd

# --- Criterios de las HU de empresas ---------------------------------------
FILAS_ESPERADAS = 300
COLUMNAS_ESPERADAS = [
    "id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa",
]
PCT_NULOS_CONTACTO = 8.0   # contacto: 8% en None
PCT_EXACTOS = 5.0          # 5% de filas repetidas tal cual
PCT_NIT_REPETIDOS = 3.0    # 3% de NIT repetidos entre empresas distintas
TOLERANCIA = 3.0           # margen en puntos porcentuales para los %


def fila(comprobacion, esperado, encontrado, ok):
    """Arma una fila del reporte; convierte el booleano en PASA / FALLA."""
    return (comprobacion, str(esperado), str(encontrado), "PASA" if ok else "FALLA")


def porcentaje(cantidad, total):
    """Devuelve cantidad como % de total (0 si total es 0)."""
    return 100.0 * cantidad / total if total else 0.0


def leer_archivo(ruta):
    """Lee el CSV, Excel o JSON y devuelve (DataFrame, comprobaciones_extra).

    Todo se lee como texto para no alterar los valores sucios. En Excel
    también revisa que la hoja se llame "empresas" (criterio de X01).
    """
    extra = []
    sufijo = ruta.suffix.lower()
    if sufijo == ".csv":
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    elif sufijo in (".xlsx", ".xls"):
        hojas = pd.ExcelFile(ruta).sheet_names
        existe = "empresas" in hojas
        extra.append(fila('Hoja de Excel "empresas"', "empresas", ", ".join(hojas), existe))
        df = pd.read_excel(ruta, sheet_name="empresas" if existe else 0, dtype=str)
    elif sufijo == ".json":
        with open(ruta, encoding="utf-8") as f:
            df = pd.DataFrame(json.load(f))  # orient="records": lista de objetos
    else:
        raise ValueError(f"Formato no soportado: {sufijo} (usa .csv, .xlsx o .json)")
    return df, extra


def revisar_filas_y_columnas(df):
    """Comprueba el número de filas y que estén exactamente las columnas de la HU."""
    faltan = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
    sobran = [c for c in df.columns if c not in COLUMNAS_ESPERADAS]
    if not faltan and not sobran:
        encontrado = f"las {len(COLUMNAS_ESPERADAS)} columnas"
    else:
        partes = []
        if faltan:
            partes.append("faltan: " + ", ".join(faltan))
        if sobran:
            partes.append("sobran: " + ", ".join(map(str, sobran)))
        encontrado = "; ".join(partes)
    return [
        fila("Número de filas", FILAS_ESPERADAS, len(df), len(df) == FILAS_ESPERADAS),
        fila("Columnas de la HU", ", ".join(COLUMNAS_ESPERADAS), encontrado, not faltan and not sobran),
    ]


def revisar_nulos(df):
    """Cuenta los nulos de cada columna: contacto ≈8%, las demás en 0."""
    resultados = []
    n = len(df)
    for col in COLUMNAS_ESPERADAS:
        if col not in df.columns:
            resultados.append(fila(f"Nulos en {col}", "columna presente", "columna ausente", False))
            continue
        nulos = int(df[col].isna().sum())
        pct = porcentaje(nulos, n)
        encontrado = f"{nulos} ({pct:.1f}%)"
        if col == "contacto":
            esperado = f"≈{PCT_NULOS_CONTACTO:.0f}% (±{TOLERANCIA:.0f} pts)"
            ok = abs(pct - PCT_NULOS_CONTACTO) <= TOLERANCIA
        else:
            esperado = "0"
            ok = nulos == 0
        resultados.append(fila(f"Nulos en {col}", esperado, encontrado, ok))
    return resultados


def revisar_duplicados(df):
    """Cuenta filas repetidas tal cual, NIT repetidos y duplicados por columna."""
    resultados = []
    n = len(df)
    exactas = int(df.duplicated().sum())
    pct_exactas = porcentaje(exactas, n)
    resultados.append(fila(
        "Filas duplicadas exactas",
        f"≈{PCT_EXACTOS:.0f}% (±{TOLERANCIA:.0f} pts)",
        f"{exactas} ({pct_exactas:.1f}%)",
        abs(pct_exactas - PCT_EXACTOS) <= TOLERANCIA,
    ))

    # NIT repetidos entre empresas distintas, sin contar las copias exactas
    if "nit" in df.columns:
        nit_rep = int(df.drop_duplicates().duplicated(subset=["nit"]).sum())
        pct_nit = porcentaje(nit_rep, n)
        resultados.append(fila(
            "NIT repetidos entre empresas distintas",
            f"≈{PCT_NIT_REPETIDOS:.0f}% (±{TOLERANCIA:.0f} pts)",
            f"{nit_rep} ({pct_nit:.1f}%)",
            abs(pct_nit - PCT_NIT_REPETIDOS) <= TOLERANCIA,
        ))
    else:
        resultados.append(fila("NIT repetidos entre empresas distintas",
                               "columna nit presente", "falta la columna", False))

    for col in COLUMNAS_ESPERADAS:
        if col not in df.columns:
            resultados.append(fila(f"Duplicados en {col}", "columna presente", "columna ausente", False))
            continue
        # Los nulos no se cuentan como duplicados entre sí
        dups = int(df[col].dropna().duplicated().sum())
        if col == "id":
            # El id solo debe repetirse en las copias exactas
            resultados.append(fila("Duplicados en id", f"{exactas} (solo las copias exactas)", dups, dups == exactas))
        else:
            # La HU no fija un número para estas columnas: solo se informa el conteo
            resultados.append(fila(f"Duplicados en {col}", "sin criterio (solo conteo)", dups, True))
    return resultados


def tabla_markdown(resultados):
    """Convierte la lista de filas en una tabla Markdown."""
    def celda(texto):
        return str(texto).replace("|", "\\|")
    lineas = ["| Comprobación | Esperado | Encontrado | Estado |", "|---|---|---|---|"]
    for fila_ in resultados:
        lineas.append("| " + " | ".join(celda(c) for c in fila_) + " |")
    return "\n".join(lineas)


def main(argv):
    """Punto de entrada: lee el archivo, ejecuta las revisiones e imprime la tabla."""
    if len(argv) != 2:
        print("Uso: python revisar_datos.py data/crudo/empresas_sucio.csv", file=sys.stderr)
        return 1
    ruta = Path(argv[1])
    if not ruta.exists():
        print(f"No existe el archivo: {ruta}", file=sys.stderr)
        return 1
    try:
        df, extra = leer_archivo(ruta)
    except Exception as error:  # archivo dañado o formato no soportado
        print(f"No se pudo leer {ruta}: {error}", file=sys.stderr)
        return 1
    resultados = extra + revisar_filas_y_columnas(df) + revisar_nulos(df) + revisar_duplicados(df)
    print(tabla_markdown(resultados))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
