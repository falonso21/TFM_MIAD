import os
import time
import pandas as pd
import streamlit as st

# Asegurarse de que exista la carpeta "data"
if not os.path.exists("data"):
    os.makedirs("data")

# Función para obtener el nombre del archivo basándose en el user_id pasado
def get_user_file_path(user_id):
    return f"data/actividades_{user_id}.csv"

# Guardar los datos: requiere el DataFrame y el user_id de la sesión
def save_data(df, user_id):
    limpiar_archivos_antiguos("data")  # Limpieza automática
    try:
        df.to_csv(get_user_file_path(user_id), index=False)
        # st.write(f"Datos guardados en {get_user_file_path(user_id)}")
    except Exception as e:
        st.error(f"Ocurrió un error al guardar los datos: {e}")

# Cargar los datos: requiere el user_id de la sesión
def load_data(user_id):
    path = get_user_file_path(user_id)
    try:
        # Si el archivo del usuario no existe, se carga el CSV de muestra
        if not os.path.exists(path):
            st.warning('Puesto que no se han subido datos, se mostrará un archivo de muestra.', icon="⚠️")
            return pd.read_csv("data/actividades_muestra.csv")
        else:
            # Si el archivo existe, se cargan los datos
            return pd.read_csv(path)
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
        return None

# Limpiar archivos viejos (por defecto, archivos con más de 15 minutos)
def limpiar_archivos_antiguos(directorio, edad_maxima_segundos=900):
    ahora = time.time()
    for archivo in os.listdir(directorio):
        if archivo.endswith(".csv"):
            ruta = os.path.join(directorio, archivo)
            try:
                if ahora - os.path.getmtime(ruta) > edad_maxima_segundos:
                    os.remove(ruta)
            except Exception as e:
                st.warning(f"No se pudo eliminar el archivo {archivo}: {e}")
