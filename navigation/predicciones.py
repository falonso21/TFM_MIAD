import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from utils.data_manager import load_data
import numpy as np
from xgboost import XGBRegressor  
import lightgbm as lgb

def prediction(df):
    # Filtrar datos solo para 'running'
    df = df[df['Deporte'] == 'running']
    
    if len(df) < 50:
        st.warning("No hay suficientes datos de carrera para hacer una predicción. Se requieren al menos 50 registros.")
        return

    # Procesar la columna 'Fecha de Inicio' para extraer la hora del día
    df['Hora del Día'] = pd.to_datetime(df['Fecha de Inicio']).dt.hour

    # Añadir nueva variable 'Pendiente' como la relación entre Elevación Ganada y Distancia
    df['Pendiente'] = df['Elevación Ganada (m)'] / df['Distancia (m)']
    
    # Características predictoras (sin incluir la variable a predecir: velocidad)
    X = df[['Distancia (m)', 'Elevación Ganada (m)', 'Frecuencia Cardíaca Media', 'Frecuencia Cardíaca Máxima', 'Hora del Día', 'Pendiente', 'VO2Max', 'Cadencia Media (spm)']]
    y = df['Velocidad media (m/s)']
    
    # Imputación de valores faltantes
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)

    # Escalado de características
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Calcular los mejores tiempos históricos por distancia (5K, 10K, 21K, 42K)
    mejores_tiempos = {
        "5K": df[(df['Distancia (m)'].between(4900, 5100))]['Duración (min)'].min() * 60,
        "10K": df[(df['Distancia (m)'].between(9900, 10100))]['Duración (min)'].min() * 60,
        "21K": df[(df['Distancia (m)'].between(20900, 21300))]['Duración (min)'].min() * 60,
        "42K": df[(df['Distancia (m)'].between(41900, 42100))]['Duración (min)'].min() * 60
    }

    # División de datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Modelos a entrenar
    models = {
        "RandomForest": RandomForestRegressor(),
        "GradientBoosting": GradientBoostingRegressor(),
        "XGBoost": XGBRegressor(),
        "Lasso": Lasso(alpha=0.1),
        "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5),  # Ajustar l1_ratio si es necesario
        "LightGBM": lgb.LGBMRegressor()
    }

    # Espacio de búsqueda de hiperparámetros
    param_distributions = {
        "RandomForest": {"n_estimators": [50, 100, 200], "max_depth": [10, 20, None], "min_samples_split": [2, 5, 10]},
        "GradientBoosting": {"n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.1, 0.2], "max_depth": [3, 5, 10]},
        "XGBoost": {"n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.1, 0.2], "max_depth": [3, 5, 10]},
        "Lasso": {"alpha": [0.01, 0.1, 1.0, 10]},
        "ElasticNet": {"alpha": [0.01, 0.1, 1.0], "l1_ratio": [0.2, 0.5, 0.8]},
        "LightGBM": {"n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.1, 0.2], "max_depth": [3, 5, 10]}
    }

    best_models = {}
    best_scores = {}

    # Entrenamiento de modelos
    for i, (name, model) in enumerate(models.items()):
        status_text.text(f"Entrenando modelo {name}...")
        search = RandomizedSearchCV(model, param_distributions[name], n_iter=10, cv=3, random_state=42, scoring='neg_mean_absolute_error')
        search.fit(X_train, y_train)
        best_models[name] = search.best_estimator_
        best_scores[name] = -search.best_score_
        progress_bar.progress((i + 1) / len(models))

    progress_bar.progress(1.0)
    status_text.text("Entrenamiento completado.")

    # Comparación de modelos usando el conjunto de test
    mae_df = pd.DataFrame.from_dict(best_scores, orient='index', columns=['MAE Train']).reset_index()
    mae_df.rename(columns={'index': 'Modelo'}, inplace=True)

    # Selección de los tres mejores modelos según el MAE en test
    sorted_models = sorted(best_scores.items(), key=lambda x: x[1])[:3]
    best_model_names = [model[0] for model in sorted_models]
    best_models_for_stacking = {name: best_models[name] for name in best_model_names}

    # Entrenamiento del mejor modelo individual (el que tiene el menor MAE en test)
    best_model_name = min(best_scores, key=best_scores.get)
    best_model = best_models[best_model_name]
    best_model.fit(X_train, y_train)

    # Predicción y cálculo del MAE para el mejor modelo individual en test
    y_pred_best_model = best_model.predict(X_test)
    mae_best_model = mean_absolute_error(y_test, y_pred_best_model)

    # Entrenamiento del modelo final con Stacking usando solo los tres mejores modelos
    final_model = StackingRegressor(
        estimators=[(name, best_models_for_stacking[name]) for name in best_model_names],
        final_estimator=Ridge()
    )
    final_model.fit(X_train, y_train)

    # Predicción y cálculo del MAE para el modelo final (Ensemble) en test
    y_pred_ensemble = final_model.predict(X_test)
    mae_ensemble = mean_absolute_error(y_test, y_pred_ensemble)

    # Predicción y cálculo del MAE para el modelo final (Ensemble) en train
    y_pred_ensemble_train = final_model.predict(X_train)
    mae_ensemble_train = mean_absolute_error(y_train, y_pred_ensemble_train)

    # Agregar los resultados al DataFrame para comparación
    mae_df['MAE Test'] = mae_df['Modelo'].map(lambda model_name: mean_absolute_error(y_test, best_models[model_name].predict(X_test)) if model_name in best_models else mae_ensemble)

    # Agregar el MAE del Ensemble (stacking) al DataFrame para test y train
    ensemble_name = f"Ensemble (Stacking) - Modelos: {', '.join(best_model_names)}"
    mae_df.loc[len(mae_df)] = [ensemble_name, mae_ensemble_train, mae_ensemble]  # Añadir fila del Ensemble

    # Mostrar la tabla de comparación de modelos con métricas de test
    st.write("### Comparación de Modelos")
    st.dataframe(mae_df)

    # Comparar el MAE en test de todos los modelos
    if mae_best_model < mae_ensemble:
        st.write(f"Modelo final: {best_model_name}")
        st.write(f"MAE del mejor modelo individual en test: {mae_best_model:.2f} m/s")
        final_model = best_model  # El mejor modelo individual se usa como el final
    else:
        st.write(f"Modelos usados en el Ensemble: {', '.join(best_model_names)}")
        st.write(f"MAE del Ensemble en test: {mae_ensemble:.2f} m/s")

    # Estimación de tiempos para distancias específicas
    distancias = {"42K 🏃‍♂️": 42000, "21K 🏃": 21000, "10K 🚶‍♂️": 10000, "5K 🚶": 5000}

    registros = {nombre: scaler.transform([X.mean().values]) for nombre in distancias}

    tiempos_segundos = {}
    for nombre, registro in registros.items():
        velocidad_predicha = final_model.predict(registro)[0]
        tiempo_estimado = distancias[nombre] / velocidad_predicha

        # Comparación con el mejor tiempo histórico
        mejor_tiempo_historico = mejores_tiempos.get(nombre.split()[0], tiempo_estimado)
        tiempo_final = min(tiempo_estimado, mejor_tiempo_historico)

        tiempos_segundos[nombre] = tiempo_final




    # Función para convertir segundos en horas y minutos
    def segundos_a_horas_minutos(tiempo_segundos):
        horas = int(tiempo_segundos // 3600)
        minutos = int((tiempo_segundos % 3600) // 60)
        return horas, minutos

    tiempos_formateados = {nombre: segundos_a_horas_minutos(tiempo) for nombre, tiempo in tiempos_segundos.items()}

    # Colores para los tiempos estimados
    colores_pastel = {"42K 🏃‍♂️": "#FFB3A7", "21K 🏃": "#A7C7E7", "10K 🚶‍♂️": "#B0E57C", "5K 🚶": "#FFD580"}

    st.markdown("### ⏱️ Tiempos Estimados de Carrera")
    col1, col2, col3, col4 = st.columns(4)
    
    for i, (nombre, (horas, minutos)) in enumerate(tiempos_formateados.items()):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"<div style='background-color: {colores_pastel[nombre]}; padding: 15px; border-radius: 10px; text-align: center; color: white; font-size: 20px;'>"
                        f"<strong>{nombre}</strong><br>⏳ {horas}h {minutos}m</div>", unsafe_allow_html=True)

    # Cálculo de tiempos estimados con la fórmula de Riegel para las distancias 10K, 21K y 42K
    def tiempo_riegel(tiempo_5k, distancia_5k, distancia_objetivo):
        return tiempo_5k * (distancia_objetivo / distancia_5k) ** 1.06

    tiempo_5k = tiempos_segundos["5K 🚶"]
    tiempos_riegel = {}
    for nombre, distancia in distancias.items():
        if "5K" not in nombre:  # Aplicar solo a 10K, 21K, 42K
            tiempo_riegel_estimado = tiempo_riegel(tiempo_5k, 5000, distancia)
            tiempo_riegel_final = min(tiempo_riegel_estimado, mejores_tiempos.get(nombre[:-2], tiempo_riegel_estimado))
            tiempos_riegel[nombre] = tiempo_riegel_final

    # Convertir a formato de horas y minutos
    tiempos_riegel_formateados = {nombre: segundos_a_horas_minutos(tiempo) for nombre, tiempo in tiempos_riegel.items()}

    # Mostrar los tiempos estimados de Riegel
    st.markdown("### ⏱️ Tiempos Estimados con Fórmula de Riegel")
    col1, col2, col3 = st.columns(3)
    
    for i, (nombre, (horas, minutos)) in enumerate(tiempos_riegel_formateados.items()):
        with [col1, col2, col3][i]:
            st.markdown(f"<div style='background-color: {colores_pastel[nombre]}; padding: 15px; border-radius: 10px; text-align: center; color: white; font-size: 20px;'>"
                        f"<strong>{nombre}</strong><br>⏳ {horas}h {minutos}m</div>", unsafe_allow_html=True)

# Función de la página de predicciones
def predicciones_page():
    st.title("Predicciones de carrera")
    try:
        df = load_data()
        if df is not None:
            expander1 = st.expander("Despliega para ver la tabla de datos")
            expander1.dataframe(df)
            prediction(df)
        else:
            st.warning("No se han encontrado datos. Por favor, descarga los datos en la página de inicio.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
