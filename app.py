import streamlit as st
from utils import load_data
from pages.main_charts import run as show_main_charts
from pages.additional_analytics import run as show_additional
from pages.forecast import run as show_forecast
from pages.clustering import run as show_clustering
from pages.anomalies import run as show_anomalies
from PIL import Image

# ——— Настройка страницы ——————————————————————————————————————————————————
logo = Image.open('7038fb25-82d5-478f-9b43-a19ac46cb9ed.png')
st.set_page_config(
    page_title="Анализ данных системы отправки рейсов",
    page_icon=logo,
    layout="wide",
)

# Краткое вводное для руководства:
st.title("Анализ данных системы отправки рейсов")
st.markdown(
    """
    Добро пожаловать в интерактивный отчёт по всем ключевым показателям перевозки пассажиров:
    - **Основные диаграммы** помогут увидеть текущих лидеров по авиакомпаниям, направлениям и договорам.
    - **Дополнительная аналитика** даст углублённое представление по месяцам, загрузке и пиковым дням.
    - **Прогноз** на 6 месяцев позволит планировать ресурсы и бюджет заранее.
    - **Кластеры** покажут, какие маршруты недоиспользованы, а какие перегружены.
    - **Аномалии** выявят резкие выбросы, которые могут сигнализировать о форс-мажоре или ошибках.

    _Цель отчёта — снижение операционных издержек, оптимизация загрузки флота и повышение качества сервиса._  
    """
)

# ——— Загрузка данных ——————————————————————————————————————————————————
st.sidebar.header("🔄 Загрузка данных")
uploaded = st.sidebar.file_uploader(
    "Загрузите ZIP (архив CSV) или одиночный CSV-файл",
    type=["zip", "csv"]
)
df = load_data(uploaded)

if df.empty:
    st.sidebar.error("Нет данных — пожалуйста, загрузите файл!")
    st.stop()

# ——— Навигация по разделам ——————————————————————————————————————————————
section = st.sidebar.radio(
    "Выберите раздел отчёта",
    (
        "Основные диаграммы",
        "Дополнительная аналитика",
        "Прогноз",
        "Кластеры",
        "Аномалии",
    ),
)

# ——— Маршрутизация ——————————————————————————————————————————————————
if section == "Основные диаграммы":
    show_main_charts(df)
elif section == "Дополнительная аналитика":
    show_additional(df)
elif section == "Прогноз":
    show_forecast(df)
elif section == "Кластеры":
    show_clustering(df)
elif section == "Аномалии":
    show_anomalies(df)