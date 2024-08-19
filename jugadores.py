import streamlit as st
import pymongo
from bson.objectid import ObjectId

# Función para conectar con MongoDB
def get_mongo_client():
    return pymongo.MongoClient("mongodb+srv://martinjauma:1234@cluster0.whflcwt.mongodb.net/")

# Obtener cliente y colecciones
client = get_mongo_client()
db = client["Presentes"]
jugadores_collection = db["Jugadores"]

# Obtener jugadores ordenados por apellido y nombre
def get_jugadores():
    return list(jugadores_collection.find({}, {"_id": 1, "apellido": 1, "nombre": 1, "posicion": 1}).sort([("apellido", 1), ("nombre", 1)]))

# Obtener posiciones únicas
def get_posiciones():
    return list(jugadores_collection.distinct("posicion"))

# Agregar un nuevo jugador
def agregar_jugador(nombre, apellido, posicion):
    nombre_formateado = nombre.capitalize()
    apellido_formateado = apellido.upper()
    jugadores_collection.insert_one({
        "nombre": nombre_formateado,
        "apellido": apellido_formateado,
        "posicion": posicion
    })

# Editar un jugador existente
def editar_jugador(jugador_id, nombre, apellido, posicion):
    nombre_formateado = nombre.capitalize()
    apellido_formateado = apellido.upper()
    jugadores_collection.update_one(
        {"_id": ObjectId(jugador_id)},
        {"$set": {"nombre": nombre_formateado, "apellido": apellido_formateado, "posicion": posicion}}
    )

# Eliminar un jugador
def eliminar_jugador(jugador_id):
    jugadores_collection.delete_one({"_id": ObjectId(jugador_id)})

# Función principal para ejecutar la página de gestión de jugadores
def run():
    st.title("📋 Gestión de Jugadores")

    # Obtener posiciones únicas
    posiciones = get_posiciones()

    # Menú de selección para Alta, Editar o Eliminar
    opcion = st.selectbox("Selecciona una opción", ["ALTA", "EDITAR", "ELIMINAR"])

    if opcion == "ALTA":
        st.header("Alta de Jugadores")
        with st.form(key='alta_jugador'):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            posicion = st.selectbox("Posición", options=posiciones)
            submit_button = st.form_submit_button("Agregar Jugador")
            if submit_button:
                if nombre and apellido and posicion:
                    agregar_jugador(nombre, apellido, posicion)
                    st.success("Jugador agregado exitosamente")
                else:
                    st.error("Por favor complete todos los campos.")

    elif opcion == "EDITAR":
        st.header("Editar Jugadores")
        jugadores = get_jugadores()
        jugador_seleccionado = st.selectbox("Seleccionar Jugador para Editar", options=[f"{j['apellido']}, {j['nombre']}" for j in jugadores])
        jugador = next((j for j in jugadores if f"{j['apellido']}, {j['nombre']}" == jugador_seleccionado), None)

        if jugador:
            with st.form(key='editar_jugador'):
                nombre = st.text_input("Nombre", value=jugador["nombre"])
                apellido = st.text_input("Apellido", value=jugador["apellido"])
                posicion = st.selectbox("Posición", options=posiciones, index=posiciones.index(jugador["posicion"]))
                submit_button = st.form_submit_button("Actualizar Jugador")
                if submit_button:
                    if nombre and apellido and posicion:
                        editar_jugador(jugador['_id'], nombre, apellido, posicion)
                        st.success("Jugador actualizado exitosamente")
                    else:
                        st.error("Por favor complete todos los campos.")
        else:
            st.warning("Selecciona un jugador para editar.")

    elif opcion == "ELIMINAR":
        st.header("Eliminar Jugadores")
        jugadores = get_jugadores()
        jugador_para_eliminar = st.selectbox("Seleccionar Jugador para Eliminar", options=[f"{j['apellido']}, {j['nombre']}" for j in jugadores])
        jugador_a_eliminar = next((j for j in jugadores if f"{j['apellido']}, {j['nombre']}" == jugador_para_eliminar), None)
        
        if jugador_a_eliminar:
            if st.button(f"Eliminar {jugador_a_eliminar['apellido']}, {jugador_a_eliminar['nombre']}"):
                eliminar_jugador(jugador_a_eliminar['_id'])
                st.success("Jugador eliminado exitosamente")
        else:
            st.warning("Selecciona un jugador para eliminar.")
