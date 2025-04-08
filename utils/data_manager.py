import os
import uuid
import time
import pandas as pd
import streamlit as st

# Configuración de la página (Debe ser lo primero)
st.set_page_config(page_title="Garmin Data", layout="wide")

# Crear carpeta de datos si no existe
if not os.path.exists("data"):
    os.makedirs("data")

# Función para obtener un ID de usuario único para cada sesión
def get_user_id():
    # Generar un UUID único para cada sesión
    return str(uuid.uuid4())

# Obtener el ID de usuario único para esta sesión
user_id = get_user_id()

# Mostrar el user_id para verificar
# st.write(f"User ID: {user_id}")

# Nombre del archivo por usuario
def get_user_file_path():
    return f"data/actividades_{user_id}.csv"

# Guardar los datos
def save_data(df):
    limpiar_archivos_antiguos("data")  # Limpieza automática
    try:
        df.to_csv(get_user_file_path(), index=False)
        # st.write(f"Datos guardados en {get_user_file_path()}")
    except Exception as e:
        st.error(f"Ocurrió un error al intentar guardar los datos: {e}")

# Cargar los datos
def load_data():
    path = get_user_file_path()
    try:
        # Si el archivo del usuario no existe, cargamos el archivo de muestra
        if not os.path.exists(path):
            st.warning('Puesto que usted no ha subido datos, la siguiente información ha sido generada con un archivo de muestra.', icon="⚠️")
            return pd.read_csv("data/actividades_muestra.csv")
        else:
            # Si el archivo del usuario existe, cargamos los datos del archivo correspondiente
            return pd.read_csv(path)
    except Exception as e:
        st.error(f"Ocurrió un error al intentar cargar los datos: {e}")
        return None

# Limpiar archivos viejos
def limpiar_archivos_antiguos(directorio, edad_maxima_segundos=900):  # 15 minutos
    ahora = time.time()
    for archivo in os.listdir(directorio):
        if archivo.endswith(".csv"):
            ruta = os.path.join(directorio, archivo)
            try:
                if ahora - os.path.getmtime(ruta) > edad_maxima_segundos:
                    os.remove(ruta)
            except Exception as e:
                st.warning(f"No se pudo eliminar el archivo {archivo}: {e}")
