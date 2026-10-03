import random
import uuid
import pandas as pd
from faker import Faker

# 1. Sembrar semillas para reproducibilidad
random.seed(42)
Faker.seed(42)
fake = Faker("es_CO")

# 2. Constantes: NIVELES (nombre -> nivel) y DIAS (nivel -> dias_max_respuesta)
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


def generar_prioridades(n=200):
    filas = []

    for _ in range(n):
        nombre = random.choice(list(NIVELES.keys()))
        nivel = NIVELES[nombre]
        dias_max_respuesta = DIAS[nivel]

        fila = {
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "nivel": nivel,
            "dias_max_respuesta": dias_max_respuesta,
        }
        filas.append(fila)

    df = pd.DataFrame(filas)
    return df


#5. Convirtiendo los datos generados en un dataframe con pandas
tabla_ordenada_prioridades = generar_prioridades()

#6. Probar la funcion
print(tabla_ordenada_prioridades)

#7. preparar la simulacion para ensuciar mis datos

#7.1 Funcion para obtener una muestra de los datos 
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 99999)).index

#7.2 funcion  auxiliar para cambiar valores de un texto

def escribir_mal(texto):
    # Implementar lógica para ensuciar el texto
    variantes = [texto.lower(), texto.title(), texto.capitalize(), f"{texto}  ","Juan Jose"]    

    return random.choice(variantes)

#7.3funcion auxiliar para cambiar los booleanos
def convertir_booleano(valor):
    if valor:
        return random.choice(["SI", "1"])
    else:
        return random.choice(["NO", "0"])