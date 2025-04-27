import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


def run(df: pd.DataFrame):
    """
    Дополнительная аналитика:
    • Динамика числа рейсов и пассажиров по месяцам
    • Распределение средней загрузки рейсов
    • Тепловая карта «месяц–день недели»

    Помогает понять:
    - Где «проседает» обслуживание в низкий сезон
    - Когда критические дни для планирования ресурсов
    - Насколько равномерно загружены маршруты
    """
    st.header("📊 Дополнительная аналитика рейсов")
    st.markdown(
        """
        Здесь вы найдёте углубленный разбор:
        1. **Количество рейсов по месяцам** — когда наибольшая активность и когда спад.  
        2. **Пассажиропоток по месяцам** — где концентрируется основной доход.  
        3. **Гистограмма средней загрузки** — выявляем слишком маленькие и чересчур большие рейсы.  
        4. **Тепловая карта** «месяц vs день недели» — для оптимального распределения экипажей и наземных служб.
        """
    )

    # Выбор периода одним разом
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Дата начала отчёта", df.dep_date.min(), key="aa_start")
    with c2:
        end = st.date_input("Дата окончания отчёта", df.dep_date.max(), key="aa_end")

    df_f = df[(df.dep_date >= pd.to_datetime(start)) & (df.dep_date <= pd.to_datetime(end))]
    if df_f.empty:
        st.warning("Нет данных за выбранный период")
        return

    # 1) Рейсы по месяцам
    with st.expander("1. Количество уникальных рейсов по месяцам", expanded=True):
        df_f["month"] = df_f.dep_date.dt.to_period("M").astype(str)
        flights = df_f.groupby("month")["flight_no"].nunique().reset_index(name="count")
        fig1 = px.line(
            flights, x="month", y="count", markers=True,
            title="🛫 Число рейсов в месяц",
            labels={"month": "Месяц", "count": "Уникальных рейсов"}
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown(
            "🔍 **Пояснение:** пики показывают, когда нужна максимальная загрузка флота и экипажа. "
            "Падения — время для профилактики и обучения персонала."
        )

    # 2) Пассажиропоток по месяцам
    with st.expander("2. Пассажиры по месяцам", expanded=False):
        df_f["month"] = df_f.dep_date.dt.to_period("M").astype(str)
        pax = df_f.groupby("month")["passengers"].sum().reset_index()
        fig2 = px.line(
            pax, x="month", y="passengers", markers=True,
            title="👥 Пассажиропоток в месяц",
            labels={"month": "Месяц", "passengers": "Пассажиров"}
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(
            "🔍 **Пояснение:** по месяцам видно, где основные доходы. "
            "Позволяет строить маркетинговые планы и менять цены."
        )

    # 3) Средняя загрузка рейсов
    with st.expander("3. Распределение средней загрузки рейсов", expanded=False):
        avg = df_f.groupby("flight_no")["passengers"].mean().reset_index()
        avg = avg[avg.passengers > 0]
        fig3 = px.histogram(
            avg, x="passengers", nbins=20,
            title="📈 Средняя загрузка по рейсам",
            labels={"passengers": "Среднее число пассажиров"}
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown(
            "🔍 **Пояснение:** чем шире распределение — тем больше нерегулярные маршруты. "
            "Варианты: либо отказаться от нерентабельных, либо стимулировать их promos."
        )

    # 4) Тепловая карта «месяц-день недели»
    with st.expander("4. Тепловая карта «месяц / день недели»", expanded=False):
        df_f["month_num"] = df_f.dep_date.dt.month
        df_f["dow"] = df_f.dep_date.dt.dayofweek
        month_map = {
            i: m for i, m in enumerate(
                ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'], 1)
        }
        day_map = {
            i: d for i, d in enumerate(
                ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'])
        }
        df_f['Месяц'] = df_f.month_num.map(month_map)
        df_f['День недели'] = df_f.dow.map(day_map)

        heat = df_f.groupby(['Месяц', 'День недели']).size().unstack(fill_value=0)
        # рисуем
        fig4, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(
            heat, cmap="YlOrRd", annot=True, fmt="d", linewidths=.5, ax=ax
        )
        ax.set_xlabel("День недели")
        ax.set_ylabel("Месяц")
        st.pyplot(fig4)
        st.markdown(
            "🔍 **Пояснение:** горячие зоны — дни пиковых нагрузок. "
            "Полезно для планирования расписаний и смен на земле."
        )