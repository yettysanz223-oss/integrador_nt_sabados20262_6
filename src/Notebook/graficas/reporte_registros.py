#!/usr/bin/env python3
"""Crea las tres graficas de la HU E6-REG-G01 y escribe las conclusiones.

Uso:
    python scripts/reporte_registros.py registros_limpio.csv

Guarda registros_grafica_1.png, registros_grafica_2.png y registros_grafica_3.png
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

# Columnas que usan las graficas y las conclusiones (el CSV limpio ya trae mes)
COLUMNAS = ["id", "estado", "id_usuario", "id_reto", "mes"]


def leer_datos(ruta):
    """Lee el CSV limpio con pandas."""
    return pd.read_csv(ruta, encoding="utf-8")


def carpeta_reportes(ruta_entrada):
    """Devuelve la carpeta reportes/ (en la raiz del proyecto si el CSV esta en data/limpio/)."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "limpio" and carpeta.parent.name == "data":
        carpeta = carpeta.parent.parent
    return carpeta / "reportes"


def calcular_consultas(df):
    """Calcula los tres resultados que se grafican (los mismos de la etapa de consultas)."""
    conteo = df["estado"].value_counts()
    por_mes = df.groupby("mes")["id"].count()
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    return conteo, por_mes, top_retos


def guardar_grafica(ruta):
    """Ajusta el diseno, guarda la imagen con dpi=120 y cierra la figura."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1_estados(conteo, carpeta):
    """Grafica 1: barras con las participaciones por estado."""
    conteo.plot(kind="bar", figsize=(8, 5))
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=0)
    ruta = carpeta / "registros_grafica_1.png"
    guardar_grafica(ruta)
    return ruta


def grafica_2_meses(por_mes, carpeta):
    """Grafica 2: linea con las participaciones por mes."""
    por_mes.plot(kind="line", marker="o", figsize=(8, 5))
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=45, ha="right")
    ruta = carpeta / "registros_grafica_2.png"
    guardar_grafica(ruta)
    return ruta


def grafica_3_retos(top_retos, carpeta):
    """Grafica 3: barras horizontales con los 10 retos con mas participantes."""
    # Los ids son UUID largos: en el eje se muestran solo los primeros 8 caracteres
    top_corto = top_retos.copy()
    top_corto.index = top_corto.index.astype(str).str[:8]
    top_corto.plot(kind="barh", figsize=(8, 5))
    plt.gca().invert_yaxis()  # el reto con mas participantes queda arriba
    plt.title("Los 10 retos con más participantes")
    plt.xlabel("Número de participantes")
    plt.ylabel("Reto (primeros 8 caracteres del id)")
    ruta = carpeta / "registros_grafica_3.png"
    guardar_grafica(ruta)
    return ruta


def maximo_con_empates(serie):
    """Devuelve (nombre, valor, empates) del valor mas alto de una serie."""
    valor = serie.max()
    ganadores = serie[serie == valor]
    return ganadores.index[0], int(valor), len(ganadores) - 1


def texto_empates(empates):
    """Devuelve una frase corta cuando hay empate en el valor mas alto."""
    if empates == 0:
        return ""
    return f" (empata con {empates} más)"


def escribir_conclusiones(df, conteo, por_mes):
    """Arma la lista de conclusiones a partir de los datos."""
    total = len(df)
    estado, n_estado, _ = maximo_con_empates(conteo)
    reto, n_reto, emp_reto = maximo_con_empates(df.groupby("id_reto")["id"].count())
    mes, n_mes, emp_mes = maximo_con_empates(por_mes)

    # Inscripciones duplicadas: mismo usuario en el mismo reto
    pares = ["id_usuario", "id_reto"]
    filas_repetidas = int(df.duplicated(subset=pares, keep=False).sum())
    sobrantes = int(df.duplicated(subset=pares, keep="first").sum())
    n_pares = int(df[df.duplicated(subset=pares, keep=False)].groupby(pares).ngroups)

    conclusiones = [
        f"El estado más frecuente es {estado} con {n_estado} de {total} participaciones "
        f"({100 * n_estado / total:.1f}%).",
        f"El reto más popular es {reto} con {n_reto} participantes{texto_empates(emp_reto)}.",
        f"El mes con más inscripciones fue {mes} con {n_mes}{texto_empates(emp_mes)}.",
    ]
    if sobrantes == 0:
        conclusiones.append("No se encontraron inscripciones duplicadas (mismo usuario en el mismo reto).")
    else:
        conclusiones.append(
            f"Se encontraron {sobrantes} inscripciones duplicadas "
            f"({filas_repetidas} filas en {n_pares} pares usuario + reto)."
        )
    conclusiones.append(
        "El back debe bloquear las inscripciones duplicadas con 409 (Conflict): un usuario "
        "no puede inscribirse dos veces en el mismo reto, y si pasan se cuentan participantes "
        "de más y se alteran las estadísticas."
    )
    return conclusiones


def main(argv):
    """Punto de entrada: lee el CSV limpio, crea las graficas e imprime rutas y conclusiones."""
    if len(argv) != 2:
        print("Uso: python scripts/reporte_registros.py registros_limpio.csv", file=sys.stderr)
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
    if df.empty:
        print("El archivo no tiene filas: no hay nada que graficar.", file=sys.stderr)
        return 1

    carpeta = carpeta_reportes(ruta)
    os.makedirs(carpeta, exist_ok=True)

    conteo, por_mes, top_retos = calcular_consultas(df)
    rutas = [
        grafica_1_estados(conteo, carpeta),
        grafica_2_meses(por_mes, carpeta),
        grafica_3_retos(top_retos, carpeta),
    ]
    for numero, ruta_png in enumerate(rutas, start=1):
        print(f"Gráfica {numero} guardada en: {ruta_png}")

    print("\nConclusiones:")
    for numero, texto in enumerate(escribir_conclusiones(df, conteo, por_mes), start=1):
        print(f"{numero}. {texto}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))