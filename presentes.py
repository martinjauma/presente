# pages/presentes.py
import streamlit as st
import pymongo
from datetime import date, datetime

# Función para conectar con MongoDB
def get_mongo_client():
    return pymongo.MongoClient("mongodb+srv://martinjauma:1234@cluster0.whflcwt.mongodb.net/")

# Obtener cliente y colecciones
client = get_mongo_client()
db = client["Presentes"]
jugadores_collection = db["Jugadores"]
presentes_collection = db["Presentes"]

# Obtener jugadores ordenados por apellido y nombre
def get_jugadores():
    return list(jugadores_collection.find({}, {"_id": 1, "apellido": 1, "nombre": 1, "posicion": 1}).sort([("apellido", 1), ("nombre", 1)]))

# Convertir la fecha seleccionada a datetime
def convertir_fecha_a_datetime(fecha):
    return datetime.combine(fecha, datetime.min.time())

# Obtener asistencia por fecha
def get_asistencia_por_fecha(fecha_seleccionada):
    fecha_datetime = convertir_fecha_a_datetime(fecha_seleccionada)
    return list(presentes_collection.find({"fecha": fecha_datetime}))

# Función para guardar la asistencia
def guardar_asistencia(presentes, fecha_seleccionada):
    fecha_datetime = convertir_fecha_a_datetime(fecha_seleccionada)
    for jugador_id, estado in presentes.items():
        presentes_collection.update_one(
            {"jugador_id": jugador_id, "fecha": fecha_datetime},
            {"$set": {"presente": estado}},
            upsert=True
        )

# Función principal para ejecutar la página de gestión de asistencias
def run():
    st.title("📋 Editar Asistencia")
    fecha_seleccionada = st.date_input("Seleccionar fecha", value=date.today())
    jugadores = get_jugadores()
    asistencia_anterior = get_asistencia_por_fecha(fecha_seleccionada)
    asistencia_dict = {a['jugador_id']: a.get('presente', False) for a in asistencia_anterior}

    st.write("## Lista de Jugadores")
    presentes = {}
    for jugador in jugadores:
        nombre = f"{jugador['apellido']}, {jugador['nombre']}"
        estado = st.checkbox(nombre, value=asistencia_dict.get(jugador['_id'], False))
        presentes[jugador['_id']] = estado

    if st.button("Guardar Asistencia"):
        guardar_asistencia(presentes, fecha_seleccionada)
        st.success("Asistencia guardada exitosamente")
