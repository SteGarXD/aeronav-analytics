import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from utils.data_loader import load_data

st.title("Кластеризация маршрутов по средней загрузке")

df = load_data()

if df is not None and not df.empty:
    agg_data = df.groupby('flight_no')['passengers'].mean().reset_index()
    agg_data = agg_data.dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(agg_data[['passengers']])

    kmeans = KMeans(n_clusters=3, random_state=42)
    agg_data['cluster'] = kmeans.fit_predict(X_scaled)

    centers = scaler.inverse_transform(kmeans.cluster_centers_).flatten()
    order = centers.argsort()
    labels_map = {
        order[0]: "Низкая загрузка",
        order[1]: "Средняя загрузка",
        order[2]: "Высокая загрузка"
    }
    agg_data['cluster_label'] = agg_data['cluster'].map(labels_map)

    st.subheader("Распределение маршрутов по кластерам")
    fig = px.scatter(
        agg_data,
        x='flight_no',
        y='passengers',
        color='cluster_label',
        labels={'passengers': 'Среднее число пассажиров', 'flight_no': 'Рейс', 'cluster_label': 'Тип кластера'},
        title="Кластеризация рейсов по средней загрузке"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Описание кластеров")
    for idx, center in enumerate(centers[order]):
        st.markdown(f"- **{labels_map[idx]}**: среднее количество пассажиров — **{center:.0f}**")

    st.markdown(
        """
        **Что это даёт:**
        - Понимание, какие рейсы требуют маркетингового продвижения (низкая загрузка).
        - Выявление стабильных маршрутов (средняя загрузка).
        - Определение самых прибыльных направлений (высокая загрузка).
        """
    )
else:
    st.error("Данные для кластеризации отсутствуют.")