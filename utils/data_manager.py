import os
import uuid
import time
import pandas as pd
import streamlit as st

# Crear carpeta de datos si no existe
if not os.path.exists("data"):
    os.makedirs("data")

# Asegurarse de que 'user_id' exista en session_state al principio de la app
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())  # Crear un ID único para la sesión

# Nombre del archivo por usuario
def get_user_file_path():
    return f"data/actividades_{st.session_state['user_id']}.csv"

# Guardar los datos
def save_data(df):
    limpiar_archivos_antiguos("data")  # Limpieza automática
    df.to_csv(get_user_file_path(), index=False)

# Cargar los datos
def load_data():
    path = get_user_file_path()
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        # Si el usuario aún no ha subido datos, puedes cargar un archivo base
        return pd.read_csv("data/actividades_muestra.csv")

# Limpiar archivos viejos
def limpiar_archivos_antiguos(directorio, edad_maxima_segundos=900):  # 15 minutos
    ahora = time.time()
    for archivo in os.listdir(directorio):
        if archivo.endswith(".csv"):
            ruta = os.path.join(directorio, archivo)
            if ahora - os.path.getmtime(ruta) > edad_maxima_segundos:
                os.remove(ruta)
