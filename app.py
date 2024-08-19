# app.py
import streamlit as st

# Configuración de la aplicación
st.set_page_config(page_title="Mi Aplicación", layout="wide")

# Ocultar la barra lateral con CSS
st.markdown(
    """
    <style>
    .css-1l02z6u {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)


from streamlit_option_menu import option_menu
import estadisticas as estadisticas
import presentes as presentes
import jugadores as jugadores



# Navegación entre páginas
selected_page = option_menu(
    menu_title="Menú",
    options=["Estadísticas", "Gestión de Asistencias", "Gestión de Jugadores"],
    icons=["bar-chart", "calendar-check", "person"],
    orientation="horizontal"
)

# Cargar la página seleccionada
if selected_page == "Gestión de Asistencias":
    presentes.run()
elif selected_page == "Estadísticas":
    estadisticas.run()
elif selected_page == "Gestión de Jugadores":
    jugadores.run()
