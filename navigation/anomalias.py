import streamlit as st
from utils.data_manager import load_data
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px

def deteccion_anomalias(df):
    # Filtrar solo actividades de Running
    df = df[df['Deporte'] == 'running']
    
    # Selección de variables relevantes
    df["Tiempo (s)"] = df["Duración (min)"] * 60
    df['Velocidad_Media'] = df['Distancia (m)'] / df['Tiempo (s)']
    df = df[['Distancia (m)', 'Tiempo (s)', 'Velocidad_Media', 'Elevación Ganada (m)', 'Frecuencia Cardíaca Media']]
    
    # Manejo de valores nulos
    df = df.dropna()
    
    # Entrenar modelo Isolation Forest
    modelo = IsolationForest(contamination=0.05, random_state=42)
    df['Anomalia'] = modelo.fit_predict(df)
    
    # Filtrar anomalías
    anomalies = df[df['Anomalia'] == -1]
    
    # Crear gráfico de dispersión con plotly
    fig = px.scatter(
        df, 
        x='Distancia (m)', 
        y='Velocidad_Media', 
        color=df['Anomalia'].map({1: "Normal", -1: "Anomalía"}),
        color_discrete_map={"Normal": "blue", "Anomalía": "red"},
        title="Detección de Anomalías en Running",
        labels={"Distancia (m)": "Distancia (m)", "Velocidad_Media": "Velocidad Media (m/s)"}
    )
    
    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig)
    
    # Mostrar entrenamientos anómalos
    st.write("⚠️ Entrenamientos anómalos detectados:")
    st.dataframe(anomalies)

def anomalias_page():
    st.title("Detección de anomalías")
    try:
        df = load_data()
        if df is not None:
            expander1 = st.expander("Despliega para ver la tabla de datos")
            expander1.dataframe(df)
            deteccion_anomalias(df)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")