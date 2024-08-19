import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from faker import Faker

# Conexión a MongoDB
client = MongoClient("mongodb+srv://martinjauma:1234@cluster0.whflcwt.mongodb.net/")
db = client["Presentes"]
jugadores_col = db["Jugadores"]
presentes_col = db["Presentes"]

fake = Faker('es_ES')

# Lista de posiciones de rugby
posiciones_rugby = [
    "Prop", "Hooker", "Lock", "Flanker", "Number 8", 
    "Scrum-half", "Fly-half", "Center", "Wing", "Full-back"
]

# Generar 50 jugadores con posiciones aleatorias
jugadores = [
    {
        "apellido": fake.last_name(), 
        "nombre": fake.first_name(),
        "posicion": random.choice(posiciones_rugby)  # Asignar una posición aleatoria
    }
    for _ in range(50)
]

# Insertar jugadores
jugadores_col.insert_many(jugadores)

# Generar fechas de martes y jueves desde 1 de marzo hasta 30 de julio de 2024
start_date = datetime(2024, 3, 1)
end_date = datetime(2024, 7, 30)
fechas = []

current_date = start_date
while current_date <= end_date:
    if current_date.weekday() in [1, 3]:  # 1 es martes, 3 es jueves
        fechas.append(current_date)
    current_date += timedelta(days=1)

# Generar presentes
presentes = []
for fecha in fechas:
    for jugador in jugadores:
        presentes.append({
            "apellido": jugador["apellido"],
            "nombre": jugador["nombre"],
            "fecha": fecha,
            "presente": random.choice([True, False])
        })

# Insertar presentes
presentes_col.insert_many(presentes)

print("Datos generados y cargados en MongoDB exitosamente.")
