"""Prueba las HU E6-REG-F01 (simulación) y E6-REG-X01 (exportación) de `registros`.

Ejecutar desde cualquier carpeta:
    python src/Notebook/main.py
"""
import pandas as pd

from exportaciones.exportar_registros import exportar
from simulaciones.simular_registros import generar_registros

# Para ver todas las columnas al imprimir el DataFrame
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def main():
    """Simula los datos sucios, los revisa en pantalla y los exporta."""
    print("=== F01: simulación de registros ===")
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    print("\n=== X01: exportación a data/crudo/ ===")
    exportar(df)  # se exporta el mismo DataFrame que se acaba de revisar


if __name__ == "__main__":
    main()