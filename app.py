import streamlit as st
from utils.data_loader import load_data
from pages import main_charts, additional_analytics, forecast, clustering, anomalies

st.set_page_config(
    page_title="Анализ данных системы отправки рейсов",
    page_icon="assets/logo.png",
    layout="wide"
)

st.sidebar.title("Навигация по разделам")
section = st.sidebar.radio(
    "Выберите раздел:",
    [
        "Основные диаграммы",
        "Дополнительная аналитика",
        "Прогноз пассажиропотока",
        "Кластеры маршрутов",
        "Аномалии пассажиропотока"
    ]
)

uploaded_file = st.sidebar.file_uploader("Загрузите файл .zip или .csv", type=["zip", "csv"])
df = load_data(uploaded_file)

if section == "Основные диаграммы":
    main_charts.render(df)
elif section == "Дополнительная аналитика":
    additional_analytics.render(df)
elif section == "Прогноз пассажиропотока":
    forecast.render(df)
elif section == "Кластеры маршрутов":
    clustering.render(df)
elif section == "Аномалии пассажиропотока":
    anomalies.render(df)