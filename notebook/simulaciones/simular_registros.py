import random
import uuid

import pandas as pd
from faker import Faker

# 1. Sembrar semillas para que el resultado sea reproducible
random.seed(42)
Faker.seed(42)

# 2. Identificar los datos a simular con su tipo de dato (mismas columnas de Backend II)
# id              texto (UUID)
# fecha_registro  fecha y hora
# observacion     texto
# estado          texto (acotado a ESTADOS)
# id_usuario      texto (UUID, acotado a IDS_USUARIO)
# id_reto         texto (UUID, acotado a IDS_RETO)

# 3. Constantes
ESTADOS = ["Inscrito", "En proceso", "Finalizado"]  # confirmar que coinciden con Backend II
IDS_USUARIO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(50)]
IDS_RETO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(40)]

FILAS = 800
COLUMNAS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"]

# Variantes sucias de estado: valor limpio -> valor sucio
ESTADO_SUCIO = {
    "Inscrito": "inscrito",
    "En proceso": "EN PROCESO",
    "Finalizado": " Finalizado ",
}

fake = Faker("es_CO")


# 4. Funciones auxiliares para ensuciar
def obtener_muestra(datos, porcentaje, total=None):
    """Devuelve los índices de un porcentaje de filas (de `total` filas, por defecto len(datos))."""
    cantidad = round((total or len(datos)) * porcentaje)
    return datos.sample(n=cantidad, random_state=random.randint(0, 9999)).index


def generar_filas_limpias(n):
    """Genera n filas limpias; cada par (id_usuario, id_reto) es único."""
    if n > len(IDS_USUARIO) * len(IDS_RETO):
        raise ValueError("n supera el número de pares usuario-reto únicos disponibles")

    filas = []
    pares_usados = set()
    for _ in range(n):
        while True:
            id_usuario = random.choice(IDS_USUARIO)
            id_reto = random.choice(IDS_RETO)
            if (id_usuario, id_reto) not in pares_usados:
                break
        pares_usados.add((id_usuario, id_reto))

        filas.append(
            {
                "id": str(uuid.UUID(int=random.getrandbits(128), version=4)),
                "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
                "observacion": fake.sentence(nb_words=10),
                "estado": random.choice(ESTADOS),
                "id_usuario": id_usuario,
                "id_reto": id_reto,
            }
        )
    return filas


# 5. Función principal: genera, ensucia y devuelve el DataFrame
def generar_registros(n=800):
    # Se re-siembra para que cada llamada dé el mismo resultado,
    # incluso si el script de exportación la importa.
    random.seed(42)
    Faker.seed(42)

    df = pd.DataFrame(generar_filas_limpias(n), columns=COLUMNAS)

    # fecha_registro: dos formatos mezclados
    #   ISO    -> 2026-03-15 14:30:00
    #   LATINO -> 15/03/2026 14:30
    iso = df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    df["fecha_registro"] = iso
    filas_elegidas = obtener_muestra(df, 0.50)
    df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]

    # observacion: 20% nulos (None)
    df["observacion"] = df["observacion"].astype(object)
    filas_elegidas = obtener_muestra(df, 0.20)
    df.loc[filas_elegidas, "observacion"] = None

    # estado: variantes 'inscrito', 'EN PROCESO', ' Finalizado '
    filas_elegidas = obtener_muestra(df, 0.30)
    df.loc[filas_elegidas, "estado"] = df.loc[filas_elegidas, "estado"].map(ESTADO_SUCIO)

    # Se eligen las filas de pares repetidos (10%) y de duplicados exactos (5%) sin solaparse;
    # el resto son las filas "originales" de las que se copia.
    idx_par = obtener_muestra(df, 0.10)
    resto = df.drop(index=idx_par)
    idx_dup = obtener_muestra(resto, 0.05, total=len(df))
    originales = resto.drop(index=idx_dup).index.tolist()

    # 10%: el mismo usuario inscrito dos veces en el mismo reto (el back lo prohíbe con 409)
    origen = random.choices(originales, k=len(idx_par))
    df.loc[idx_par, "id_usuario"] = df.loc[origen, "id_usuario"].to_numpy()
    df.loc[idx_par, "id_reto"] = df.loc[origen, "id_reto"].to_numpy()

    # 5%: filas repetidas tal cual (incluido el id)
    origen = random.choices(originales, k=len(idx_dup))
    df.loc[idx_dup, :] = df.loc[origen, :].to_numpy()

    return df


# 6. Revisar que los datos quedaron sucios
if __name__ == "__main__":
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())