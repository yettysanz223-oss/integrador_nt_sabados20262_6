import random
import uuid

import pandas as pd
from faker import Faker

# 1. Pais e idioma de la simulacion
fake = Faker("es_CO")

# 2. Semillas fijas para que el resultado sea siempre el mismo
Faker.seed(42)
random.seed(42)

# 3. Constantes: catalogo real (solo 10 categorias) y areas responsables
CATEGORIAS = [
    "Logistica",
    "Tecnologia",
    "Marketing",
    "Finanzas",
    "Recursos Humanos",
    "Ventas",
    "Produccion",
    "Calidad",
    "Soporte",
    "Investigacion",
]

# Se usa solo en este ejercicio de analisis, para poder agrupar.
AREAS = ["Operaciones", "Comercial", "Administrativa", "Tecnica", "Directiva"]

# Porcentajes de suciedad
PCT_DESCRIPCION_NULA = 0.15
PCT_AREA_NULA = 0.10
PCT_DUPLICADOS = 0.08


def _ensuciar_nombre(nombre):
    """Devuelve una variante de escritura del mismo nombre."""
    variantes = [
        nombre,                  # 'Logistica'
        nombre.upper(),          # 'LOGISTICA'
        nombre.lower(),          # 'logistica'
        f" {nombre.lower()} ",   # ' logistica '
        f"  {nombre}",           # espacios al inicio
        f"{nombre}  ",           # espacios al final
        nombre.replace("i", "í", 1).lower(),  # 'logística' (con tilde)
    ]
    return random.choice(variantes)


def generar_categorias(n=250):
    """Genera n filas sucias de la tabla categorias y devuelve un DataFrame."""
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": random.choice(CATEGORIAS),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS),
        })
    df = pd.DataFrame(filas)

    # --- Ensuciar a proposito ---
    # nombre: variantes del mismo nombre (mayusculas, espacios, tildes)
    df["nombre"] = df["nombre"].apply(_ensuciar_nombre)

    # descripcion: 15% None
    idx = df.sample(frac=PCT_DESCRIPCION_NULA, random_state=42).index
    df.loc[idx, "descripcion"] = None

    # area_responsable: 10% None
    idx = df.sample(frac=PCT_AREA_NULA, random_state=43).index
    df.loc[idx, "area_responsable"] = None

    # 8% de filas repetidas tal cual (duplicados exactos).
    # Se reemplazan filas por copias de otras, para mantener n filas en total.
    n_dup = int(n * PCT_DUPLICADOS)
    destino = df.sample(n=n_dup, random_state=44).index
    origen = df.drop(destino).sample(n=n_dup, random_state=45).index
    for d, o in zip(destino, origen):
        df.loc[d] = df.loc[o].values

    return df


if __name__ == "__main__":
    df = generar_categorias()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())