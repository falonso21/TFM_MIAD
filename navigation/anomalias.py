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

def anomalias_page(user_id):
    st.title("Detección de anomalías")
    try:
        df = load_data(user_id)
        if df is not None:
            st.markdown("""
                        En esta página se aplica un modelo de **detección de anomalías** utilizando el algoritmo **Isolation Forest** sobre tus actividades de **running**.  
                        El objetivo es encontrar entrenamientos que se salgan de tu patrón habitual, ya sea por su duración, intensidad, velocidad o elevación.

                        ### ¿Cómo funciona Isolation Forest?
                        Isolation Forest es un algoritmo basado en árboles de decisión que **"aísla" observaciones inusuales**.  
                        Funciona generando múltiples árboles aleatorios y dividiendo los datos por características seleccionadas al azar. Las observaciones que son más fáciles de aislar (es decir, que se separan en menos divisiones) son marcadas como **anómalas**, porque sus características son menos comunes comparadas con el resto del conjunto.

                        Este método es rápido, eficiente y muy útil para detectar datos atípicos incluso en grandes volúmenes de información.

                        ### ¿Para qué puede servirte?
                        - Detectar errores en la recolección de datos (por ejemplo, GPS inexacto o fallos del dispositivo).
                        - Identificar sesiones que no siguen tu ritmo habitual (muy suaves, intensas, largas o cortas).
                        - Revisar entrenamientos únicos o fuera de lo común que podrían requerir una atención especial o un análisis más profundo.

                        Se visualiza cada actividad en un gráfico interactivo, diferenciando claramente los entrenamientos normales de las posibles **anomalías**.
                        """)

            expander1 = st.expander("Despliega para ver la tabla de datos")
            expander1.dataframe(df)
            deteccion_anomalias(df)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
