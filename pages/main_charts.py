import streamlit as st
import pandas as pd
import plotly.express as px


def run(df: pd.DataFrame):
    """
    Раздел «Основные диаграммы»:
    - Топ-5 авиакомпаний
    - Топ-5 направлений (рейсов)
    - Топ-5 аэропортов
    - Договоры (круговая и столбчатая диаграмма)

    Помогает быстро определить:
    • Где мы зарабатываем больше всего пассажиров.
    • По каким договорам (или без договора) лётные программы наиболее крупные.
    """
    st.header("Анализ данных системы отправки рейсов")
    st.markdown(
        """
        В этом разделе вы видите пять лидеров по основным бизнес-метрикам:
        - 🛫 авиакомпании с наибольшим пассажиропотоком  
        - 🌐 самые популярные направления  
        - 🏁 аэропорты с наибольшим пассажиропотоком  
        - 📄 распределение по договорным партнёрам  

        Выбор дат позволяет оценить динамику за любой период.
        """
    )

    # Настройка дат
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Дата начала", df["dep_date"].min(), key="mc_start")
    with c2:
        end = st.date_input("Дата окончания", df["dep_date"].max(), key="mc_end")

    mask = (df["dep_date"] >= pd.to_datetime(start)) & (df["dep_date"] <= pd.to_datetime(end))
    df_f = df.loc[mask]

    if df_f.empty:
        st.warning("Нет данных за выбранный период")
        return

    charts = [
        ("Топ-5 авиакомпаний", "airline", "bar"),
        ("Топ-5 направлений", "flight_no", "bar"),
        ("Топ-5 аэропортов", "airport", "bar"),
        ("Договоры: круговая", "contract_short", "pie"),
        ("Договоры: столбчатая", "contract_short", "bar"),
    ]

    for title, col, kind in charts:
        st.subheader(title)
        # агрегируем
        agg = df_f.groupby(col)["passengers"].sum().reset_index(name="value")
        top5 = agg.nlargest(5, "value")
        if kind == "pie":
            fig = px.pie(
                top5, names=col, values="value", hole=0.3,
                title=title,
                labels={col: title, "value": "Пассажиры"}
            )
        else:
            fig = px.bar(
                top5, x="value", y=col, orientation="h",
                title=title,
                labels={"value": "Пассажиры", col: title}
            )
        st.plotly_chart(fig, use_container_width=True)