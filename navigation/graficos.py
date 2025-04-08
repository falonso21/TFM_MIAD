import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from pyecharts.charts import Calendar, Pie, Bar, Scatter, Geo
from pyecharts import options as opts
from pyecharts.globals import ChartType, SymbolType
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts
import seaborn as sns
from utils.data_manager import load_data

def mostrar_graficos(df):

    # Definir una paleta de colores fija
    colores = [
        "#4E79A7",  # Azul
        "#F28E2B",  # Naranja
        "#E15759",  # Rojo
        "#76B7B2",  # Verde azulado
        "#59A14F",  # Verde
        "#EDC949",  # Amarillo
        "#AF7AA1",  # Púrpura
        "#FF9DA7",  # Rosa claro
        "#9C755F",  # Marrón
        "#BAB0AC",  # Gris
        "#86BCB6",  # Verde menta
        "#F4A582",  # Naranja salmón
        "#92C5DE",  # Azul cielo
        "#D6604D",  # Rojo ladrillo
        "#4393C3",  # Azul acero
        "#B2182B",  # Rojo intenso
        "#D4B9DA",  # Lila pastel
        "#E6F598",  # Verde lima claro
        "#999999",  # Gris neutro
        "#D95F02",  # Naranja oscuro
    ]

    st.header("Frecuencia y tipo de entrenamiento por año")
    st.write("En esta sección se presentan diferentes gráficos que, de un rápido vistazo, nos permiten ver como ha sido la frecuencia de entrenamiento"
    "y el tipo de deportes practicados en un determinado año de entre todos los registrados.")

    # Convertir la columna a tipo datetime
    df["Fecha de Inicio"] = pd.to_datetime(df["Fecha de Inicio"], errors='coerce')

    # Eliminar valores nulos en la fecha y en la columna "Deporte"
    df = df.dropna(subset=["Fecha de Inicio", "Deporte"])

    # Obtener todos los deportes únicos **del dataset completo**, no solo del año seleccionado
    deportes_unicos_totales = sorted(df["Deporte"].unique())

    # Crear un mapeo **fijo** de colores basado en los deportes globales
    color_map_global = {deporte: colores[i % len(colores)] for i, deporte in enumerate(deportes_unicos_totales)}

    # Obtener los años disponibles en el dataset
    df["Año"] = df["Fecha de Inicio"].dt.year
    años_disponibles = sorted(df["Año"].unique(), reverse=True)

    # Desplegable para seleccionar el año
    año_seleccionado = st.selectbox("Selecciona un año", años_disponibles)

    # Interfaz de Streamlit
    st.subheader("📅 Calendario de Entrenamientos por Deporte")
    st.write("Selecciona un año para ver los entrenamientos realizados con colores según el deporte.")

    # Filtrar los datos por el año seleccionado
    df_filtrado = df[df["Año"] == año_seleccionado].copy()

    # Seleccionar una sola actividad por día (de manera aleatoria)
    df_filtrado["Fecha"] = df_filtrado["Fecha de Inicio"].dt.date
    df_filtrado = df_filtrado.groupby("Fecha").apply(lambda x: x.sample(1)).reset_index(drop=True)

    # Obtener lista de deportes únicos del año seleccionado
    deportes_unicos = df_filtrado["Deporte"].unique()

    # Crear la lista de datos [(fecha, deporte_index)] para el calendario
    data_calendar = [(str(row["Fecha"]), deportes_unicos_totales.index(row["Deporte"]) + 1) for _, row in df_filtrado.iterrows()]

    # Crear lista de mapeo para el visualmap (asociar colores con deportes)
    pieces = [{"value": deportes_unicos_totales.index(deporte) + 1, "label": deporte, "color": color_map_global[deporte]} for deporte in deportes_unicos]

    # Definir rango de fechas para el calendario
    start_date = f"{año_seleccionado}-01-01"
    end_date = f"{año_seleccionado}-12-31"

    # Crear el gráfico de calendario
    calendar = (
        Calendar()
        .add("", data_calendar, calendar_opts=opts.CalendarOpts(range_=[start_date, end_date]))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Entrenamientos en {año_seleccionado}"),
            visualmap_opts=opts.VisualMapOpts(is_piecewise=True,
                                            pieces=pieces,
                                            orient="horizontal",  
                                            pos_bottom="0%",  
                                            pos_left="center"),  
        )
    )

    # Mostrar gráfico de calendario en Streamlit
    st_pyecharts(calendar)
    # Crear columnas para poner los gráficos lado a lado
    col1, col2 = st.columns(2)

    # ─────────────────────────────────────────────────────────────
    # 🔹 GRÁFICO DE TARTA: DISTRIBUCIÓN DE ENTRENAMIENTOS POR DEPORTE
    # ─────────────────────────────────────────────────────────────
    # Contar cantidad de entrenamientos por deporte
    entrenamientos_por_deporte = df_filtrado["Deporte"].value_counts()

    # Convertir a formato adecuado para pyecharts
    data_pie = [[deporte, int(cantidad)] for deporte, cantidad in zip(entrenamientos_por_deporte.index, entrenamientos_por_deporte.values)]

    # Usar la misma asignación de colores global
    pie_colores = [color_map_global[deporte] for deporte in entrenamientos_por_deporte.index]

    # Crear el gráfico de tarta con los colores asignados
    pie = (
        Pie()
        .add(
            "", 
            data_pie, 
            radius=["40%", "70%"],  
            rosetype="area",  
        )
        .set_colors(pie_colores)  
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Distribución de Entrenamientos en {año_seleccionado}"),
            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="-10%"),  # Leyenda en la parte inferior
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}: {c} ({d}%)",  
                rich={
                    "b": {"fontSize": 16, "fontWeight": "bold", "color": "#ffffff"},
                    "c": {"fontSize": 14, "color": "#FFD700"},  
                    "d": {"fontSize": 12, "color": "#FF6347"},  
                }
            )
        )  
    )

    # ─────────────────────────────────────────────────────────────
    # 🔹 GRÁFICO DE BARRAS: CALORÍAS TOTALES POR DEPORTE
    # ─────────────────────────────────────────────────────────────

    # Filtrar los datos para el año seleccionado
    df_filtrado = df[df["Año"] == año_seleccionado]
    with col2:
        st.subheader("📊 Calorías Totales por Deporte")
        st.write(f"Este gráfico muestra las calorías totales consumidas por tipo de deporte en el año {año_seleccionado}.")
        aggregation = st.selectbox("Selecciona un tipo de agregación", ["Calorías totales", "Calorías medias"])
    
    if aggregation == "Calorías totales":
        # Agrupar por deporte y sumar las calorías
        calorias_por_deporte = df_filtrado.groupby("Deporte")["Calorías"].sum().reset_index()
    elif aggregation == "Calorías medias":
        # Agrupar por deporte y hacer media de las calorías
        calorias_por_deporte = df_filtrado.groupby("Deporte")["Calorías"].mean().reset_index()

    # Ordenar los deportes por el total de calorías
    calorias_por_deporte = calorias_por_deporte.sort_values("Calorías", ascending=False)

    # Crear la lista de barras con colores asignados a cada deporte
    barras = []
    for idx, row in calorias_por_deporte.iterrows():
        deporte = row["Deporte"]
        calorias = round(row["Calorías"],1)
        
        # Asignar el color usando el mapeo de colores global
        color = color_map_global[deporte]

        # Crear un BarItem para cada barra con el valor y el color correspondiente
        barras.append(
            opts.BarItem(
                name=deporte,
                value=calorias,
                itemstyle_opts=opts.ItemStyleOpts(color=color)  # Asignar color a la barra
            )
        )

    # Crear el gráfico de barras
    bar = (
        Bar()
        .add_xaxis(calorias_por_deporte["Deporte"].tolist())  # Etiquetas de los deportes
        .add_yaxis("Calorías Totales", barras, category_gap=0)  # Pasar las barras con los colores
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{aggregation} en {año_seleccionado}"),
            xaxis_opts=opts.AxisOpts(name="Deporte", axislabel_opts=opts.LabelOpts(rotate=-45)),
            yaxis_opts=opts.AxisOpts(name="Calorías"),
            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="-10%"),  # Leyenda en la parte inferior
            toolbox_opts=opts.ToolboxOpts(is_show=True, orient="horizontal", pos_top="0%"),
        )
    )

    # Mostrar gráfico de tarta en la primera columna
    with col1:
        st.subheader("🥧 Distribución de Tipos de Entrenamientos")
        st.write("Este gráfico muestra la cantidad de entrenamientos por tipo de deporte en el año seleccionado.")
        st_pyecharts(pie)

    # Mostrar gráfico de barras en la segunda columna
    with col2:
        st_pyecharts(bar)

    st.header("Relaciones de interés entre variables")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Relación entre Ritmo medio y distancia")
        
        # Asignar los colores a cada deporte en el scatter plot
        df_filtrado["Color"] = df_filtrado["Deporte"].map(color_map_global)
        
        fig = px.scatter(
            df_filtrado, 
            x="Distancia (m)", 
            y="Ritmo medio (min/km)", 
            color="Deporte",  # Usa el mismo esquema de colores
            color_discrete_map=color_map_global,  # Aplica el mapeo de colores
            hover_data=["Nombre de la Actividad", "Calorías", "Frecuencia Cardíaca Media"], 
            title="Relación entre Ritmo medio y Distancia",
            labels={"Distancia (m)": "Distancia (m)", "Ritmo medio (min/km)": "Ritmo medio (min/km)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Relación entre frecuencia media y distancia")
        
        fig = px.scatter(
            df_filtrado, 
            x="Distancia (m)", 
            y="Frecuencia Cardíaca Media", 
            color="Deporte",  # Usa el mismo esquema de colores
            color_discrete_map=color_map_global,  # Aplica el mapeo de colores
            hover_data=["Nombre de la Actividad", "Calorías", "Frecuencia Cardíaca Media"], 
            title="Relación entre Frecuencia Media y Distancia",
            labels={"Distancia (m)": "Distancia (m)", "Frecuencia Cardíaca Media": "Frecuencia Cardíaca Media"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col1:
        fig = px.scatter(
            df_filtrado, 
            x="Duración (min)", 
            y="Calorías", 
            color="Deporte",  # Usa el mismo esquema de colores
            color_discrete_map=color_map_global,  # Aplica el mapeo de colores
            hover_data=["Nombre de la Actividad", "Calorías", "Duración (min)"], 
            title="Relación entre Duración y Calorías",
            labels={"Duración (min)": "Duración (min)", "Calorías": "Calorías"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df_filtrado, 
            x="Duración (min)", 
            y="Frecuencia Cardíaca Máxima", 
            color="Deporte",  # Usa el mismo esquema de colores
            color_discrete_map=color_map_global,  # Aplica el mapeo de colores
            hover_data=["Nombre de la Actividad", "Frecuencia Cardíaca Máxima", "Duración (min)"], 
            title="Relación entre Duración y Frecuencia Cardíaca Máxima",
            labels={"Duración (min)": "Duración (min)", "Frecuencia Cardíaca Máxima": "Frecuencia Cardíaca Máxima"},
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.header(f"¿Dónde entrenaste en el año {año_seleccionado}?")

    # Filtrar datos que tienen coordenadas válidas
    df_geo = df_filtrado.dropna(subset=["Latitud", "Longitud"])

    # Convertir a tipo numérico (por si acaso)
    df_geo["Latitud"] = pd.to_numeric(df_geo["Latitud"], errors="coerce")
    df_geo["Longitud"] = pd.to_numeric(df_geo["Longitud"], errors="coerce")
    df_geo = df_geo.dropna(subset=["Latitud", "Longitud"])

    # Mostrar el heatmap
    st.map(df_geo, latitude="Latitud", longitude="Longitud")

    st.header("¿Cómo ha evolucionado tu VO2Max?")
    df_vo2max = df.dropna(subset=["VO2Max"])
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_vo2max['Fecha de Inicio'],
        y=df_vo2max['VO2Max'],
        mode='lines+markers',  # Esto especifica tanto líneas como marcadores
        name='VO2Max'
    ))

    st.plotly_chart(fig)



# Función de la página de gráficos
def graficos_page():
    st.title("Gráficos de Actividades")

    # Cargar los datos previamente descargados
    try:
        df = load_data()
        if df is not None:
            expander1= st.expander("Despliega para ver la tabla de datos")
            expander1.dataframe(df)
            mostrar_graficos(df)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")