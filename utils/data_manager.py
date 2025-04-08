import streamlit as st
import os
import uuid
import time
import pandas as pd

# Configuración de la página (Debe ser lo primero)
st.set_page_config(page_title="Garmin Data", layout="wide")

# Ruta de archivo para almacenar el user_id
USER_ID_FILE = "data/user_id.txt"

# Crear carpeta de datos si no existe
if not os.path.exists("data"):
    os.makedirs("data")

# Función para obtener el ID de usuario usando st.session_state
def get_user_id():
    # Si ya tenemos un user_id en la sesión, devolverlo
    if "user_id" in st.session_state:
        return st.session_state["user_id"]
    
    # Si no, leer el archivo o generar un nuevo UUID
    try:
        if os.path.exists(USER_ID_FILE):
            with open(USER_ID_FILE, "r") as file:
                user_id = file.read().strip()
        else:
            user_id = str(uuid.uuid4())
            with open(USER_ID_FILE, "w") as file:
                file.write(user_id)
        
        # Guardar el user_id en session_state para usarlo durante toda la sesión
        st.session_state["user_id"] = user_id
        return user_id
    except Exception as e:
        st.error(f"Ocurrió un error al intentar acceder al archivo de usuario: {e}")
        return None

# Obtener el ID de usuario
user_id = get_user_id()

# Si no se pudo obtener un user_id, detener la ejecución
if user_id is None:
    st.error("No se pudo generar o cargar el User ID. La aplicación no puede continuar.")
    st.stop()

# Mostrar el user_id para verificar
st.write(f"User ID: {user_id}")

# Nombre del archivo por usuario
def get_user_file_path():
    return f"data/actividades_{user_id}.csv"

# Guardar los datos
def save_data(df):
    limpiar_archivos_antiguos("data")  # Limpieza automática
    try:
        df.to_csv(get_user_file_path(), index=False)
        st.write(f"Datos guardados en {get_user_file_path()}")
    except Exception as e:
        st.error(f"Ocurrió un error al intentar guardar los datos: {e}")

# Cargar los datos
def load_data():
    path = get_user_file_path()
    try:
        if os.path.exists(path):
            return pd.read_csv(path)
        else:
            # Si el usuario aún no ha subido datos, puedes cargar un archivo base
            st.warning('Puesto que usted no ha subido datos, la siguiente información ha sido generada con un archivo de muestra.', icon="⚠️")
            return pd.read_csv("data/actividades_muestra.csv")
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
                st.warning
