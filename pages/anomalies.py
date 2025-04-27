import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

st.title("Обнаружение аномалий в пассажиропотоке")


df = load_data()

if df is not None and not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(
            "Дата начала", value=df['dep_date'].min(), key="anom_start"
        )
    with col2:
        end = st.date_input(
            "Дата окончания", value=df['dep_date'].max(), key="anom_end"
        )

    df['dep_date'] = pd.to_datetime(df['dep_date'], errors='coerce')
    mask = (df['dep_date'] >= pd.to_datetime(start)) & (df['dep_date'] <= pd.to_datetime(end))
    df_filt = df.loc[mask]

    if df_filt.empty:
        st.warning("Нет данных в выбранном диапазоне.")
    else:
        mean_p = df_filt['passengers'].mean()
        std_p = df_filt['passengers'].std()
        threshold = mean_p + 3 * std_p

        iso = IsolationForest(contamination=0.01, random_state=42)
        df_filt['iso_anomaly'] = iso.fit_predict(df_filt[['passengers']]) == -1

        lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01)
        df_filt['lof_anomaly'] = lof.fit_predict(df_filt[['passengers']]) == -1

        tabs = st.tabs(["Порог", "IsolationForest", "LocalOutlierFactor"])

        with tabs[0]:
            st.subheader("Аномалии по пороговому правилу")
            fig_thr = px.scatter(
                df_filt, x='dep_date', y='passengers', color=df_filt['passengers'] > threshold,
                color_discrete_map={True: '#ff7f0e', False: '#1f77b4'},
                labels={
                    'dep_date': 'Дата',
                    'passengers': 'Пассажиров',
                    'color': 'Аномалия'
                },
                title=f"Аномалии (порог > {int(threshold)} пассажиров)"
            )
            st.plotly_chart(fig_thr, use_container_width=True)
            st.dataframe(
                df_filt[df_filt['passengers'] > threshold][['flight_no', 'dep_date', 'passengers']]
                .rename(columns={'flight_no': 'Рейс', 'dep_date': 'Дата', 'passengers': 'Пассажиров'})
                .reset_index(drop=True)
            )

        with tabs[1]:
            st.subheader("Аномалии IsolationForest")
            fig_iso = px.scatter(
                df_filt, x='dep_date', y='passengers', color='iso_anomaly',
                color_discrete_map={True: '#ff7f0e', False: '#1f77b4'},
                labels={'iso_anomaly': 'Аномалия', 'dep_date': 'Дата', 'passengers': 'Пассажиров'},
                title="IsolationForest: аномальные рейсы"
            )
            st.plotly_chart(fig_iso, use_container_width=True)
            st.dataframe(
                df_filt[df_filt['iso_anomaly']][['flight_no', 'dep_date', 'passengers']]
                .rename(columns={'flight_no': 'Рейс', 'dep_date': 'Дата', 'passengers': 'Пассажиров'})
                .reset_index(drop=True)
            )

        with tabs[2]:
            st.subheader("Аномалии LocalOutlierFactor")
            fig_lof = px.scatter(
                df_filt, x='dep_date', y='passengers', color='lof_anomaly',
                color_discrete_map={True: '#ff7f0e', False: '#1f77b4'},
                labels={'lof_anomaly': 'Аномалия', 'dep_date': 'Дата', 'passengers': 'Пассажиров'},
                title="LocalOutlierFactor: аномальные рейсы"
            )
            st.plotly_chart(fig_lof, use_container_width=True)
            st.dataframe(
                df_filt[df_filt['lof_anomaly']][['flight_no', 'dep_date', 'passengers']]
                .rename(columns={'flight_no': 'Рейс', 'dep_date': 'Дата', 'passengers': 'Пассажиров'})
                .reset_index(drop=True)
            )
else:
    st.error("Не удалось загрузить данные.")