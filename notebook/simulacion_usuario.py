import random
import uuid
import pandas as pd
from faker import Faker

#1. Sembrar Semillas para los datos a simular 

random.seed(42)
Faker.seed(42)

#2. Identificar los datos a simular con su tipo de dato 
#id (texto (UUID)), 
# nombre (texto), 
#descripcion (texto), acotar
# fecha_inicio (fecha), 
#fecha_fin (fecha), 
# estado (texto), acotar 
#id_empresa (texto (UUID)), 
#id_categoria (texto (UUID)), acotar
#id_prioridad (texto (UUID)). acotar 

#3 Establecer una constante para el numero de simulaciones

filas_a_simular = 500
faker = Faker("es_CO")

#4. funcion para generar datos falsos de la tabla retos
def generar_retos_falsos(numero_filas=500):
    usuarios = []
    for _ in range(numero_filas):
        usuarios.append(
            {
                "id": str(uuid.uuid4()),
                "nombre": faker.name(),
                "descripcion": faker.text(),
                "fecha_inicio": faker.date_this_decade(),
                "fecha_fin": faker.date_this_decade(),
                "estado": random.choice(["activo", "inactivo", "pendiente"]),
                "id_empresa": str(uuid.uuid4()),
                "id_categoria": str(uuid.uuid4()),
                "id_prioridad": str(uuid.uuid4())
            }
        )
    return usuarios

#5 Convertir la lista de diccionarios a un DataFrame de pandas
tabla_ordenada_retos = pd.DataFrame(generar_retos_falsos())

#6. Probar la funcion generadora de datos falsos
print (tabla_ordenada_retos)

#7. preparar la simulacion para ensuciar mis datos

#7.1 Funcion para obtener una muestra de los datos 

def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index

#7.2 Funcion auxiliar para cambiar valores de un texto 
def escribir_mal(texto):
    variantes = [texto.title(),texto.lower() ,texto.upper(),texto.capitalize(), f" {texto} ", "Andres"]
    return random.choice(variantes)

#7.3 Funcion Auxiliar para cambiar los booleanos
def convertir_booleano(valor):
    if valor:
        return random.choice(["SI", "1"])
    else:
        return random.choice(["NO", "0"])

#7.4 Funcion Principal para ensuciar los datos  smilados 
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # Nombre: el 10% tenga espacios y 8% tenga mayusculas
    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = "" + datos_df.loc[filas_elegidas, "nombre"] + " "

    filas_elegidas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].str.upper()

    # correo: el 5% tenga espacios este sin arroba
    filas_elegidas = obtener_muestra(datos_df, 0.05)
    datos_df.loc[filas_elegidas, "correo"] = datos_df.loc[filas_elegidas, "correo"].str.replace("@", "")

    #correo: el 4% de os correos no deberia tener ningun valor (None)
    filas_elegidas = obtener_muestra(datos_df, 0.04)
    datos_df.loc[filas_elegidas, "correo"] = None

    #rol: Aplicar errores de escritura (variantes)

    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "rol"] = datos_df.loc[filas_elegidas, "rol"].map(escribir_mal)

    #Activo: en ocasiones llega SI, NO, 1, 0
    datos_df["activo"] = datos_df["activo"].astype(object)
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "activo"] = datos_df.loc[filas_elegidas, "activo"].map(convertir_booleano)

    #Mezclar el formato de fecha 
    #ISO=> YYYY-MM-DD HH:MM:SS
    #LATINO=> DD/MM/YYYY HH:MM:SS
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M:%S")
    datos_df["fecha_registro"] = iso 
    filas_elegidas = obtener_muestra(datos_df, 0.25)
    datos_df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]