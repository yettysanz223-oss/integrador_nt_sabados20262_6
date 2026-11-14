import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

# 1. Semillas fijas para que los datos sean reproducibles
random.seed(42)
Faker.seed(42)
fake = Faker("es_CO")

# 2. Constantes: catalogos fijos (las llaves foraneas salen de aqui,
#    asi varios retos comparten empresa/categoria/prioridad)
def _uuids_fijos(prefijo, cantidad):
    # uuid5 es deterministico: los mismos IDs en cada ejecucion
    return [str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{prefijo}-{i}")) for i in range(cantidad)]

ESTADOS = ["en_curso", "cerrado", "pendiente"]
IDS_EMPRESA = _uuids_fijos("empresa", 8)
IDS_CATEGORIA = _uuids_fijos("categoria", 5)
IDS_PRIORIDAD = _uuids_fijos("prioridad", 3)

# Variantes sucias de estado
VARIANTES_ESTADO = {
    "en_curso": ["en_curso", "EN CURSO", " en_curso "],
    "cerrado": [" Cerrado ", "CERRADO", "cerrado "],
    "pendiente": [" Pendiente ", "PENDIENTE", "pendiente "],
}


# 3. Generar datos limpios
def _generar_limpios(n):
    filas = []
    for _ in range(n):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append(
            {
                "id": str(uuid.uuid4()),
                "nombre": fake.sentence(nb_words=6).rstrip("."),
                "descripcion": fake.sentence(nb_words=12),
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
                "estado": random.choice(ESTADOS),
                "id_empresa": random.choice(IDS_EMPRESA),
                "id_categoria": random.choice(IDS_CATEGORIA),
                "id_prioridad": random.choice(IDS_PRIORIDAD),
            }
        )
    return pd.DataFrame(filas)


# 4. Utilidades para ensuciar
def _muestra(df, porcentaje):
    return df.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index


def _ensuciar_estado(valor):
    return random.choice(VARIANTES_ESTADO[valor])


# 5. Ensuciar los datos
def _ensuciar(df):
    df = df.copy()

    # nombre: 10% con espacios sobrantes
    idx = _muestra(df, 0.10)
    df.loc[idx, "nombre"] = "  " + df.loc[idx, "nombre"] + "  "

    # descripcion: 12% nulos
    idx = _muestra(df, 0.12)
    df.loc[idx, "descripcion"] = None

    # fecha_fin: 5% anterior a fecha_inicio (error logico)
    df["fecha_fin"] = df["fecha_fin"].astype(object)
    idx = _muestra(df, 0.05)
    df.loc[idx, "fecha_fin"] = df.loc[idx, "fecha_inicio"].map(
        lambda f: f - timedelta(days=random.randint(1, 30))
    )

    # fecha_fin: 8% nulos
    idx = _muestra(df, 0.08)
    df.loc[idx, "fecha_fin"] = None

    # fecha_inicio: formatos mezclados (ISO y latino)
    iso = df["fecha_inicio"].map(lambda f: f.strftime("%Y-%m-%d"))
    latino = df["fecha_inicio"].map(lambda f: f.strftime("%d/%m/%Y"))
    df["fecha_inicio"] = iso
    idx = _muestra(df, 0.40)
    df.loc[idx, "fecha_inicio"] = latino.loc[idx]

    # estado: variantes de escritura (30% de las filas)
    idx = _muestra(df, 0.30)
    df.loc[idx, "estado"] = df.loc[idx, "estado"].map(_ensuciar_estado)

    # 5% de filas duplicadas exactas
    duplicados = df.sample(frac=0.05, random_state=random.randint(0, 9999))
    df = pd.concat([df, duplicados], ignore_index=True)

    return df


# 6. Funcion principal, importable desde el script de exportacion
def generar_retos(n=500):
    df = _generar_limpios(n)
    df = _ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    