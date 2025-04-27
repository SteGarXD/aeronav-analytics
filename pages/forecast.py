import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly
from utils.data_loader import load_data

st.title("Прогноз пассажиропотока на 6 месяцев")

df = load_data()

if df is not None and not df.empty:
    df_monthly = df.groupby(df['dep_date'].dt.to_period('M'))['passengers'].sum().reset_index()
    df_monthly['ds'] = df_monthly['dep_date'].dt.to_timestamp()
    df_monthly['y'] = df_monthly['passengers']

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(df_monthly[['ds', 'y']])

    future = model.make_future_dataframe(periods=6, freq='M')
    forecast = model.predict(future)

    st.subheader("График прогноза пассажиропотока")
    fig = plot_plotly(model, forecast)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Компоненты прогноза")
    components_fig = model.plot_components(forecast)
    st.pyplot(components_fig)

    st.subheader("Таблица прогноза на ближайшие 6 месяцев")
    future_data = forecast[['ds', 'yhat']].tail(6)
    future_data.columns = ["Месяц", "Прогноз пассажиров"]
    future_data["Месяц"] = future_data["Месяц"].dt.strftime("%B %Y")
    st.dataframe(future_data.style.format({"Прогноз пассажиров": "{:,.0f}"}))

    st.markdown(
        """
        **Интерпретация:**
        - Рост графика указывает на увеличение пассажиропотока.
        - Спад может говорить о сезонных колебаниях.
        - Выявление трендов помогает планировать загрузку рейсов и маркетинговые активности.
        """
    )
else:
    st.error("Данные для построения прогноза отсутствуют.")