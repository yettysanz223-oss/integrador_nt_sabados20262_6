"""Reporte grafico de la tabla retos (HU G01 de Kaizen).

Uso (desde la raiz del proyecto):
    python src/reporte_retos.py retos_limpio.csv
    python src/reporte_retos.py data/limpio/retos_limpio.csv

Lee el CSV limpio, crea tres graficas con matplotlib, las guarda en reportes/
(retos_grafica_1.png, retos_grafica_2.png y retos_grafica_3.png) e imprime la
ruta de cada una junto con las conclusiones.
"""
import os
import sys

import matplotlib

# Backend sin ventana: el script solo guarda las imagenes y nunca se queda esperando.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

CARPETA_SALIDA = "reportes"
RUTA_POR_DEFECTO = os.path.join("data", "limpio", "retos_limpio.csv")
RUTA_GRAFICA_1 = os.path.join(CARPETA_SALIDA, "retos_grafica_1.png")
RUTA_GRAFICA_2 = os.path.join(CARPETA_SALIDA, "retos_grafica_2.png")
RUTA_GRAFICA_3 = os.path.join(CARPETA_SALIDA, "retos_grafica_3.png")

COLUMNAS_NECESARIAS = ["fecha_inicio", "fecha_fin", "estado"]

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre",
    11: "noviembre", 12: "diciembre",
}


def leer_datos(ruta):
    """Lee el CSV limpio con pandas y avisa con un mensaje claro si falta el archivo."""
    if not os.path.exists(ruta):
        sys.exit(
            f"Error: no existe el archivo '{ruta}'. "
            "Uso: python src/reporte_retos.py retos_limpio.csv"
        )
    return pd.read_csv(ruta)


def preparar_datos(df):
    """Convierte las fechas a datetime y garantiza que exista la columna duracion_dias.

    Si el CSV ya trae duracion_dias (lo normal despues de la HU L01) se respeta;
    si no, se calcula como fecha_fin - fecha_inicio en dias.
    """
    faltantes = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al CSV le faltan las columnas {faltantes}.")

    df = df.copy()
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")
    if "duracion_dias" not in df.columns:
        df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    return df


def contar_por_estado(df):
    """Devuelve la cantidad de retos por estado, ordenada por nombre de estado."""
    return df["estado"].value_counts().sort_index()


def contar_por_mes(df):
    """Devuelve cuantos retos empiezan en cada mes (AAAA-MM), incluidos los meses en 0."""
    periodos = df["fecha_inicio"].dropna().dt.to_period("M")
    conteo = periodos.value_counts().sort_index()
    rango = pd.period_range(conteo.index.min(), conteo.index.max(), freq="M")
    conteo = conteo.reindex(rango, fill_value=0)
    conteo.index = conteo.index.astype(str)  # texto para que el eje X se lea bien
    return conteo


def retos_con_duracion_valida(df):
    """Filtra los retos con duracion real (descarta nulos y fin antes que inicio)."""
    return df[df["duracion_dias"] >= 0]


def grafica_estados(df):
    """Grafica 1 (barras): cantidad de retos por estado. Devuelve la ruta guardada."""
    conteo = contar_por_estado(df)

    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar")
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado del reto")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_1, dpi=120)
    plt.close()
    return RUTA_GRAFICA_1


def grafica_por_mes(df):
    """Grafica 2 (linea): retos que empiezan cada mes. Devuelve la ruta guardada."""
    por_mes = contar_por_mes(df)

    plt.figure(figsize=(10, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio (AAAA-MM)")
    plt.ylabel("Cantidad de retos")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_2, dpi=120)
    plt.close()
    return RUTA_GRAFICA_2


def grafica_duracion(df):
    """Grafica 3 (histograma): como se reparte la duracion de los retos."""
    duraciones = retos_con_duracion_valida(df)["duracion_dias"]

    plt.figure(figsize=(8, 5))
    duraciones.plot(kind="hist", bins=20, edgecolor="black")
    plt.title("Distribucion de la duracion de los retos")
    plt.xlabel("Duracion (dias)")
    plt.ylabel("Cantidad de retos")
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_3, dpi=120)
    plt.close()
    return RUTA_GRAFICA_3


def imprimir_conclusiones(df):
    """Imprime lo aprendido: mes con mas retos, duracion por estado y fechas incoherentes."""
    por_mes = contar_por_mes(df)
    mes_top = por_mes.idxmax()
    anio, mes = mes_top.split("-")
    nombre_mes = MESES[int(mes)]
    validos = retos_con_duracion_valida(df)
    promedio_estado = validos.groupby("estado")["duracion_dias"].mean().round(1)
    incoherentes = int((df["duracion_dias"] < 0).sum())
    sin_fin = int(df["fecha_fin"].isna().sum())

    print("\n===== CONCLUSIONES =====")
    print(
        f"1. Mes con mas retos: {nombre_mes} de {anio} ({int(por_mes.max())} retos de {len(df)}). "
        "Puede deberse a que en datos simulados las fechas salen al azar dentro de un rango "
        "de aproximadamente 15 meses (el primero y el ultimo mes quedan incompletos y por eso tienen menos); "
        "con datos reales podria deberse a la temporada: inicio de ano, ciclos academicos "
        "o presupuestos de las empresas."
    )
    print("2. Duracion promedio por estado (solo retos con fechas validas):")
    for est, valor in promedio_estado.items():
        print(f"   - {est}: {valor} dias")
    print(
        f"   Duracion minima y maxima observadas: {int(validos['duracion_dias'].min())} "
        f"y {int(validos['duracion_dias'].max())} dias."
    )
    print(
        f"3. Retos con la fecha de fin ANTES que la de inicio: {incoherentes} "
        "(dato para el back: validar que fecha_fin >= fecha_inicio al registrar un reto)."
    )
    print(f"   Retos sin fecha_fin: {sin_fin} (no se puede calcular su duracion).")


def main():
    """Lee el CSV limpio, crea las tres graficas e imprime las conclusiones."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    df = preparar_datos(leer_datos(ruta))
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    print(f"Archivo leido: {ruta} ({len(df)} filas)")
    for ruta_img in (grafica_estados(df), grafica_por_mes(df), grafica_duracion(df)):
        print(f"Grafica guardada en: {ruta_img}")

    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()
