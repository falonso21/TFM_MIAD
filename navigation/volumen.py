import streamlit as st
from utils.data_manager import load_data
import pandas as pd

# Función para procesar datos por semana
def calcular_volumen_semanal(df):
    # Verificar si la columna 'Fecha de Inicio' existe
    if 'Fecha de Inicio' not in df.columns:
        raise ValueError("La columna 'Fecha de Inicio' no se encuentra en los datos.")
    
    # Crear una copia para evitar modificaciones sobre el original
    df = df.copy()
    
    # Convertir a datetime con manejo de errores
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], errors='coerce')
    
    # Eliminar filas con fechas inválidas (NaT)
    df = df.dropna(subset=['Fecha de Inicio'])
    
    # Crear la columna 'Semana'
    df['Semana'] = df['Fecha de Inicio'].dt.to_period('W').apply(lambda r: f"{r.start_time.date()} a {r.end_time.date()}")
    
    # Agregar métricas por semana
    resumen = df.groupby('Semana').agg(
        Kilometros_Running=('Distancia (m)', lambda x: x[df['Deporte'] == 'running'].sum() / 1000),
        Kilometros_Cycling=('Distancia (m)', lambda x: x[df['Deporte'] == 'cycling'].sum() / 1000),
        Tiempo_Total=('Duración (min)', lambda x: x.sum() / 60),
        Dias_Entrenamiento=('Fecha de Inicio', 'count'),
        FC_Reposo=('Tasa Metabólica Basal', 'mean')
    ).reset_index()
    
    # Calcular el cambio porcentual para las columnas de kilómetros y tiempo
    resumen = calcular_cambio_km_running(resumen)
    resumen = calcular_cambio_km_cycling(resumen)
    resumen = calcular_cambio_tiempo_total(resumen)
    
    # Crear la columna Riesgo_Lesion basada en el cambio porcentual de Tiempo_Total
    resumen['Riesgo_Lesion'] = resumen['Cambio_Tiempo_Total %'].apply(lambda x: 'Alto' if x > 20 else 'Normal')
    
    # Calcular Ratio de Carga
    promedio_historico = resumen['Tiempo_Total'].mean()
    resumen['Ratio_Carga'] = resumen['Tiempo_Total'] / promedio_historico
    
    return resumen

# Función para calcular el cambio porcentual de kilómetros de running
def calcular_cambio_km_running(df_semanal):
    # Calcular el cambio porcentual de kilómetros de running
    df_semanal['Cambio_Km_Running %'] = df_semanal['Kilometros_Running'].pct_change() * 100
    
    # Reemplazar valores infinitos por 100 (asumiendo un 100% de incremento si fue cero antes)
    df_semanal['Cambio_Km_Running %'].replace([float('inf'), -float('inf')], 100, inplace=True)
    
    # Reemplazar NaN (que podría generarse en la primera fila) por 0
    df_semanal['Cambio_Km_Running %'].fillna(0, inplace=True)
    
    return df_semanal

# Función para calcular el cambio porcentual de kilómetros en bicicleta
def calcular_cambio_km_cycling(df_semanal):
    # Calcular el cambio porcentual de kilómetros en bicicleta
    df_semanal['Cambio_Km_Cycling %'] = df_semanal['Kilometros_Cycling'].pct_change() * 100
    
    # Reemplazar valores infinitos por 100 (asumiendo un 100% de incremento si fue cero antes)
    df_semanal['Cambio_Km_Cycling %'].replace([float('inf'), -float('inf')], 100, inplace=True)
    
    # Reemplazar NaN (que podría generarse en la primera fila) por 0
    df_semanal['Cambio_Km_Cycling %'].fillna(0, inplace=True)
    
    return df_semanal

# Función para calcular el cambio porcentual de tiempo total
def calcular_cambio_tiempo_total(df_semanal):
    # Calcular el cambio porcentual de tiempo total
    df_semanal['Cambio_Tiempo_Total %'] = df_semanal['Tiempo_Total'].pct_change() * 100
    
    # Reemplazar valores infinitos por 100 (asumiendo un 100% de incremento si fue cero antes)
    df_semanal['Cambio_Tiempo_Total %'].replace([float('inf'), -float('inf')], 100, inplace=True)
    
    # Reemplazar NaN (que podría generarse en la primera fila) por 0
    df_semanal['Cambio_Tiempo_Total %'].fillna(0, inplace=True)
    
    return df_semanal

# Función para resaltar toda la fila con riesgo de lesión
def resaltar_filas_riesgo(row):
    # Si el riesgo de lesión es "Alto", resaltar toda la fila
    return ['background-color: yellow' if row['Riesgo_Lesion'] == 'Alto' else '' for _ in row]

# Página en Streamlit
def volumen_semanal_page():
    st.title("📅 Volumen Semanal de Entrenamiento")
    
    try:
        df = load_data()
        
        if df is not None:
            expander1 = st.expander("Despliega para ver la tabla de datos original")
            expander1.dataframe(df)
            
            # Calcular los datos semanales con los indicadores de riesgo
            df_semanal = calcular_volumen_semanal(df)
            
            # Mostrar la tabla de datos semanales
            st.write("📊 Datos agregados por semana:")
            
            # Resaltar las filas con riesgo de lesión (cambio > 20% en Tiempo_Total)
            df_semanal_resaltado = df_semanal.style.apply(resaltar_filas_riesgo, axis=1)
            st.dataframe(df_semanal_resaltado)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
