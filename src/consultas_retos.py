"""Consultas sobre la tabla retos (HU Q01 de Kaizen).

Uso:
    python src/consultas_retos.py retos_limpio.csv
    python src/consultas_retos.py data/limpio/retos_limpio.csv

Lee el CSV LIMPIO (no el sucio), resuelve las cinco consultas de la HU con
pandas, imprime el titulo y el resultado de cada una en orden y guarda
retos_consulta_N.csv en la misma carpeta del archivo de entrada
(con data/limpio/retos_limpio.csv quedan en data/limpio/).
"""
import os
import sys

import pandas as pd

RUTA_POR_DEFECTO = os.path.join("data", "limpio", "retos_limpio.csv")


def leer_retos(ruta):
    """Lee retos_limpio.csv con las fechas como datetime y valida lo necesario."""
    if not os.path.exists(ruta):
        sys.exit(
            f"Error: no existe el archivo '{ruta}'. "
            "Ejecuta primero 'python src/limpiar_retos.py' desde la raiz del proyecto."
        )
    df = pd.read_csv(ruta, parse_dates=["fecha_inicio", "fecha_fin"])
    obligatorias = ["id", "nombre", "fecha_inicio", "estado", "duracion_dias", "fecha_valida"]
    faltan = [c for c in obligatorias if c not in df.columns]
    if faltan:
        sys.exit(
            f"Error: faltan las columnas {faltan}. "
            "Verifica que sea el archivo LIMPIO (retos_limpio.csv), no el sucio."
        )
    return df


def guardar_resultado(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como retos_consulta_N.csv en la carpeta dada."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"retos_consulta_{numero}.csv")
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    print(f"-> guardado en {ruta}\n")


def consulta_1_en_curso(df, carpeta):
    """Consulta 1: que retos estan en curso (filtro por estado EN_CURSO)."""
    print("=== Consulta 1: Que retos estan en curso? ===")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(f"Total de retos en curso: {len(en_curso)}")
    print(en_curso.to_string())
    guardar_resultado(en_curso, carpeta, 1)
    return en_curso


def consulta_2_mas_largos(df, carpeta):
    """Consulta 2: los 10 retos con mayor duracion_dias (nombre, duracion y estado)."""
    print("=== Consulta 2: Cuales son los 10 retos mas largos? ===")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos.to_string())
    guardar_resultado(largos, carpeta, 2)
    return largos


def consulta_3_conteo_por_estado(df, carpeta):
    """Consulta 3: cuantos retos hay por estado (value_counts)."""
    print("=== Consulta 3: Cuantos retos hay por estado? ===")
    conteo = df["estado"].value_counts()
    print(conteo.to_string())
    # value_counts devuelve una Serie con el estado como indice: se pasa a tabla para guardarla.
    tabla = conteo.rename_axis("estado").reset_index(name="cantidad")
    guardar_resultado(tabla, carpeta, 3)
    return conteo


def consulta_4_duracion_por_estado(df, carpeta):
    """Consulta 4 (GROUPBY): cantidad, promedio, minimo y maximo de duracion_dias por estado.

    Solo cuenta los retos con fechas validas (fecha_valida == True), igual que las
    conclusiones de reporte_retos.py. Asi no entran las duraciones negativas
    (fin antes que inicio) y las dos HU muestran los mismos promedios.
    """
    print("=== Consulta 4: Cual es la duracion promedio, minima y maxima por estado? ===")
    print("(solo retos con fechas validas: se excluyen fin antes que inicio y sin fecha_fin)")
    validos = df[df["fecha_valida"]]
    resumen = validos.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(2)
    print(resumen.to_string())
    guardar_resultado(resumen.reset_index(), carpeta, 4)
    return resumen


def consulta_5_retos_por_mes(df, carpeta):
    """Consulta 5 (GROUPBY): cuantos retos empiezan cada mes (segun fecha_inicio)."""
    print("=== Consulta 5: Cuantos retos empiezan cada mes? ===")
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    print(por_mes.to_string())
    # El indice es un Period: se pasa a texto (AAAA-MM) para que el CSV quede legible.
    tabla = por_mes.rename_axis("mes").reset_index(name="cantidad_retos")
    tabla["mes"] = tabla["mes"].astype(str)
    guardar_resultado(tabla, carpeta, 5)
    return por_mes


def main():
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    carpeta = os.path.dirname(os.path.abspath(ruta))

    df = leer_retos(ruta)
    print(f"Archivo leido: {ruta} ({len(df)} filas)\n")

    consulta_1_en_curso(df, carpeta)
    consulta_2_mas_largos(df, carpeta)
    consulta_3_conteo_por_estado(df, carpeta)
    consulta_4_duracion_por_estado(df, carpeta)
    consulta_5_retos_por_mes(df, carpeta)


if __name__ == "__main__":
    main()
