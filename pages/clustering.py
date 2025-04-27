import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px


def run(df: pd.DataFrame):
    """
    Кластеризация маршрутов по средней загрузке:
    • Низкая, Средняя, Высокая загрузка

    Помогает:
    - Определить маршруты для стимулирования (низкая)
    - Выделить «локомотивы» (средняя)
    - Анализировать перегруз (высокая)
    """
    st.header("🗂 Кластеризация маршрутов по средней загрузке")
    st.markdown(
        """
        Автоматическое разделение маршрутов на три группы:
        - **Низкая загрузка**: требует маркетинга.  
        - **Средняя загрузка**: стабильные кластеры.  
        - **Высокая загрузка**: возможны дополнительные рейсы.
        """
    )

    # Средняя загрузка по рейсам
    agg = df.groupby("flight_no")["passengers"].mean().reset_index()
    scaler = StandardScaler()
    x = scaler.fit_transform(agg[["passengers"]])

    # 3 кластера
    kmeans = KMeans(n_clusters=3, random_state=42)
    agg["cluster"] = kmeans.fit_predict(x)

    # Центры
    centers = scaler.inverse_transform(kmeans.cluster_centers_).flatten()
    order = centers.argsort()
    labels = {
        order[0]: "Низкая загрузка",
        order[1]: "Средняя загрузка",
        order[2]: "Высокая загрузка",
    }
    agg["cluster_label"] = agg["cluster"].map(labels)

    # Визуализация
    fig = px.scatter(
        agg, x="flight_no", y="passengers",
        color="cluster_label",
        title="Маршруты по уровню загрузки",
        labels={"cluster_label": "Группа", "passengers": "Средняя загрузка"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Печатаем центры кластера
    st.markdown("**Средние значения загрузки по группам:**")
    for i, c in enumerate(centers):
        st.write(f"- **{labels[i]}**: {c:.1f} пассажиров")

    st.markdown(
        """
        **Рекомендации**:  
        1. Маркетируйте маршруты из группы «Низкая загрузка».  
        2. Удерживайте "средние" кластеры стабильными.  
        3. Рассмотрите добавление рейсов для «Высокой загрузки».
        """
    )