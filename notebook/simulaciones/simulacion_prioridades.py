import random
import uuid
import pandas as pd
from faker import Faker

# 1. Sembrar semillas para los datos a simular
random.seed(42)
Faker.seed(42)

# 2. Identificar los datos a simular con su tipo de dato
# id (texto UUID)
# nombre (texto), acotar: Baja, Media, Alta, Urgente, Critica
# nivel (entero), acotar: depende del nombre (NIVELES)
# dias_max_respuesta (entero), acotar: depende del nivel (DIAS)

# 3. Establecer constantes
filas_a_simular = 200
faker = Faker("es_CO")

# NIVELES (nombre -> nivel) y DIAS (nivel -> dias_max_respuesta)
NIVELES = {
    "Baja": 1,
    "Media": 2,
    "Alta": 3,
    "Urgente": 4,
    "Critica": 5,
}

DIAS = {
    1: 15,
    2: 10,
    3: 5,
    4: 2,
    5: 1,
}

# Apoyo para escribir el nivel con palabra al ensuciar
PALABRAS_NIVEL = {1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco"}


# 4. Función para generar los datos de la tabla prioridades
def generar_prioridades(n=200):
    prioridades = []
    for _ in range(n):
        nombre = random.choice(list(NIVELES.keys()))
        nivel = NIVELES[nombre]
        dias_max_respuesta = DIAS[nivel]
        prioridades.append(
            {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "nivel": nivel,
                "dias_max_respuesta": dias_max_respuesta,
            }
        )

    # 5. Convertir la lista de diccionarios a un DataFrame de pandas
    tabla_ordenada_prioridades = pd.DataFrame(prioridades)

    # 6. Ensuciar los datos simulados y devolver el DataFrame
    return ensuciar(tabla_ordenada_prioridades)


# 7. Preparar la simulación para ensuciar mis datos

# 7.1 Función para obtener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index


# 7.2 Función auxiliar para cambiar valores de un texto
def escribir_mal(texto):
    variantes = [texto.upper(), f" {texto.lower()} ", texto.capitalize()]
    return random.choice(variantes)


# 7.3 Función auxiliar para cambiar los booleanos (plantilla del profesor)
# En prioridades no hay columna booleana, por eso no se llama.
def convertir_booleano(valor):
    if valor:
        return random.choice(["SI", "1"])
    else:
        return random.choice(["NO", "0"])


# 7.4 Función auxiliar para escribir el nivel con palabra
def nivel_a_palabra(valor):
    return PALABRAS_NIVEL[int(valor)]


# 7.5 Función principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # nombre: el 30% con variantes ('ALTA', ' alta ', 'Alta')
    filas_elegidas = obtener_muestra(datos_df, 0.30)
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].map(escribir_mal)

    # nivel: a veces TEXTO ('3'), a veces la palabra ('tres') y 7% en None
    datos_df["nivel"] = datos_df["nivel"].astype(object)

    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "nivel"] = datos_df.loc[filas_elegidas, "nivel"].map(str)

    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "nivel"] = datos_df.loc[filas_elegidas, "nivel"].map(nivel_a_palabra)

    filas_elegidas = obtener_muestra(datos_df, 0.07)
    datos_df.loc[filas_elegidas, "nivel"] = None

    # dias_max_respuesta: 5% en None y 3% con un valor absurdo (999)
    datos_df["dias_max_respuesta"] = datos_df["dias_max_respuesta"].astype("Int64")

    filas_none = obtener_muestra(datos_df, 0.05)
    datos_df.loc[filas_none, "dias_max_respuesta"] = None

    restantes = datos_df.drop(index=filas_none)
    filas_absurdas = obtener_muestra(restantes, 0.03)
    datos_df.loc[filas_absurdas, "dias_max_respuesta"] = 999

    # duplicados exactos: 8% de filas repetidas (siempre al final)
    duplicados = datos_df.sample(frac=0.08, random_state=random.randint(0, 9999))
    datos_df = pd.concat([datos_df, duplicados], ignore_index=True)

    return datos_df


# 8. Probar la función y revisar que los datos quedaron sucios
if __name__ == "__main__":
    df = generar_prioridades(filas_a_simular)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())