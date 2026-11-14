"""
reporte_prioridades.py - HU G01: tres gráficas y conclusiones de la tabla prioridades.

Ejecutar desde la raíz del repositorio:
    python notebook/graficas/reporte_prioridades.py

Qué hace:
    1. Lee data/limpio/prioridades_limpio.csv.
    2. Crea tres gráficas con matplotlib y las guarda en reportes/ (dpi=120).
    3. Imprime la ruta de cada gráfica y, al final, las conclusiones.

Librerías: pandas (lectura y resúmenes) y matplotlib (gráficas).
"""

import os

import matplotlib
matplotlib.use("Agg")  # Sin ventana: el script nunca se queda esperando un plt.show()
import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------- constantes
RUTA_LIMPIO = "data/limpio/prioridades_limpio.csv"
CARPETA_REPORTES = "reportes"
COLUMNAS = ["nombre", "nivel", "dias_max_respuesta"]
PRIORIDADES_ESPERADAS = 5
NIVEL_MIN, NIVEL_MAX = 1, 5

RUTA_G1 = os.path.join(CARPETA_REPORTES, "prioridades_grafica_1.png")
RUTA_G2 = os.path.join(CARPETA_REPORTES, "prioridades_grafica_2.png")
RUTA_G3 = os.path.join(CARPETA_REPORTES, "prioridades_grafica_3.png")

# Paleta categórica en orden fijo (cada prioridad conserva su color en las gráficas 2 y 3)
PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#6250d6", "#e34948"]
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_SUAVE = "#52514e"
REJILLA = "#e3e2de"


# ---------------------------------------------------------------- lectura
def leer_datos(ruta):
    """Lee el archivo limpio, comprueba las columnas y convierte nivel y días a número."""
    if ruta.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(ruta)
    else:
        df = pd.read_csv(ruta)

    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Al archivo le faltan las columnas: {', '.join(faltan)}")

    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")

    # Una fila sin nombre, nivel o días no se puede graficar: se avisa y se descarta
    antes = len(df)
    df = df.dropna(subset=COLUMNAS).copy()
    if len(df) < antes:
        print(f"Aviso: se descartaron {antes - len(df)} filas con valores vacíos o no numéricos.")
    df["nivel"] = df["nivel"].astype(int)
    return df


def calcular_resumenes(df):
    """Calcula por_nivel, resumen, conteo y los colores que usan las gráficas."""
    # Filas por nivel (gráfica 1)
    por_nivel = df["nivel"].value_counts().sort_index()

    # Las prioridades se ordenan por su nivel para que el orden y el color sean siempre los mismos
    orden = df.groupby("nombre")["nivel"].min().sort_values().index

    # Días de respuesta por prioridad (gráfica 2)
    resumen = (df.groupby("nombre")["dias_max_respuesta"]
               .agg(["mean", "min", "max", "count"])
               .reindex(orden))

    # Reparto de filas por prioridad (gráfica 3)
    conteo = df["nombre"].value_counts().reindex(orden)

    colores = [PALETA[i % len(PALETA)] for i in range(len(orden))]
    return por_nivel, resumen, conteo, colores


# ---------------------------------------------------------------- gráficas
def estilo_ejes(ax):
    """Deja los ejes discretos: sin bordes arriba/derecha y rejilla suave solo horizontal."""
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.yaxis.grid(True, color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=TEXTO_SUAVE)


def grafica_1_filas_por_nivel(por_nivel):
    """Gráfica 1 (barras): cuántas filas hay por nivel. Guarda y devuelve la ruta."""
    plt.figure(figsize=(7, 4.5), facecolor=SUPERFICIE)
    ax = por_nivel.plot(kind="bar", color=PALETA[0], width=0.6, rot=0)
    ax.bar_label(ax.containers[0], padding=3, color=TEXTO)
    estilo_ejes(ax)
    plt.title("Cantidad de filas por nivel de prioridad", color=TEXTO)
    plt.xlabel("Nivel", color=TEXTO_SUAVE)
    plt.ylabel("Cantidad de filas", color=TEXTO_SUAVE)
    plt.tight_layout()
    plt.savefig(RUTA_G1, dpi=120)
    plt.close()
    return RUTA_G1


def grafica_2_dias_promedio(resumen, colores):
    """Gráfica 2 (barras): días promedio de respuesta por prioridad. Guarda y devuelve la ruta."""
    plt.figure(figsize=(8, 4.5), facecolor=SUPERFICIE)
    ax = resumen["mean"].plot(kind="bar", color=colores, width=0.6, rot=15)
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3, color=TEXTO)
    estilo_ejes(ax)
    plt.title("Días promedio de respuesta por prioridad", color=TEXTO)
    plt.xlabel("Prioridad", color=TEXTO_SUAVE)
    plt.ylabel("Días promedio", color=TEXTO_SUAVE)
    plt.tight_layout()
    plt.savefig(RUTA_G2, dpi=120)
    plt.close()
    return RUTA_G2


def grafica_3_reparto(conteo, colores):
    """Gráfica 3 (torta): reparto de las prioridades. Guarda y devuelve la ruta."""
    plt.figure(figsize=(6, 6), facecolor=SUPERFICIE)
    ax = plt.subplot()
    ax.set_facecolor(SUPERFICIE)
    conteo.plot(kind="pie", autopct="%1.1f%%", colors=colores, startangle=90,
                wedgeprops={"edgecolor": SUPERFICIE, "linewidth": 1.5}, ax=ax)
    plt.title("Reparto porcentual de prioridades", color=TEXTO)
    plt.ylabel("")  # Quitar etiqueta lateral fea
    plt.tight_layout()
    plt.savefig(RUTA_G3, dpi=120)
    plt.close()
    return RUTA_G3


# ---------------------------------------------------------------- conclusiones
def imprimir_conclusiones(df, resumen):
    """Imprime las conclusiones basadas en los datos procesados."""
    n_reales = df["nombre"].nunique()
    print("\n" + "=" * 50)
    print(" CONCLUSIONES - HU G01: TABLA PRIORIDADES")
    print("=" * 50)
    print(f"1. Prioridades reales encontradas: {n_reales} (Se esperaban {PRIORIDADES_ESPERADAS}).")
    print("2. Relación entre nivel y días máximos de respuesta:")
    for nombre, row in resumen.iterrows():
        print(f"   - {nombre}: max {row['max']} días (media: {row['mean']:.1f} días)")
    print("   Conclusión: a mayor nivel (más urgente), menos días para responder.")
    print("3. Validación en el Back-End:")
    print(f"   Es indispensable validar que el nivel esté entre {NIVEL_MIN} y {NIVEL_MAX}")
    print("   para mantener la integridad referencial y asegurar que los cálculos")
    print("   de prioridades no rompan las reglas de negocio del sistema.")
    print("=" * 50)


# ---------------------------------------------------------------- main
def main():
    ruta_archivo = RUTA_LIMPIO
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    print(f"Leyendo datos desde: {ruta_archivo}")
    df = leer_datos(ruta_archivo)

    por_nivel, resumen, conteo, colores = calcular_resumenes(df)

    r1 = grafica_1_filas_por_nivel(por_nivel)
    r2 = grafica_2_dias_promedio(resumen, colores)
    r3 = grafica_3_reparto(conteo, colores)

    print(f"Gráfica 1 guardada en: {r1}")
    print(f"Gráfica 2 guardada en: {r2}")
    print(f"Gráfica 3 guardada en: {r3}")

    imprimir_conclusiones(df, resumen)


if __name__ == "__main__":
    main()