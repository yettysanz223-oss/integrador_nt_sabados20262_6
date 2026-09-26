import random
import uuid
import pandas as pd
from faker import Faker


#1. Sembrar semillas para los datos a simular 

random.seed(42)

Faker.seed(42)


#2. Identificar los datos a simular con su tipo de dato
# Se generan 250 filas con estas columnas: 
#id (texto (UUID)), 
#nombre (texto), ***acotar
#descripcion (texto),  
#area_responsable (texto). *****acotar



#3. Establecer una constante para el número e simulacions
FILAS = 250
ROLES=["administrador", "Estudiante", "emoresario", "profesor"]

falsito=Faker("es_CO")

#4. Funcion generadora

def generar_datos(numero_filas=250):
    usuarios=[]
    for _ in range(numero_filas):
        usuarios.append({
            "id": str(uuid.uuid4),
            "nombre": falsito.name(),
            "correo": falsito.email(),
            "contraseña_hash":falsito.sha250(),
            "rol": random.choose(ROLES),
            "fecha_registro": falsito.date_time_between(start_dat="-2y", end_date="now")

        })
        return usuarios

    #5 Convirtiendo los datos generados en un dataframe con PANDAS(Libreria)

    tabla_ordenada_usuario=pd .DataFrame(generar_datos())
    #6 probar la funcion

    print(tabla_ordenada_usuario)