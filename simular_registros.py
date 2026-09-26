import random 
import uuid
from faker import Faker
#id (texto (UUID)), 
# fecha_registro (fecha y hora), 
# observacion (texto), estado (texto), 
# id_usuario (texto (UUID)), 
# id_reto (texto (UUID)).
random.seed(42)
Faker.seed(42)

FILAS=800
Fake=Faker("es_CO")
ESTADOS={"CREADO","ELIMINADO","ACTUALIZADO",}
IDS_USUARIO=[10243, 85910, "usr_492", "usr_715", 20485]
IDS_RETO=["4a1f8c6b-9d2e-4b7c-a1f3-8e5d2c6b4a1f",
    "7b3e9d1c-8f4a-4e2b-b3c5-9d8e7f6a5b4c",
    "c9a8b7c6-d5e4-4f3b-a2c1-0d9e8f7a6b5c",
    "1f2e3d4c-5b6a-4f7e-8d9c-0b1a2f3e4d5c",
    "a5b6c7d8-e9f0-4a1b-bc2d-3e4f5a6b7c8d"]
def generar_datos(numero_filas=800):
    usuarios = []
    for _ in range(numero_filas):
        usuarios.append({
            "id": str(uuid.uuid4()),
            "nombre": Fake.name(),
            "correo": Fake.email(),
            "contrasena_hash": Fake.sha256(),
            "fecha_registro": Fake.date_time_between(
                start_date="-1y", end_date="now"
            ),
        })
    return usuarios
    


