import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def run(df: pd.DataFrame):
    """
    Обнаружение аномалий:
    • Пороговое (mean + 3·std)
    • IsolationForest
    • LocalOutlierFactor

    Помогает:
    - Мгновенно увидеть выбросыD
    - Выявить неожиданные всплески или провалы
    """
    st.header("⚠️ Обнаружение аномалий в пассажиропотоке")
    st.markdown(
        """
        Разные методы показывают:
        - Критические выбросы по простому порогу  
        - Автоматические «странные точки» через IsolationForest и LOF  
        - Результаты можно сверить и выбрать надёжнее
        """
    )

    # Простое пороговое значение
    mean_p = df.passengers.mean()
    std_p = df.passengers.std()
    threshold = mean_p + 3 * std_p
    st.markdown(f"**Порог выбросов (mean + 3·std):** {threshold:.0f} пассажиров")

    df["threshold_anomaly"] = df.passengers > threshold

    # IsolationForest
    iso = IsolationForest(contamination=0.01, random_state=42)
    df["iso_label"] = iso.fit_predict(df[["passengers"]])
    df["iso_anomaly"] = df.iso_label == -1

    # LocalOutlierFactor
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01)
    df["lof_label"] = lof.fit_predict(df[["passengers"]])
    df["lof_anomaly"] = df.lof_label == -1

    tabs = st.tabs(["По порогу", "IsolationForest", "LocalOutlierFactor"])

    # По порогу
    with tabs[0]:
        an = df[df.threshold_anomaly]
        fig0 = px.scatter(
            an, x="dep_date", y="passengers", color="flight_no",
            title="Аномалии: порог (> mean+3·std)"
        )
        st.plotly_chart(fig0, use_container_width=True)
        st.dataframe(
            an[["flight_no", "dep_date", "passengers"]]
            .rename(columns={
                "flight_no": "Рейс",
                "dep_date": "Дата",
                "passengers": "Пассажиров"
            }).reset_index(drop=True)
        )

    # IsolationForest
    with tabs[1]:
        an_iso = df[df.iso_anomaly]
        fig1 = px.scatter(
            an_iso, x="dep_date", y="passengers", color="flight_no",
            title="Аномалии: IsolationForest"
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(
            an_iso[["flight_no", "dep_date", "passengers"]]
            .rename(columns={"flight_no": "Рейс", "dep_date": "Дата", "passengers": "Пассажиров"})
            .reset_index(drop=True)
        )

    # LOF
    with tabs[2]:
        an_lof = df[df.lof_anomaly]
        fig2 = px.scatter(
            an_lof, x="dep_date", y="passengers", color="flight_no",
            title="Аномалии: LocalOutlierFactor"
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(
            an_lof[["flight_no", "dep_date", "passengers"]]
            .rename(columns={"flight_no": "Рейс", "dep_date": "Дата", "passengers": "Пассажиров"})
            .reset_index(drop=True)
        )

    st.markdown(
        """
        **Как это использовать**:  
        - Сверяйте списки аномалий между методами.  
        - Ищите форс-мажор на пике (поток > 3·σ).  
        - Отлавливайте ошибки в учёте или внезапные события.
        """
    )