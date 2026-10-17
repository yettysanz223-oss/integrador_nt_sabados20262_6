import random
import uuid
from faker import Faker

# sembrar semillas para los datos a simular
random.seed(42)
Faker.seed(42)

#2 identificar los datos a simular con su tipo de dato
'''Se generan 800 filas con estas columnas: 
id (texto (UUID)),
fecha_registro (fecha y hora),
observacion (texto),
estado (texto) inscrito-acotado, 
id_usuario (texto (UUID)),
id_reto (texto (UUID)).'''

# establecer una cosntante para el numeo de simulaicones.
FILAS=800


#Funcion generadora

def generar_datos(numero_filas):
    pass
