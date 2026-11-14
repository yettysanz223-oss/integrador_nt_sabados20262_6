import random
import uuid

import pandas as pd
from faker import Faker

# 1. Sembrar semillas para que el resultado sea reproducible
random.seed(42)
Faker.seed(42)

# 2. Identificar los datos a simular con su tipo de dato (mismas columnas de Backend II)
# id        texto (UUID)
# nombre    texto
# nit       texto
# sector    texto (acotado a SECTORES)
# contacto  texto
# correo    texto
# telefono  texto
# activa    booleano

# 3. Constantes
SECTORES = ["Logistica", "Tecnologia", "Salud", "Educacion", "Comercio", "Construccion"]

FILAS = 300
COLUMNAS = ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"]

fake = Faker("es_CO")


# 4. Funciones auxiliares
def obtener_muestra(datos, porcentaje, total=None):
    """Devuelve los índices de un porcentaje de filas (de `total` filas, por defecto len(datos))."""
    cantidad = round((total or len(datos)) * porcentaje)
    return datos.sample(n=cantidad, random_state=random.randint(0, 9999)).index


def generar_filas_limpias(n):
    """Genera n filas limpias de empresas."""
    filas = []
    for _ in range(n):
        filas.append(
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
        )
    return filas


def nit_con_puntos(nit):
    """900123456-7 -> 900.123.456-7"""
    digitos = nit.replace("-", "")
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9]}"


def nit_sin_nada(nit):
    """900123456-7 -> 9001234567"""
    return nit.replace("-", "")


def telefono_sucio(telefono, formato):
    """Devuelve el teléfono en uno de tres formatos: 0 pegado, 1 con espacios, 2 con +57 y guiones."""
    if formato == 0:
        return telefono
    if formato == 1:
        return f"{telefono[:3]} {telefono[3:6]} {telefono[6:]}"
    return f"+57 {telefono[:3]}-{telefono[3:6]}-{telefono[6:]}"


def activa_a_texto(valor):
    """True -> 'SI' o '1'; False -> 'No' o '0'."""
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])


def sector_sucio(sector):
    """Variante sucia del sector: 'Logistica', 'LOGISTICA' o ' logistica '."""
    return random.choice([sector, sector.upper(), f" {sector.lower()} "])


# 5. Función principal: genera, ensucia y devuelve el DataFrame
def generar_empresas(n=300):
    # Se re-siembra para que cada llamada dé el mismo resultado,
    # incluso si el script de exportación la importa.
    random.seed(42)
    Faker.seed(42)

    df = pd.DataFrame(generar_filas_limpias(n), columns=COLUMNAS)

    # nombre: 10% con espacios sobrantes y 15% en MAYUSCULAS
    filas_elegidas = obtener_muestra(df, 0.10)
    df.loc[filas_elegidas, "nombre"] = " " + df.loc[filas_elegidas, "nombre"] + " "
    filas_elegidas = obtener_muestra(df, 0.15)
    df.loc[filas_elegidas, "nombre"] = df.loc[filas_elegidas, "nombre"].str.upper()

    # nit: la mitad con puntos y guiones (900.123.456-7), la otra mitad sin nada (9001234567)
    mitad = obtener_muestra(df, 0.50)
    df["nit"] = df["nit"].map(nit_sin_nada)
    df.loc[mitad, "nit"] = df.loc[mitad, "nit"].map(nit_con_puntos)

    # sector: variantes del mismo sector
    filas_elegidas = obtener_muestra(df, 0.30)
    df.loc[filas_elegidas, "sector"] = df.loc[filas_elegidas, "sector"].map(sector_sucio)

    # contacto: 8% en None
    df["contacto"] = df["contacto"].astype(object)
    filas_elegidas = obtener_muestra(df, 0.08)
    df.loc[filas_elegidas, "contacto"] = None

    # correo: 6% sin la arroba (correo inválido)
    filas_elegidas = obtener_muestra(df, 0.06)
    df.loc[filas_elegidas, "correo"] = df.loc[filas_elegidas, "correo"].str.replace("@", "", regex=False)

    # telefono: tres formatos mezclados
    formatos = pd.Series([random.randint(0, 2) for _ in range(len(df))], index=df.index)
    df["telefono"] = [telefono_sucio(t, f) for t, f in zip(df["telefono"], formatos)]

    # activa: a veces llega como texto 'SI', 'No', '1', '0'
    df["activa"] = df["activa"].astype(object)
    filas_elegidas = obtener_muestra(df, 0.20)
    df.loc[filas_elegidas, "activa"] = df.loc[filas_elegidas, "activa"].map(activa_a_texto)

    # Se eligen las filas de NIT repetidos (3%) y de duplicados exactos (5%) sin solaparse;
    # el resto son las filas "originales" de las que se copia.
    idx_nit = obtener_muestra(df, 0.03)
    resto = df.drop(index=idx_nit)
    idx_dup = obtener_muestra(resto, 0.05, total=len(df))
    originales = resto.drop(index=idx_dup).index.tolist()

    # 3%: el mismo NIT en empresas distintas (el NIT debería ser único)
    origen = random.choices(originales, k=len(idx_nit))
    df.loc[idx_nit, "nit"] = df.loc[origen, "nit"].to_numpy()

    # 5%: filas repetidas tal cual (incluido el id)
    origen = random.choices(originales, k=len(idx_dup))
    df.loc[idx_dup, :] = df.loc[origen, :].to_numpy()

    return df


# 6. Revisar que los datos quedaron sucios
if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
