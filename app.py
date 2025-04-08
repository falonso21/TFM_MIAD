import streamlit as st
from streamlit_option_menu import option_menu  # Para crear un menú de opciones entre las páginas

# Páginas
from navigation import home, graficos, predicciones, anomalias, clustering, volumen
SDC_LOGO = "assets/SDC_Hor_250.png"


# Función principal de la app
def main():
    st.set_page_config(page_title="Garmin Data", layout="wide")
    st.sidebar.image(SDC_LOGO, use_container_width=True)

    # Menú de navegación
    with st.sidebar:
        selected = option_menu(
            "Navegación",
            ["Home", "Gráficos", "Predicciones de carrera", "Detección de anomalías", "Clustering de entrenamientos", "Carga semanal de entrenamientos"],
            icons=["house", "bar-chart", "trophy", "lightbulb", "diagram-3", "calendar-week"],
            menu_icon="cast",
            default_index=0
        )

    # Condicional para mostrar las páginas
    if selected == "Home":
        home.home_page()
    elif selected == "Gráficos":
        graficos.graficos_page()
    elif selected == "Predicciones de carrera":
        predicciones.predicciones_page()
    elif selected == "Detección de anomalías":
        anomalias.anomalias_page()
    elif selected == "Clustering de entrenamientos":
        clustering.clustering_page()
    elif selected == "Carga semanal de entrenamientos":
        volumen.volumen_semanal_page()

    About1 = st.sidebar.markdown('## 🤝 Sobre mí')

    About = st.sidebar.info('Mi nombre es Francisco Alonso, soy un científico de datos con más de 6 años de experiencia. Este dashboard nace como proyecto TFM del Máster en Inteligencia Artificial aplicada al deporte que he cursado en 2024/25 con la idea de poder aplicar mis conocimientos de IA en el sector deportivo.')

    Contact = st.sidebar.markdown('## 📩 ¡Encuéntrame en LinkedIn!')
    Contact1 = st.sidebar.info('[Francisco Alonso Fernández](https://www.linkedin.com/in/franciscoalonsofernandez/) Senior Data Scientist en [Atos](https://atos.net/es/espana).')

    

if __name__ == "__main__":
    main()
