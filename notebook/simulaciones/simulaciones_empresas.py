import random
import re
import uuid

import pandas as pd
from faker import Faker

fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)

SECTORES = [
    "Tecnologia",
    "Logistica",
    "Salud",
    "Educacion",
    "Finanzas",
    "Comercio",
    "Manufactura",
    "Construccion",
    "Turismo",
    "Agricultura",
]


# ---------------------------------------------------------------------------
# Helpers de "simular" — cada uno se encarga de UNA sola columna.
# El orden en que se llaman abajo (en generar_empresas) no se puede cambiar:
# como todos usan random/Faker, cambiar el orden cambiaría el resultado
# aunque la semilla siga siendo 42.
# ---------------------------------------------------------------------------

def solo_digitos(texto):
    """Quita todo lo que no sea un numero (puntos, guiones, espacios)."""
    return re.sub(r"\D", "", texto)


def simular_nombre(df, n):
    """10% de los nombres con espacios sobrantes, 15% en MAYUSCULAS."""
    idx_espacios = random.sample(range(n), int(n * 0.10))
    for i in idx_espacios:
        df.loc[i, "nombre"] = f"  {df.loc[i, 'nombre']}  "

    idx_mayus = random.sample(range(n), int(n * 0.15))
    for i in idx_mayus:
        df.loc[i, "nombre"] = df.loc[i, "nombre"].upper()


def simular_nit(df, n):
    """Mitad de los NIT con formato 900.123.456-7, mitad solo numeros."""
    indices = list(range(n))
    random.shuffle(indices)
    mitad = n // 2
    con_formato, sin_formato = indices[:mitad], indices[mitad:]

    for i in con_formato:
        d = solo_digitos(df.loc[i, "nit"])
        df.loc[i, "nit"] = f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9]}"

    for i in sin_formato:
        df.loc[i, "nit"] = solo_digitos(df.loc[i, "nit"])


def simular_sector(df):
    """Las filas de sector 'Logistica' quedan con variantes de escritura."""
    variantes = ["Logistica", "LOGISTICA", " logistica "]
    filas_logistica = df[df["sector"] == "Logistica"].index
    for i in filas_logistica:
        df.loc[i, "sector"] = random.choice(variantes)


def poner_nulos(df, columna, n, porcentaje):
    """Deja en None un porcentaje de filas de la columna indicada."""
    indices = random.sample(range(n), int(n * porcentaje))
    df.loc[indices, columna] = None


def simular_correo(df, n, porcentaje=0.06):
    """Le quita la arroba a un porcentaje de correos (correo invalido)."""
    indices = random.sample(range(n), int(n * porcentaje))
    for i in indices:
        df.loc[i, "correo"] = df.loc[i, "correo"].replace("@", "")


def formatear_telefono(digitos, formato):
    """digitos trae 10 numeros seguidos (ej: 3001234567)."""
    if formato == "plano":
        return digitos
    if formato == "espacios":
        return f"{digitos[0:3]} {digitos[3:6]} {digitos[6:10]}"
    return f"+57 {digitos[0:3]}-{digitos[3:6]}-{digitos[6:10]}"


def simular_telefono(df, n):
    """Cada telefono queda en uno de tres formatos, elegido al azar."""
    formatos = ["plano", "espacios", "internacional"]
    for i in range(n):
        formato = random.choice(formatos)
        df.loc[i, "telefono"] = formatear_telefono(df.loc[i, "telefono"], formato)


def simular_activa(df, n, porcentaje=0.20):
    """Convierte la columna a texto en algunos casos: 'SI', 'No', '1', '0'."""
    df["activa"] = df["activa"].astype(object)  # para poder mezclar bool y str
    indices = random.sample(range(n), int(n * porcentaje))
    for i in indices:
        es_activa = df.loc[i, "activa"]
        df.loc[i, "activa"] = random.choice(["SI", "1"]) if es_activa else random.choice(["No", "0"])


def duplicar_filas(df, n, porcentaje=0.05):
    """Copia filas completas de un indice de origen a uno de destino."""
    cantidad = int(n * porcentaje)
    origenes = random.sample(range(n), cantidad)
    destinos = random.sample(range(n), cantidad)
    for origen, destino in zip(origenes, destinos):
        df.loc[destino] = df.loc[origen]


def duplicar_nits(df, n, porcentaje=0.03):
    """Copia solo el NIT entre dos empresas distintas (dato inconsistente)."""
    cantidad = int(n * porcentaje)
    origenes = random.sample(range(n), cantidad)
    destinos = random.sample(range(n), cantidad)
    for origen, destino in zip(origenes, destinos):
        df.loc[destino, "nit"] = df.loc[origen, "nit"]


def generar_datos_limpios(n):
    filas = [
        {
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        }
        for _ in range(n)
    ]
    return pd.DataFrame(filas)


def generar_empresas(n=300):
    df = generar_datos_limpios(n)

    simular_nombre(df, n)
    simular_nit(df, n)
    simular_sector(df)
    poner_nulos(df, "contacto", n, porcentaje=0.08)
    simular_correo(df, n)
    simular_telefono(df, n)
    simular_activa(df, n)
    duplicar_filas(df, n)
    duplicar_nits(df, n)

    return df


if __name__ == "__main__":
    df = generar_empresas(300)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())