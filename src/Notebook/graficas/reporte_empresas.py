#!/usr/bin/env python3
"""Crea las tres graficas de la HU E6-EMP-G01 y escribe las conclusiones.

Uso:
    python src/Notebook/graficas/reporte_empresas.py data/limpio/empresas_limpio.csv

Si no se pasa ninguna ruta, se usa data/limpio/empresas_limpio.csv de la raíz del proyecto.
Guarda empresas_grafica_1.png, empresas_grafica_2.png y empresas_grafica_3.png
en la carpeta reportes/ (si el CSV esta en data/limpio/, reportes/ queda en la
raiz del proyecto; si no, junto al archivo de entrada). Imprime la ruta de cada
grafica y las conclusiones.
"""
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

# Raiz del proyecto: graficas -> Notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_POR_DEFECTO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"

# Columnas que usan las graficas y las conclusiones
COLUMNAS = ["id", "sector", "activa", "correo_valido"]


def leer_datos(ruta):
    """Lee el CSV limpio con pandas y deja activa y correo_valido como booleanos."""
    df = pd.read_csv(ruta, encoding="utf-8", dtype={"nit": str, "telefono": str})
    for columna in ("activa", "correo_valido"):
        if columna in df.columns:
            df[columna] = df[columna].astype(str).str.strip().str.lower().map({"true": True, "false": False})
    return df


def carpeta_reportes(ruta_entrada):
    """Devuelve la carpeta reportes/ (en la raiz del proyecto si el CSV esta en data/limpio/)."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "limpio" and carpeta.parent.name == "data":
        carpeta = carpeta.parent.parent
    return carpeta / "reportes"


def calcular_consultas(df):
    """Calcula los resultados que se grafican (los mismos de la etapa de consultas)."""
    por_sector = df["sector"].value_counts()
    activas = df["activa"].map({True: "Activas", False: "Inactivas"}).value_counts()
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    tabla = tabla.reindex(columns=[True, False], fill_value=0)
    tabla.columns = ["Activas", "Inactivas"]
    return por_sector, activas, tabla


def guardar_grafica(ruta):
    """Ajusta el diseno, guarda la imagen con dpi=120 y cierra la figura."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1_sectores(por_sector, carpeta):
    """Grafica 1: barras con la cantidad de empresas por sector."""
    por_sector.plot(kind="bar", figsize=(8, 5))
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45, ha="right")
    ruta = carpeta / "empresas_grafica_1.png"
    guardar_grafica(ruta)
    return ruta


def grafica_2_activas(activas, carpeta):
    """Grafica 2: torta con empresas activas vs inactivas."""
    activas.plot(kind="pie", autopct="%1.1f%%", figsize=(8, 5))
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Proporcion de empresas")
    ruta = carpeta / "empresas_grafica_2.png"
    guardar_grafica(ruta)
    return ruta


def grafica_3_apiladas(tabla, carpeta):
    """Grafica 3: barras apiladas con activas e inactivas por sector."""
    tabla.plot(kind="bar", stacked=True, figsize=(8, 5))
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    ruta = carpeta / "empresas_grafica_3.png"
    guardar_grafica(ruta)
    return ruta


def escribir_conclusiones(df, por_sector, activas):
    """Arma la lista de conclusiones que responde las preguntas de la HU."""
    total = len(df)
    maximo = por_sector.max()
    lideres = sorted(por_sector[por_sector == maximo].index)
    pct_inactivas = 100 * activas.get("Inactivas", 0) / total
    invalidos = int((~df["correo_valido"]).sum())

    return [
        f"El sector con más empresas es {', '.join(lideres)} con {maximo} de {total} "
        f"({100 * maximo / total:.1f}%).",
        f"El {pct_inactivas:.1f}% de las empresas está inactivo: ese porcentaje no genera "
        "actividad real en la plataforma y conviene revisarlo.",
        f"Aparecieron {invalidos} correos inválidos (sin arroba). Hay que validarlos en el back "
        "porque la validación del front se puede saltar, y así ningún cliente, script o API "
        "puede guardar datos sucios en la base de datos.",
    ]


def main(argv):
    """Punto de entrada: lee el CSV limpio, crea las graficas e imprime rutas y conclusiones."""
    if len(argv) > 2:
        print("Uso: python src/Notebook/graficas/reporte_empresas.py [empresas_limpio.csv]", file=sys.stderr)
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
    if df.empty:
        print("El archivo no tiene filas: no hay nada que graficar.", file=sys.stderr)
        return 1

    carpeta = carpeta_reportes(ruta)
    os.makedirs(carpeta, exist_ok=True)

    por_sector, activas, tabla = calcular_consultas(df)
    rutas = [
        grafica_1_sectores(por_sector, carpeta),
        grafica_2_activas(activas, carpeta),
        grafica_3_apiladas(tabla, carpeta),
    ]
    for numero, ruta_png in enumerate(rutas, start=1):
        print(f"Gráfica {numero} guardada en: {ruta_png}")

    print("\nConclusiones:")
    for numero, texto in enumerate(escribir_conclusiones(df, por_sector, activas), start=1):
        print(f"{numero}. {texto}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
