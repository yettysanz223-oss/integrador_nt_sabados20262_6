"""
Organizacion que registra o propone retos. Crea el script `src/simular_empresas.py`.
Con la libreria Faker genera 300 filas falsas de la tabla `empresas`, con las MISMAS
columnas que usa Backend II. Despues ensucia los datos a proposito: nulos, duplicados,
espacios sobrantes, mayusculas mezcladas y formatos distintos. Esos errores son los
que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

Usa Faker("es_CO") y fija la semilla con Faker.seed(42) y random.seed(42) para que
el resultado sea SIEMPRE el mismo y tu companero pueda reproducirlo.
"""

import random
import uuid
from faker import Faker