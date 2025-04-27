import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly

def run(df: pd.DataFrame):
    """
    Прогноз пассажиропотока на 6 месяцев вперёд с помощью Prophet.

    Даст вам:
    - Тренд и сезонность
    - Таблицу с месячным прогнозом
    - Интерпретации для бизнеса
    """
    st.header("🔮 Прогноз пассажиропотока на 6 месяцев")
    st.markdown(
        """
        Прогноз позволяет заранее распределить:
        - Закупку топлива и наземные ресурсы  
        - Графики работы экипажа  
        - Маркетинговые акции в низкие сезоны  
        """
    )

    # Подготовка исторических данных по месяцам
    hist = df.groupby(df.dep_date.dt.to_period("M"))["passengers"] \
        .sum().reset_index(name="y")
    hist["ds"] = hist.dep_date.dt.to_timestamp()

    # Обучаем модель
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(hist[["ds", "y"]])

    # Будущее на 6 месяцев
    future = m.make_future_dataframe(periods=6, freq="M")
    forecast = m.predict(future)

    # График
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1, use_container_width=True)

    # Компоненты (тренд + сезонность)
    comp = m.plot_components(forecast)
    st.pyplot(comp)

    # Таблица прогноза
    next6 = (forecast[["ds", "yhat"]]
             .tail(6)
             .rename(columns={"ds": "Месяц", "yhat": "Прогноз пассажиров"})
             )
    # Обрезаем всё, что ниже нуля, а потом округляем и переводим в int
    next6["Прогноз пассажиров"] = (
        next6["Прогноз пассажиров"]
        .clip(lower=0)
        .round(0)
        .astype(int)
    )
    st.markdown("**Прогноз по месяцам (неотрицательный):**")
    st.dataframe(next6.set_index("Месяц"))

    st.markdown(
        """
        **Как применять**:  
        - Сравните прогноз с прошлогодними результатами, чтобы скорректировать планы.  
        - Используйте тренд для долговременных стратегий.  
        - Сезонность поможет планировать рекламные кампании заранее.
        """
    )