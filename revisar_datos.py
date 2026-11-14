#!/usr/bin/env python3
"""Revisa registros_sucio (.csv, .xlsx o .json) contra las HU E6-REG-F01 y E6-REG-X01.

Uso:
    python scripts/revisar_datos.py registros_sucio.csv

Imprime una tabla en Markdown con: Comprobación | Esperado | Encontrado | Estado.
Usa pandas solo porque hace falta para leer Excel (con openpyxl).
"""
import json
import sys
from pathlib import Path

import pandas as pd

# --- Criterios tomados de references/criterios.md -------------------------
FILAS_ESPERADAS = 800
COLUMNAS_ESPERADAS = [
    "id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto",
]
PCT_NULOS_OBSERVACION = 20.0   # observacion: 20% en None
PCT_EXACTOS = 5.0              # 5% de filas repetidas tal cual
PCT_PARES_REPETIDOS = 10.0     # 10% con el par id_usuario + id_reto repetido
TOLERANCIA = 2.0               # margen en puntos porcentuales para los %


def fila(comprobacion, esperado, encontrado, ok):
    """Arma una fila del reporte; convierte el booleano en PASA / FALLA."""
    return (comprobacion, str(esperado), str(encontrado), "PASA" if ok else "FALLA")


def porcentaje(cantidad, total):
    """Devuelve cantidad como % de total (0 si total es 0)."""
    return 100.0 * cantidad / total if total else 0.0


def leer_archivo(ruta):
    """Lee el CSV, Excel o JSON y devuelve (DataFrame, comprobaciones_extra).

    Todo se lee como texto para no alterar los valores sucios. En Excel
    también revisa que la hoja se llame "registros" (criterio de X01).
    """
    extra = []
    sufijo = ruta.suffix.lower()
    if sufijo == ".csv":
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    elif sufijo in (".xlsx", ".xls"):
        hojas = pd.ExcelFile(ruta).sheet_names
        existe = "registros" in hojas
        extra.append(fila('Hoja de Excel "registros"', "registros", ", ".join(hojas), existe))
        df = pd.read_excel(ruta, sheet_name="registros" if existe else 0, dtype=str)
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
        encontrado = "las 6 columnas"
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
    """Cuenta los nulos de cada columna: observacion ≈20%, las demás en 0."""
    resultados = []
    n = len(df)
    for col in COLUMNAS_ESPERADAS:
        if col not in df.columns:
            resultados.append(fila(f"Nulos en {col}", "columna presente", "columna ausente", False))
            continue
        nulos = int(df[col].isna().sum())
        pct = porcentaje(nulos, n)
        encontrado = f"{nulos} ({pct:.1f}%)"
        if col == "observacion":
            esperado = f"≈{PCT_NULOS_OBSERVACION:.0f}% (±{TOLERANCIA:.0f} pts)"
            ok = abs(pct - PCT_NULOS_OBSERVACION) <= TOLERANCIA
        else:
            esperado = "0"
            ok = nulos == 0
        resultados.append(fila(f"Nulos en {col}", esperado, encontrado, ok))
    return resultados


def revisar_duplicados(df):
    """Cuenta duplicados por columna, filas repetidas tal cual y pares usuario+reto."""
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

    # Pares id_usuario + id_reto repetidos, sin contar las copias exactas
    if {"id_usuario", "id_reto"} <= set(df.columns):
        pares = int(df.drop_duplicates().duplicated(subset=["id_usuario", "id_reto"]).sum())
        pct_pares = porcentaje(pares, n)
        resultados.append(fila(
            "Pares id_usuario + id_reto repetidos",
            f"≥{PCT_PARES_REPETIDOS:.0f}% (−{TOLERANCIA:.0f} pts)",
            f"{pares} ({pct_pares:.1f}%)",
            pct_pares >= PCT_PARES_REPETIDOS - TOLERANCIA,
        ))
    else:
        resultados.append(fila("Pares id_usuario + id_reto repetidos",
                               "ambas columnas presentes", "falta una", False))

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
        print("Uso: python scripts/revisar_datos.py registros_sucio.csv", file=sys.stderr)
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