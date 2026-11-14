#!/usr/bin/env python3
"""Limpia empresas_sucio.csv siguiendo la HU E6-EMP-L01.

Uso:
    python src/Notebook/limpiezas/limpiar_empresas.py data/crudo/empresas_sucio.csv

Si no se pasa ninguna ruta, se usa data/crudo/empresas_sucio.csv de la raíz del proyecto.
Imprime el diagnostico antes y despues de limpiar y cuantas filas se eliminaron.
Guarda empresas_limpio.csv: si el archivo sucio esta en una carpeta "crudo"
(data/crudo/), lo guarda en la carpeta hermana "limpio" (data/limpio/); si no,
lo guarda junto al archivo de entrada.
"""
import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: limpiezas -> Notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_POR_DEFECTO = RAIZ / "data" / "crudo" / "empresas_sucio.csv"

# Columnas que debe traer el archivo sucio (las mismas de la tabla empresas)
COLUMNAS = ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"]
# Columnas obligatorias: despues de limpiar no puede quedar ningun nulo aqui
OBLIGATORIAS = ["id", "nombre", "nit", "sector", "telefono", "activa"]


def leer_datos(ruta):
    """Lee el CSV sucio con pandas (todo como texto para no perder ceros ni formatos)."""
    return pd.read_csv(ruta, encoding="utf-8", dtype=str)


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

    # 2. Quitar los espacios sobrantes del nombre
    df["nombre"] = df["nombre"].str.strip()

    # 3. Unificar el sector ('LOGISTICA' y ' logistica ' quedan como 'Logistica')
    df["sector"] = df["sector"].str.strip().str.title()

    # 4. Dejar el nit en un solo formato: sin puntos ni guiones
    df["nit"] = df["nit"].str.strip().str.replace(r"[.\-]", "", regex=True)

    # 5. Dejar el telefono solo con digitos
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)

    # 6. Convertir activa a booleano de verdad (al leer el CSV llega como TEXTO)
    df["activa"] = (
        df["activa"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({"TRUE": True, "SI": True, "1": True, "FALSE": False, "NO": False, "0": False})
    )

    # 7. Rellenar los contactos vacios
    df["contacto"] = df["contacto"].fillna("Sin contacto")

    # 8. Marcar los correos invalidos (sin arroba) en una columna nueva
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    print(f"Correos invalidos marcados: {(~df['correo_valido']).sum()}")

    # 9. Despues de normalizar pueden aparecer duplicados exactos nuevos
    antes = len(df)
    df = df.drop_duplicates().copy()
    print(f"Duplicados exactos nuevos tras normalizar: {antes - len(df)}")

    # 10. Avisar de los NIT repetidos entre empresas distintas (no se borran, solo se avisa)
    nit_repetidos = df[df.duplicated(subset=["nit"], keep=False)]
    print(f"Filas con NIT repetido entre empresas distintas: {len(nit_repetidos)}")
    print()
    return df


def comprobar_resultado(df):
    """Verifica que no queden nulos en las obligatorias ni duplicados exactos."""
    nulos = int(df[OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("===== Comprobacion final =====")
    print(f"Nulos en columnas obligatorias: {nulos} -> {'PASA' if nulos == 0 else 'FALLA'}")
    print(f"Duplicados exactos: {duplicados} -> {'PASA' if duplicados == 0 else 'FALLA'}")
    print()


def ruta_salida(ruta_entrada):
    """Devuelve la ruta de empresas_limpio.csv (data/limpio/ si la entrada esta en data/crudo/)."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "crudo":
        carpeta = carpeta.parent / "limpio"
    return carpeta / "empresas_limpio.csv"


def main(argv):
    """Punto de entrada: lee, diagnostica, limpia, diagnostica otra vez y guarda."""
    if len(argv) > 2:
        print("Uso: python src/Notebook/limpiezas/limpiar_empresas.py [empresas_sucio.csv]", file=sys.stderr)
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
