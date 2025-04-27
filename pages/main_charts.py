import streamlit as st
from utils.data_loader import load_data
from utils.charts import render_chart

st.title("Основные диаграммы: Анализ системы отправки рейсов")

df = load_data()

if df is not None and not df.empty:
    charts = [
        ("Топ‑5 авиакомпаний", "airline", "bar"),
        ("Топ‑5 направлений", "flight_no", "bar"),
        ("Топ‑5 аэропортов", "airport", "bar"),
        ("Договоры (круговая диаграмма)", "contract_short", "pie"),
        ("Договоры (столбчатая диаграмма)", "contract_short", "bar"),
    ]

    for i, (title, column, kind) in enumerate(charts):
        st.subheader(title)

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Дата начала",
                value=df["dep_date"].min(),
                key=f"start_date_main_{i}"
            )

        with col2:
            end_date = st.date_input(
                "Дата окончания",
                value=df["dep_date"].max(),
                key=f"end_date_main_{i}"
            )

        mask = (df['dep_date'] >= pd.to_datetime(start_date)) & (df['dep_date'] <= pd.to_datetime(end_date))
        df_filtered = df.loc[mask]

        st.plotly_chart(render_chart(df_filtered, column, title, kind=kind, showlegend=(kind == "pie")), use_container_width=True)
else:
    st.error("Не удалось загрузить данные.")