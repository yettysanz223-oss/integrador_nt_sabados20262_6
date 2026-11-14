#!/usr/bin/env python3
"""Limpia registros_sucio.csv siguiendo la HU E6-REG-L01.

Uso:
    python scripts/limpiar_registros.py registros_sucio.csv

Imprime el diagnostico antes y despues de limpiar y cuantas filas se eliminaron.
Guarda registros_limpio.csv: si el archivo sucio esta en una carpeta "crudo"
(data/crudo/), lo guarda en la carpeta hermana "limpio" (data/limpio/); si no,
lo guarda junto al archivo de entrada.
"""
import sys
from pathlib import Path

import pandas as pd

# Columnas que debe traer el archivo sucio (las mismas de la tabla registros)
COLUMNAS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"]


def leer_datos(ruta):
    """Lee el CSV sucio con pandas."""
    return pd.read_csv(ruta, encoding="utf-8")


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())
    print()


def limpiar(df):
    """Corrige uno por uno los errores de la HU y devuelve el DataFrame limpio."""
    # 1. Quitar los duplicados exactos
    antes = len(df)
    df = df.drop_duplicates().copy()  # .copy() evita el SettingWithCopyWarning
    print(f"Duplicados exactos eliminados: {antes - len(df)}")

    # 2. Convertir la fecha aunque venga en dos formatos
    nulos_antes = df["fecha_registro"].isna().sum()
    df["fecha_registro"] = pd.to_datetime(
        df["fecha_registro"], format="mixed", dayfirst=True, errors="coerce"
    )
    invalidas = df["fecha_registro"].isna().sum() - nulos_antes
    print(f"Fechas que no se pudieron convertir (quedan NaT): {invalidas}")

    # 3. Unificar el estado: sin espacios sobrantes, mayusculas y guion bajo
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")

    # 4. Rellenar las observaciones vacias
    df["observacion"] = df["observacion"].fillna("Sin observacion")

    # 5. Detectar las participaciones repetidas (mismo usuario en el mismo reto)
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"Filas con participaciones repetidas (usuario + reto): {len(repetidos)}")

    # 6. Dejar solo la primera participacion de cada par
    antes = len(df)
    df = df.drop_duplicates(subset=["id_usuario", "id_reto"], keep="first").copy()
    print(f"Participaciones repetidas eliminadas: {antes - len(df)}")

    # 7. Crear la columna mes para agrupar despues
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    print()
    return df


def comprobar_resultado(df):
    """Verifica que no queden nulos ni duplicados exactos e imprime el resultado."""
    nulos = int(df.isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("===== Comprobacion final =====")
    print(f"Nulos en todo el DataFrame: {nulos} -> {'PASA' if nulos == 0 else 'FALLA'}")
    print(f"Duplicados exactos: {duplicados} -> {'PASA' if duplicados == 0 else 'FALLA'}")
    print()


def ruta_salida(ruta_entrada):
    """Devuelve la ruta de registros_limpio.csv (data/limpio/ si la entrada esta en data/crudo/)."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "crudo":
        carpeta = carpeta.parent / "limpio"
    return carpeta / "registros_limpio.csv"


def main(argv):
    """Punto de entrada: lee, diagnostica, limpia, diagnostica otra vez y guarda."""
    if len(argv) != 2:
        print("Uso: python scripts/limpiar_registros.py registros_sucio.csv", file=sys.stderr)
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

    filas_antes = len(df)
    imprimir_diagnostico(df, "DIAGNOSTICO ANTES")
    df = limpiar(df)
    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES")
    print(f"Filas eliminadas: {filas_antes - len(df)} (antes {filas_antes}, despues {len(df)})\n")
    comprobar_resultado(df)

    destino = ruta_salida(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"Archivo limpio guardado en: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))