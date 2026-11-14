"""Limpia los datos sucios de la tabla `prioridades` (HU L01 de Kaizen).

Ejecutar desde la raiz del repositorio:
    python notebook/limpieza/limpiar_prioridades.py

Lee:
    data/crudo/prioridades_sucio.csv

Genera:
    data/limpio/prioridades_limpio.csv     -> tabla limpia
    data/limpio/prioridades_catalogo.csv   -> catalogo real (5 filas)
"""
import os

import pandas as pd

# 1. Rutas (se ejecuta desde la raiz del repositorio)
RUTA_SUCIO = "data/crudo/prioridades_sucio.csv"
CARPETA_LIMPIO = "data/limpio"
RUTA_LIMPIO = f"{CARPETA_LIMPIO}/prioridades_limpio.csv"
RUTA_CATALOGO = f"{CARPETA_LIMPIO}/prioridades_catalogo.csv"

# 2. Constantes (iguales a las de la simulacion)
NIVELES = {"Baja": 1, "Media": 2, "Alta": 3, "Urgente": 4, "Critica": 5}
PALABRAS = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]
DIAS_MAXIMO_VALIDO = 60


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def unificar_nombre(df):
    """Quita espacios y deja la primera letra en mayuscula (Alta, Media...)."""
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    return df


def convertir_nivel(df):
    """Pasa el nivel escrito con palabra a numero y todo a tipo numerico."""
    df["nivel"] = df["nivel"].astype("string").str.strip().str.lower()
    df["nivel"] = df["nivel"].replace(PALABRAS)
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    return df


def rellenar_nivel(df):
    """Rellena el nivel vacio usando el nombre de la prioridad."""
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES))
    return df


def limpiar_dias(df):
    """Convierte a numero, anula los absurdos (>60) y rellena con la mediana."""
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    absurdos = int((df["dias_max_respuesta"] > DIAS_MAXIMO_VALIDO).sum())
    df.loc[df["dias_max_respuesta"] > DIAS_MAXIMO_VALIDO, "dias_max_respuesta"] = None
    mediana = df["dias_max_respuesta"].median()
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(mediana)
    print(f"\nValores absurdos (>{DIAS_MAXIMO_VALIDO}) anulados: {absurdos}")
    print(f"Mediana usada para rellenar dias_max_respuesta: {mediana}")
    return df


def usar_enteros(df):
    """Deja nivel y dias_max_respuesta como enteros."""
    for col in ["nivel", "dias_max_respuesta"]:
        df[col] = df[col].round().astype("Int64")
    return df


def verificar(df):
    """Avisa si quedan nulos en columnas obligatorias o duplicados exactos."""
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    if nulos == 0 and duplicados == 0:
        print("\nOK: no quedan nulos ni duplicados exactos.")
    else:
        print(f"\nATENCION: quedan {nulos} nulos y {duplicados} duplicados exactos.")


def main():
    # 3. Leer el CSV sucio y diagnosticar
    df = pd.read_csv(RUTA_SUCIO)
    filas_inicio = len(df)
    imprimir_diagnostico(df, "ANTES DE LIMPIAR")

    # 4. Limpiar paso a paso
    df = df.drop_duplicates()
    df = unificar_nombre(df)
    df = convertir_nivel(df)
    df = rellenar_nivel(df)
    df = limpiar_dias(df)
    df = usar_enteros(df)
    df = df.drop_duplicates()  # por si al unificar aparecieron nuevos

    # 5. Catalogo real: una fila por nombre
    catalogo = df.drop_duplicates(subset=["nombre"])

    # 6. Diagnostico final
    imprimir_diagnostico(df, "DESPUES DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_inicio - len(df)}")
    verificar(df)

    # 7. Guardar resultados (la carpeta se crea sola si no existe)
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    df.to_csv(RUTA_LIMPIO, index=False, encoding="utf-8")
    catalogo.to_csv(RUTA_CATALOGO, index=False, encoding="utf-8")
    print(f"\nGuardado: {RUTA_LIMPIO}")
    print(f"Guardado: {RUTA_CATALOGO}")


if __name__ == "__main__":
    main()