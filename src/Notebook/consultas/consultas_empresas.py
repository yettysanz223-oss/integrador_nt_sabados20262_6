#!/usr/bin/env python3
"""Responde las cinco consultas de la HU E6-EMP-Q01 sobre empresas_limpio.csv.

Uso:
    python src/Notebook/consultas/consultas_empresas.py data/limpio/empresas_limpio.csv

Si no se pasa ninguna ruta, se usa data/limpio/empresas_limpio.csv de la raíz del proyecto.
Imprime el titulo y el resultado de cada consulta, en orden, y guarda
empresas_consulta_1.csv ... empresas_consulta_5.csv en la misma carpeta
del archivo de entrada (data/limpio/ en el proyecto).
"""
import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: consultas -> Notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_POR_DEFECTO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"

# Columnas que usan las consultas
COLUMNAS = ["id", "nombre", "sector", "activa"]
# Cuantas filas se muestran en consola en las consultas que devuelven filas
FILAS_A_MOSTRAR = 10


def leer_datos(ruta):
    """Lee el CSV limpio con pandas (nit y telefono como texto)."""
    return pd.read_csv(ruta, encoding="utf-8", dtype={"nit": str, "telefono": str})


def mostrar_filas(resultado):
    """Imprime cuantas filas tiene el resultado y las primeras FILAS_A_MOSTRAR."""
    print(f"Filas encontradas: {len(resultado)}")
    if resultado.empty:
        print("(ninguna)")
        return
    print(resultado.head(FILAS_A_MOSTRAR).to_string(index=False))
    if len(resultado) > FILAS_A_MOSTRAR:
        print(f"... se muestran {FILAS_A_MOSTRAR} de {len(resultado)}; todas van en el CSV")


def consulta_1_activas(df):
    """Consulta 1: empresas activas."""
    print("Consulta 1 - Cuales son las empresas activas")
    activas = df[df["activa"] == True]
    mostrar_filas(activas)
    return activas


def consulta_2_logistica(df):
    """Consulta 2: empresas del sector Logistica, ordenadas por nombre."""
    print("Consulta 2 - Que empresas son del sector Logistica, ordenadas por nombre")
    logistica = df[df["sector"] == "Logistica"].sort_values("nombre")
    mostrar_filas(logistica)
    return logistica


def consulta_3_por_sector(df):
    """Consulta 3: cuantas empresas hay por sector (conteo rapido)."""
    print("Consulta 3 - Cuantas empresas hay por sector (conteo rapido)")
    conteo = df["sector"].value_counts()
    print(conteo)
    return conteo


def consulta_4_groupby_sector(df):
    """Consulta 4 (groupby): empresas por sector, de mayor a menor."""
    print("Consulta 4 - GROUPBY: empresas por sector, de mayor a menor")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    print(por_sector)
    return por_sector


def consulta_5_activas_por_sector(df):
    """Consulta 5 (groupby doble): activas e inactivas por sector."""
    print("Consulta 5 - GROUPBY doble: activas e inactivas por sector")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla)
    return tabla


def guardar_resultado(resultado, numero, carpeta):
    """Guarda el resultado de la consulta N como empresas_consulta_N.csv y devuelve la ruta."""
    ruta = carpeta / f"empresas_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series):
        # Los conteos son Series: se pasan a tabla
        resultado = resultado.rename("cantidad").reset_index()
    elif resultado.index.name is not None:
        # La tabla del groupby doble trae el sector como indice
        resultado = resultado.reset_index()
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def main(argv):
    """Punto de entrada: lee el CSV limpio, resuelve las cinco consultas y guarda cada una."""
    if len(argv) > 2:
        print("Uso: python src/Notebook/consultas/consultas_empresas.py [empresas_limpio.csv]", file=sys.stderr)
        return 1
    ruta = Path(argv[1]) if len(argv) == 2 else RUTA_POR_DEFECTO
    if not ruta.exists():
        print(f"No existe el archivo: {ruta}", file=sys.stderr)
        return 1

    df = leer_datos(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        print("Faltan columnas en el archivo: " + ", ".join(faltan), file=sys.stderr)
        return 1

    carpeta = ruta.resolve().parent
    consultas = [
        consulta_1_activas,
        consulta_2_logistica,
        consulta_3_por_sector,
        consulta_4_groupby_sector,
        consulta_5_activas_por_sector,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        destino = guardar_resultado(resultado, numero, carpeta)
        print(f"Guardado en: {destino}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
