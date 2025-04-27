import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from utils.data_loader import load_data

st.title("Дополнительная аналитика по рейсам")

df = load_data()

if df is not None and not df.empty:
    analytics = [
        ("Рейсы по месяцам", "flight_no", "flights"),
        ("Пассажиры по месяцам", "passengers", "passengers"),
        ("Средняя загрузка рейсов", "avg_passengers", "avg_passengers"),
        ("Тепловая карта количества рейсов", "heatmap", "heatmap"),
    ]

    for idx, (title, ylabel, key) in enumerate(analytics):
        with st.expander(title, expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input(
                    "Дата начала",
                    value=df["dep_date"].min(),
                    key=f"start_date_add_{key}"
                )

            with col2:
                end_date = st.date_input(
                    "Дата окончания",
                    value=df["dep_date"].max(),
                    key=f"end_date_add_{key}"
                )

            mask = (df['dep_date'] >= pd.to_datetime(start_date)) & (df['dep_date'] <= pd.to_datetime(end_date))
            df_filtered = df.loc[mask]

            if key == "flights":
                df_filtered["month"] = df_filtered['dep_date'].dt.to_period("M").astype(str)
                data = df_filtered.groupby("month")["flight_no"].nunique().reset_index()
                fig = px.line(data, x="month", y="flight_no", markers=True, title=title)
                st.plotly_chart(fig, use_container_width=True)

            elif key == "passengers":
                df_filtered["month"] = df_filtered['dep_date'].dt.to_period("M").astype(str)
                data = df_filtered.groupby("month")["passengers"].sum().reset_index()
                fig = px.line(data, x="month", y="passengers", markers=True, title=title)
                st.plotly_chart(fig, use_container_width=True)

            elif key == "avg_passengers":
                data = df_filtered.groupby("flight_no")["passengers"].mean().reset_index()
                fig = px.histogram(data, x="passengers", nbins=20, title=title)
                st.plotly_chart(fig, use_container_width=True)

            elif key == "heatmap":
                df_filtered["month_num"] = df_filtered['dep_date'].dt.month
                df_filtered["dow"] = df_filtered['dep_date'].dt.dayofweek

                month_map = {
                    i: m for i, m in enumerate([
                        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
                    ], 1)
                }
                day_map = {
                    i: d for i, d in enumerate([
                        'Понедельник', 'Вторник', 'Среда', 'Четверг',
                        'Пятница', 'Суббота', 'Воскресенье'
                    ])
                }

                df_filtered["Месяц"] = df_filtered["month_num"].map(month_map)
                df_filtered["День недели"] = df_filtered["dow"].map(day_map)

                heatmap_data = df_filtered.groupby(["Месяц", "День недели"]).size().unstack(fill_value=0)

                fig, ax = plt.subplots(figsize=(12, 6))
                sns.heatmap(heatmap_data, cmap="YlOrRd", annot=True, fmt="d",_