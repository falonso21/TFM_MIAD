import streamlit as st
from streamlit_option_menu import option_menu  # Para crear el menú de navegación

# Página y navegación (resto de imports)
from navigation import home, graficos, predicciones, anomalias, clustering, volumen

SDC_LOGO = "assets/SDC_Hor_250.png"

# Configuración de la página: DEBE estar al inicio
st.set_page_config(page_title="Garmin Data", layout="wide")

# Generar un user_id único por sesión y guardarlo en session_state
if "user_id" not in st.session_state:
    # Genera un UUID nuevo para cada usuario
    import uuid
    st.session_state["user_id"] = str(uuid.uuid4())

# Ahora obtenemos el user_id para la sesión actual
user_id = st.session_state["user_id"]
# st.write(f"User ID: {user_id}")  # Sólo para verificación; puedes quitarlo luego

# Coloca la imagen en la sidebar
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

# Según la opción seleccionada, muestra la página correspondiente.
if selected == "Home":
    home.home_page()   # Envíale el user_id a la página
elif selected == "Gráficos":
    graficos.graficos_page(user_id)
elif selected == "Predicciones de carrera":
    predicciones.predicciones_page(user_id)
elif selected == "Detección de anomalías":
    anomalias.anomalias_page(user_id)
elif selected == "Clustering de entrenamientos":
    clustering.clustering_page(user_id)
elif selected == "Carga semanal de entrenamientos":
    volumen.volumen_semanal_page(user_id)

# Información y contacto en la sidebar
st.sidebar.markdown('## 🤝 Sobre mí')
st.sidebar.info('Mi nombre es Francisco Alonso, soy un científico de datos con más de 6 años de experiencia. Este dashboard nace como proyecto TFM del Máster en Inteligencia Artificial aplicada al deporte que he cursado en 2024/25 con la idea de poder aplicar mis conocimientos de IA en el sector deportivo.')
st.sidebar.markdown('## 📩 ¡Encuéntrame en LinkedIn!')
st.sidebar.info('[Francisco Alonso Fernández](https://www.linkedin.com/in/franciscoalonsofernandez/) Senior Data Scientist en [Atos](https://atos.net/es/espana).')
