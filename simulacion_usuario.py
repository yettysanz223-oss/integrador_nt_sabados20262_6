import random
import uuid
from faker import Faker


#1. Sembrar semillas para los datos a simular 
random.seed(42)
Faker.seed(42)

# 2. Identificar los datos a simular con su tipo de dato
# id — texto (UUID)
# nombre — texto
# nit — texto
# sector — texto **** averiguar para la otra semana debo estar pendiente con lo que deben estar acotado
# contacto — texto
# correo — texto
# telefono — texto
# activa — booleano


#3. Establecer una constante para el numero e simulaciones 
FILAS = 300
ROLES=[Administrador,]

#4. funcion generadora
def generar_datos(numeros_filas=400):
    'rol':random.choice(ROLES),
    fechas_registro=:FALSITO.date

