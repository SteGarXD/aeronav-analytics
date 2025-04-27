import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

def forecast_passengers(df):
    hist = df.groupby(df.dep_date.dt.to_period('M'))['passengers'].sum().reset_index()
    hist['ds'] = hist.dep_date.dt.to_timestamp()
    hist['y'] = hist.passengers

    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(hist[['ds', 'y']])

    future = m.make_future_dataframe(periods=6, freq='M')
    forecast = m.predict(future)

    fig_forecast = Prophet.plot_plotly(m, forecast)

    return forecast, fig_forecast, m

def cluster_routes(df):
    agg = df.groupby('flight_no')['passengers'].mean().reset_index()

    scaler = StandardScaler()
    X = scaler.fit_transform(agg[['passengers']])

    kmeans = KMeans(n_clusters=3, random_state=42)
    agg['cluster'] = kmeans.fit_predict(X)

    centers = scaler.inverse_transform(kmeans.cluster_centers_).flatten()

    order = centers.argsort()
    labels = {
        order[0]: "Низкая загрузка",
        order[1]: "Средняя загрузка",
        order[2]: "Высокая загрузка"
    }
    agg['cluster_label'] = agg['cluster'].map(labels)

    fig = px.scatter(
        agg,
        x='flight_no',
        y='passengers',
        color='cluster_label',
        title="Кластеризация маршрутов по средней загрузке",
        labels={"flight_no": "Рейс", "passengers": "Среднее число пассажиров", "cluster_label": "Кластер"}
    )

    return agg, fig, centers, labels

def detect_anomalies(df):
    X = df[['passengers']].values

    mean_p = df['passengers'].mean()
    std_p = df['passengers'].std()
    threshold = mean_p + 3 * std_p
    df['threshold_anomaly'] = df['passengers'] > threshold

    iso = IsolationForest(contamination=0.01, random_state=42)
    df['iso_label'] = iso.fit_predict(X)
    df['iso_anomaly'] = df['iso_label'] == -1

    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01)
    df['lof_label'] = lof.fit_predict(X)
    df['lof_anomaly'] = df['lof_label'] == -1

    return df, threshold