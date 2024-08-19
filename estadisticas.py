# pages/estadisticas.py
import streamlit as st
import pandas as pd
import pymongo
import unicodedata
from datetime import datetime, date
import io

# Función para conectar con MongoDB
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient("mongodb+srv://martinjauma:1234@cluster0.whflcwt.mongodb.net/")

# Obtener cliente y colecciones
client = get_mongo_client()
db = client["Presentes"]
jugadores_collection = db["Jugadores"]
presentes_collection = db["Presentes"]

# Función para normalizar texto (eliminar acentos y convertir a minúsculas)
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()

# Función para dar formato al nombre
def format_nombre(nombre):
    return nombre.capitalize()

# Función para dar formato al apellido
def format_apellido(apellido):
    return apellido.upper()

# Función para obtener jugadores cacheados
@st.cache_data(ttl=600)
def get_jugadores():
    return list(jugadores_collection.find({}, {"_id": 1, "apellido": 1, "nombre": 1, "posicion": 1}))

# Función para obtener posiciones cacheadas
@st.cache_data(ttl=600)
def get_posiciones():
    return jugadores_collection.distinct("posicion")

# Función para obtener fechas únicas cacheadas
@st.cache_data(ttl=600)
def get_fechas_unicas():
    fechas = presentes_collection.distinct("fecha")
    return [f.date() for f in fechas if isinstance(f, datetime)]

# Función para convertir datetime.date a datetime.datetime
def date_to_datetime(date_obj):
    return datetime.combine(date_obj, datetime.min.time())

# Función para obtener asistencia en un rango de fechas y total
def get_asistencia(fecha_inicio, fecha_fin, filtro_posiciones):
    fecha_inicio_datetime = date_to_datetime(fecha_inicio)
    fecha_fin_datetime = date_to_datetime(fecha_fin)
    fechas_unicas = get_fechas_unicas()
    fechas_rango = [date_to_datetime(fecha) for fecha in fechas_unicas if fecha_inicio <= fecha <= fecha_fin]
    jugadores = get_jugadores()
    resultados = []
    for jugador in jugadores:
        if "Todos" in filtro_posiciones or jugador["posicion"] in filtro_posiciones:
            asistencias_rango = list(presentes_collection.find({
                "jugador_id": jugador['_id'],
                "fecha": {"$in": fechas_rango}
            }))
            fechas_presentes_rango = set(a['fecha'].date() for a in asistencias_rango if a.get("presente") and 'fecha' in a)
            total_fechas_rango = len(fechas_rango)
            total_fechas_presentes_rango = len(fechas_presentes_rango)
            porcentaje_asistencia_rango = round((total_fechas_presentes_rango / total_fechas_rango) * 100) if total_fechas_rango > 0 else 0
            asistencias_total = list(presentes_collection.find({"jugador_id": jugador['_id']}))
            fechas_total = set(a['fecha'].date() for a in asistencias_total if 'fecha' in a)
            fechas_presentes_total = set(a['fecha'].date() for a in asistencias_total if a.get("presente") and 'fecha' in a)
            total_fechas_total = len(get_fechas_unicas())
            total_fechas_presentes_total = len(fechas_presentes_total)
            porcentaje_asistencia_total = round((total_fechas_presentes_total / total_fechas_total) * 100) if total_fechas_total > 0 else 0
            resultados.append({
                "Nombre": f"{jugador['apellido']}, {jugador['nombre']}",
                "Asistencia en Rango": f"{porcentaje_asistencia_rango}%",
                "Asistencia Total": f"{porcentaje_asistencia_total}%"
            })
    df = pd.DataFrame(resultados)
    df.index = df.index + 1  # Start index from 1
    df.index.name = 'N°'
    return df

# Función para actualizar las estadísticas en session_state
def actualizar_statistics(fecha_inicio, fecha_fin, posiciones):
    st.session_state["statistics_df"] = get_asistencia(fecha_inicio, fecha_fin, posiciones)

# Función principal para ejecutar la página de estadísticas
def run():
    st.title("🏉 Estadísticas")
    if "statistics_df" not in st.session_state:
        st.session_state["statistics_df"] = pd.DataFrame()  # DataFrame vacío inicialmente
    fecha_inicio = st.date_input("Fecha de Inicio", value=date.today())
    fecha_fin = st.date_input("Fecha de Fin", value=date.today())
    posiciones = st.multiselect("Filtrar por Posición", options=["Todos"] + get_posiciones(), default=["Todos"])
    if st.button("Actualizar Estadísticas"):
        actualizar_statistics(fecha_inicio, fecha_fin, posiciones)
    df = st.session_state["statistics_df"]
    if not df.empty:
        st.write("## Estadísticas de Asistencia")
        def color_coding(val):
            if val.strip('%') == '0':
                color = 'white'
            else:
                porcentaje = int(val.strip('%'))
                if porcentaje < 50:
                    color = 'red'
                elif porcentaje < 75:
                    color = 'orange'
                else:
                    color = 'green'
            return f'color: {color}'
        df_styled = df.style.applymap(color_coding, subset=["Asistencia en Rango", "Asistencia Total"])
        st.dataframe(df_styled)
        def convert_df_to_csv(df):
            buffer = io.StringIO()
            df.to_csv(buffer, index=True)
            buffer.seek(0)
            return buffer.getvalue()
        csv = convert_df_to_csv(df)
        st.download_button(
            label="Descargar Estadísticas CSV",
            data=csv,
            file_name='estadisticas_asistencia.csv',
            mime='text/csv'
        )
    else:
        st.write("No se encontraron datos para mostrar.")
