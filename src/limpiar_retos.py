"""Limpieza de la tabla retos (HU L01 de Kaizen).

Uso (desde la raiz del proyecto):
    python src/limpiar_retos.py
    python src/limpiar_retos.py data/crudo/retos_sucio.csv

Lee el CSV sucio, imprime el diagnostico (antes), corrige los errores que
sembro la simulacion, imprime el diagnostico otra vez (despues) y guarda
data/limpio/retos_limpio.csv.
"""
import os
import sys

import pandas as pd

RUTA_ENTRADA = os.path.join("data", "crudo", "retos_sucio.csv")
RUTA_SALIDA = os.path.join("data", "limpio", "retos_limpio.csv")

# Columnas que no pueden quedar con nulos despues de limpiar.
# fecha_fin queda fuera a proposito: la HU no define como rellenarla y
# inventar fechas falsearia los datos; esas filas se marcan con
# fecha_valida = False (ver crear_duracion_y_validar).
COLUMNAS_OBLIGATORIAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]


def leer_csv(ruta):
    """Lee el CSV sucio con pd.read_csv() y devuelve el DataFrame."""
    if not os.path.exists(ruta):
        sys.exit(
            f"Error: no existe el archivo '{ruta}'. "
            "Ejecuta primero 'python src/exportar_retos.py' desde la raiz del proyecto."
        )
    return pd.read_csv(ruta)


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print(f"shape: {df.shape}")
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print(f"\nDuplicados exactos: {df.duplicated().sum()}")


def quitar_duplicados(df):
    """Elimina las filas duplicadas exactas."""
    return df.drop_duplicates()


def limpiar_espacios(df):
    """Quita los espacios sobrantes al inicio y al final de nombre y descripcion."""
    for col in ["nombre", "descripcion"]:
        if col in df.columns:
            df[col] = df[col].str.strip()
    return df


def convertir_serie_fechas(serie):
    """Convierte una columna de fechas con formatos mezclados a datetime.

    Las fechas ISO (AAAA-MM-DD) se leen aparte: con dayfirst=True pandas las
    podria invertir (2026-03-05 saldria como 5 de marzo -> 3 de mayo). El resto
    (DD/MM/AAAA, etc.) usa la instruccion de los criterios.
    """
    texto = serie.astype("string").str.strip()
    es_iso = texto.str.match(r"^\d{4}-\d{1,2}-\d{1,2}", na=False)
    resultado = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")
    if es_iso.any():
        resultado[es_iso] = pd.to_datetime(
            texto[es_iso], format="ISO8601", errors="coerce"
        )
    if (~es_iso).any():
        resultado[~es_iso] = pd.to_datetime(
            texto[~es_iso], format="mixed", dayfirst=True, errors="coerce"
        )
    return resultado


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime aceptando varios formatos."""
    for col in ["fecha_inicio", "fecha_fin"]:
        if col in df.columns:
            df[col] = convertir_serie_fechas(df[col])
    return df


def unificar_estado(df):
    """Quita espacios, pasa a mayusculas y cambia espacios internos por guion bajo."""
    if "estado" in df.columns:
        df["estado"] = (
            df["estado"].str.strip().str.upper().str.replace(" ", "_", regex=False)
        )
    return df


def rellenar_descripcion(df):
    """Rellena las descripciones vacias con 'Sin descripcion'."""
    if "descripcion" in df.columns:
        df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def crear_duracion_y_validar(df):
    """Crea duracion_dias y fecha_valida (False si fin antes que inicio o falta fecha_fin)."""
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    df["fecha_valida"] = df["duracion_dias"] >= 0
    return df


def guardar(df, ruta):
    """Crea la carpeta de salida si hace falta y guarda el CSV limpio."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")


def main():
    """Ejecuta todo el proceso de limpieza."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA

    df = leer_csv(ruta_entrada)
    filas_antes = len(df)
    nulos_antes = df.isna().sum()

    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados(df)
    df = limpiar_espacios(df)
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripcion(df)
    df = crear_duracion_y_validar(df)

    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

    # Nulos corregidos por columna (solo columnas que ya existian)
    nulos_despues = df.isna().sum()
    comparacion = pd.DataFrame(
        {"antes": nulos_antes, "despues": nulos_despues.reindex(nulos_antes.index)}
    )
    comparacion["corregidos"] = comparacion["antes"] - comparacion["despues"]
    print("\nNulos antes vs despues:")
    print(comparacion)

    eliminadas = filas_antes - len(df)
    fin_antes_inicio = int((df["duracion_dias"] < 0).sum())
    sin_fecha_fin = int(df["fecha_fin"].isna().sum())
    print(f"\nFilas eliminadas (duplicados): {eliminadas}")
    print(f"Fechas incoherentes (fin antes que inicio): {fin_antes_inicio}")
    print(f"Retos sin fecha_fin (no se inventa, quedan con fecha_valida=False): {sin_fecha_fin}")
    print(f"Filas con fecha_valida=False en total: {int((~df['fecha_valida']).sum())}")

    # Verificacion de los criterios finales
    nulos_obl = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print(f"Nulos en columnas obligatorias {COLUMNAS_OBLIGATORIAS}: {nulos_obl}")
    print(f"Duplicados exactos restantes: {duplicados}")
    if nulos_obl or duplicados:
        print("AVISO: aun quedan nulos obligatorios o duplicados (revisa fechas ilegibles).")

    guardar(df, RUTA_SALIDA)
    print(f"\nArchivo limpio guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
