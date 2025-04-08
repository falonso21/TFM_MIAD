import streamlit as st
from utils.data_manager import load_data
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import plotly.express as px

def aplicar_clustering(df, eps=0.5, min_samples=5):
    # Filtrar solo actividades de Running y Ciclismo
    df = df[df['Deporte'].isin(['running', 'cycling'])]
    
    # Selección de variables relevantes
    df['Tiempo (s)'] = df['Duración (min)'] * 60
    df['Velocidad_Media'] = df['Distancia (m)'] / df['Tiempo (s)']
    df = df[['Distancia (m)', 'Tiempo (s)', 'Velocidad_Media', 'Elevación Ganada (m)', 'Frecuencia Cardíaca Media']]
    
    # Manejo de valores nulos
    df = df.dropna()
    
    # Normalización de los datos
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    
    # Aplicar DBSCAN
    modelo = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = modelo.fit_predict(df_scaled)
    df['Cluster'] = clusters
    
    # Crear gráfico interactivo con plotly
    fig = px.scatter(
        df, 
        x='Distancia (m)', 
        y='Velocidad_Media', 
        color=df['Cluster'].astype(str),
        title="Clustering de Actividades Deportivas con DBSCAN",
        labels={"Distancia (m)": "Distancia (m)", "Velocidad_Media": "Velocidad Media (m/s)"},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    return df, fig

def clustering_page(user_id):
    st.title("Clustering de Actividades con DBSCAN")
    
    try:
        if 'df' not in st.session_state or st.button("Actualizar Datos"):
            st.session_state.df = load_data(user_id)
        df = st.session_state.df
        
        if df is not None:
            st.markdown("""
            Esta página aplica **técnicas de clustering** (agrupamiento) usando el algoritmo **DBSCAN** sobre tus actividades deportivas de **running** y **ciclismo**.  
            El objetivo es identificar **patrones ocultos** en tus entrenamientos, como sesiones similares en intensidad, duración o exigencia, agrupándolas automáticamente sin necesidad de clasificarlas manualmente.

            ### ¿Cómo funciona DBSCAN?
            **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) es un algoritmo de agrupamiento basado en densidad.  
            Agrupa puntos que están **cerca unos de otros** y considera como *ruido* o *anomalía* aquellos que no encajan en ningún grupo.

            Se basa en dos parámetros principales:
            - `eps`: la distancia máxima entre dos puntos para que se consideren vecinos.
            - `min_samples`: el número mínimo de puntos necesarios para formar un grupo denso.

            Esto lo hace ideal para identificar **grupos de entrenamientos similares**, sin necesidad de especificar cuántos grupos debe haber.

            ### ¿Para qué puede servirte?
            - Detectar distintos tipos de entrenamientos que sueles realizar (por ejemplo: salidas suaves, sesiones intensas, rutas de montaña).
            - Identificar posibles anomalías o entrenamientos atípicos.
            - Analizar tu evolución agrupando actividades similares para comparar progresos.

            Puedes ajustar los parámetros del algoritmo para afinar los resultados y explorar visualmente los grupos detectados en el gráfico interactivo.
            """)

            expander1 = st.expander("Despliega para ver la tabla de datos")
            expander1.dataframe(df)
            
            # Selección de parámetros para DBSCAN
            eps = st.slider("Selecciona el valor de eps", min_value=0.1, max_value=2.0, step=0.1, value=0.5)
            min_samples = st.slider("Selecciona el número mínimo de muestras", min_value=2, max_value=10, value=5)
            
            df_clustered, fig = aplicar_clustering(df, eps, min_samples)
            
            st.plotly_chart(fig)
            
            # Mostrar datos clusterizados
            st.write("📊 Datos clusterizados:")
            st.dataframe(df_clustered)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
