#!/usr/bin/env python3
"""Responde las cinco consultas de la HU E6-REG-Q01 sobre registros_limpio.csv.

Uso:
    python scripts/consultas_registros.py registros_limpio.csv

Imprime el titulo y el resultado de cada consulta, en orden, y guarda
registros_consulta_1.csv ... registros_consulta_5.csv en la misma carpeta
del archivo de entrada (data/limpio/ en el proyecto).
"""
import sys
from pathlib import Path

import pandas as pd

# Columnas que usan las consultas (el archivo limpio ya trae la columna mes)
COLUMNAS = ["id", "estado", "id_usuario", "id_reto", "mes"]
# Cuantas filas se muestran en consola en las consultas que devuelven filas
FILAS_A_MOSTRAR = 10


def leer_datos(ruta):
    """Lee el CSV limpio con pandas."""
    return pd.read_csv(ruta, encoding="utf-8")


def mostrar_filas(resultado):
    """Imprime cuantas filas tiene el resultado y las primeras FILAS_A_MOSTRAR."""
    print(f"Filas encontradas: {len(resultado)}")
    if resultado.empty:
        print("(ninguna)")
        return
    print(resultado.head(FILAS_A_MOSTRAR).to_string(index=False))
    if len(resultado) > FILAS_A_MOSTRAR:
        print(f"... se muestran {FILAS_A_MOSTRAR} de {len(resultado)}; todas van en el CSV")


def consulta_1_finalizados(df):
    """Consulta 1: participaciones ya finalizadas."""
    print("Consulta 1 - Participaciones ya finalizadas")
    finalizados = df[df["estado"] == "FINALIZADO"]
    mostrar_filas(finalizados)
    return finalizados


def consulta_2_repetidos(df):
    """Consulta 2: participaciones repetidas (mismo usuario en el mismo reto)."""
    print("Consulta 2 - Participaciones repetidas (mismo usuario en el mismo reto)")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    # Se ordena solo para ver juntas las filas de cada par repetido
    repetidos = repetidos.sort_values(["id_usuario", "id_reto"])
    mostrar_filas(repetidos)
    return repetidos


def consulta_3_por_estado(df):
    """Consulta 3: cuantas participaciones hay por estado."""
    print("Consulta 3 - Cuantas participaciones hay por estado")
    conteo = df["estado"].value_counts()
    print(conteo)
    return conteo


def consulta_4_top_retos(df):
    """Consulta 4 (groupby): los 10 retos con mas participantes."""
    print("Consulta 4 - GROUPBY: los 10 retos con mas participantes")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    print(top_retos)
    return top_retos


def consulta_5_por_mes(df):
    """Consulta 5 (groupby): cuantas participaciones hubo cada mes."""
    print("Consulta 5 - GROUPBY por mes: cuantas participaciones hubo cada mes")
    por_mes = df.groupby("mes")["id"].count()
    print(por_mes)
    return por_mes


def guardar_resultado(resultado, numero, carpeta):
    """Guarda el resultado de la consulta N como registros_consulta_N.csv y devuelve la ruta."""
    ruta = carpeta / f"registros_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series):
        # Los conteos son Series: se pasan a tabla con una columna "cantidad"
        resultado = resultado.rename("cantidad").reset_index()
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def main(argv):
    """Punto de entrada: lee el CSV limpio, resuelve las cinco consultas y guarda cada una."""
    if len(argv) != 2:
        print("Uso: python scripts/consultas_registros.py registros_limpio.csv", file=sys.stderr)
        return 1
    ruta = Path(argv[1])
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
        consulta_1_finalizados,
        consulta_2_repetidos,
        consulta_3_por_estado,
        consulta_4_top_retos,
        consulta_5_por_mes,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        destino = guardar_resultado(resultado, numero, carpeta)
        print(f"Guardado en: {destino}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))