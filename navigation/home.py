import streamlit as st
import pandas as pd
from garminconnect import Garmin
from utils.data_manager import save_data
GARMIN_LOGO = "assets/garmin-logo-0.png"

def obtener_actividades(email, password):
    client = Garmin(email, password)
    client.login()
    activities = client.get_activities(0, 5000)

    activity_data = []
    for act in activities:
        sport = act["activityType"]["typeKey"]
        cadence = act.get("averageRunningCadenceInStepsPerMinute") if sport == "running" else act.get("averageBikeCadence")
        max_cadence = act.get("maxRunningCadenceInStepsPerMinute") if sport == "running" else act.get("maxBikeCadence")
        
        lat = act.get("startLatitude")
        lon = act.get("startLongitude")
        elevation_gain = act.get("elevationGain")
        elevation_loss = act.get("elevationLoss")
        temperature = act.get("temperature")

        hr_zones = ["hrTimeInZone_1", "hrTimeInZone_2", "hrTimeInZone_3", "hrTimeInZone_4", "hrTimeInZone_5"]
        time_in_zones = {zone: act.get(zone, 0) for zone in hr_zones}
        
        distance = act.get("distance")
        duration = act.get("duration")
        avg_pace = (duration / 60) / (distance / 1000) if distance and duration else None

        activity_data.append({
            "Activity ID": act["activityId"],
            "Nombre de la Actividad": act.get("activityName"),
            "Fecha de Inicio": act.get("startTimeLocal"),
            "Deporte": sport,
            "Duración (min)": duration / 60 if duration else None,
            "Distancia (m)": distance,
            "Ritmo medio (min/km)": avg_pace,
            "Velocidad media (m/s)": act.get("averageSpeed"),
            "Velocidad máxima (m/s)": act.get("maxSpeed"),
            "Calorías": act.get("calories"),
            "Tasa Metabólica Basal": act.get("bmrCalories"),
            "Frecuencia Cardíaca Media": act.get("averageHR"),
            "Frecuencia Cardíaca Máxima": act.get("maxHR"),
            "Tiempo en Zona 1 (s)": time_in_zones["hrTimeInZone_1"],
            "Tiempo en Zona 2 (s)": time_in_zones["hrTimeInZone_2"],
            "Tiempo en Zona 3 (s)": time_in_zones["hrTimeInZone_3"],
            "Tiempo en Zona 4 (s)": time_in_zones["hrTimeInZone_4"],
            "Tiempo en Zona 5 (s)": time_in_zones["hrTimeInZone_5"],
            "VO2Max": act.get("vO2MaxValue"),
            "Cadencia Media (spm)": cadence,
            "Cadencia Máxima (spm)": max_cadence,
            "Elevación Ganada (m)": elevation_gain,
            "Elevación Perdida (m)": elevation_loss,
            "Potencia Media (W)": act.get("averagePower"),
            "Potencia Máxima (W)": act.get("maxPower"),
            "Temperatura (°C)": temperature,
            "Latitud": lat,
            "Longitud": lon,
            "Lugar": act.get("locationName")
        })
    
    return pd.DataFrame(activity_data)

def home_page(user_id):
    # st.image(GARMIN_LOGO)
    st.title("Bienvenido a Garmin Data")
    email = st.text_input("Introduce tu email de Garmin")
    password = st.text_input("Introduce tu contraseña de Garmin", type="password")

    if st.button("Descargar Datos"):
        if email and password:
            try:
                df = obtener_actividades(email, password)
                save_data(df, user_id)
                st.write(df)
                st.success("Datos descargados correctamente")
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
        else:
            st.warning("Por favor, ingresa tus credenciales.")
