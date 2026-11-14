"""HU Q01: cinco consultas con pandas sobre la tabla prioridades.

Ejecutar desde la raiz del repositorio:
    python notebook/consultas/consultas_prioridades.py

Lee:
    data/limpio/prioridades_limpio.csv   (el archivo LIMPIO, no el sucio)

Genera:
    data/limpio/prioridades_consulta_1.csv ... prioridades_consulta_5.csv
"""
import os

import pandas as pd

# 1. Rutas (se ejecuta desde la raiz del repositorio)
RUTA_LIMPIO = "data/limpio/prioridades_limpio.csv"
CARPETA_SALIDA = "data/limpio"


def consulta_1_ordenadas(df):
    """Consulta 1: prioridades ordenadas de la mas urgente a la menos urgente."""
    print("\n=== Consulta 1: Prioridades ordenadas de la mas urgente a la menos urgente ===")
    ordenadas = df.sort_values("nivel")
    print(ordenadas.to_string(index=False))
    return ordenadas


def consulta_2_urgentes(df):
    """Consulta 2: solo las prioridades urgentes (nivel 1 y 2)."""
    print("\n=== Consulta 2: Solo las prioridades urgentes (nivel 1 y 2) ===")
    urgentes = df[df["nivel"] <= 2]
    print(urgentes.to_string(index=False))
    return urgentes


def consulta_3_conteo_nombres(df):
    """Consulta 3: cuantas veces aparece cada nombre (detecta las variantes)."""
    print("\n=== Consulta 3: Cuantas veces aparece cada nombre (detecta las variantes) ===")
    conteo = df["nombre"].value_counts()
    conteo.index.name = "nombre"
    conteo.name = "veces"
    print(conteo.to_string())
    return conteo.reset_index()


def consulta_4_filas_por_nivel(df):
    """Consulta 4 (GROUPBY): cuantas filas hay por nivel."""
    print("\n=== Consulta 4: Cuantas filas hay por nivel (groupby) ===")
    por_nivel = df.groupby("nivel")["id"].count()
    por_nivel.name = "filas"
    print(por_nivel.to_string())
    return por_nivel.reset_index()


def consulta_5_dias_por_prioridad(df):
    """Consulta 5 (GROUPBY): dias de respuesta minimo, promedio y maximo por prioridad."""
    print("\n=== Consulta 5: Dias de respuesta minimo, promedio y maximo por prioridad (groupby) ===")
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    print(resumen.to_string())
    return resumen.reset_index()


def main():
    # 2. Leer el CSV limpio
    df = pd.read_csv(RUTA_LIMPIO)

    consultas = [
        consulta_1_ordenadas,
        consulta_2_urgentes,
        consulta_3_conteo_nombres,
        consulta_4_filas_por_nivel,
        consulta_5_dias_por_prioridad,
    ]

    # 3. Ejecutar cada consulta y guardar su resultado
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    for numero, funcion in enumerate(consultas, start=1):
        resultado = funcion(df)
        salida = f"{CARPETA_SALIDA}/prioridades_consulta_{numero}.csv"
        resultado.to_csv(salida, index=False, encoding="utf-8")

    print(f"\nListo: se guardaron prioridades_consulta_1.csv ... prioridades_consulta_5.csv en {CARPETA_SALIDA}")


if __name__ == "__main__":
    main()