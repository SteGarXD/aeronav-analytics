import pandas as pd
import glob, zipfile, urllib.request
import streamlit as st


@st.cache_data
def load_data(uploaded_file=None):
    """
    Загружает данные из:
    - загруженного ZIP/CSV-файла
    - если файл не загружен — стягивает образец из Google Drive

    Возвращает объединённый DataFrame с колонками:
    flight_no, dep_date (datetime), airline, airport, passengers, contract_short
    """
    # 1) Если пользователь загрузил ZIP или CSV — распакуем/прочитаем:
    if uploaded_file:
        # ZIP?
        if uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(uploaded_file, "r") as Z:
                Z.extractall("data_custom")
            paths = glob.glob("data_custom/**/*.csv", recursive=True)
        else:
            # Одиночный CSV
            paths = [uploaded_file]
    else:
        # иначе стягиваем демонстрационный архив
        url = "https://drive.google.com/uc?id=1kXz-DCE2jgKuAfyvlAtri0fOYvRdz1J_&export=download"
        zip_path = "sample_data.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as Z:
            Z.extractall("data")
        paths = glob.glob("data/**/*.csv", recursive=True)

    dfs = []
    for p in paths:
        df0 = pd.read_csv(p, sep=";", encoding="cp1251")
        # бросаем «Unnamed»
        df0 = df0.loc[:, ~df0.columns.str.contains("^Unnamed")]
        # приводим пассажиров к числу
        df0["passengers"] = pd.to_numeric(df0["Кол-во пасс."], errors="coerce").fillna(0).astype(int)
        # сокращаем договоры до первого слова
        df0["contract_short"] = df0["№ договора"].fillna("Без договора") \
            .str.extract(r"([^\\s]+)")[0] \
            .fillna("Без договора")
        # переименовываем для удобства
        df0 = df0.rename(columns={
            "Код а/к": "airline",
            "Код а/п": "airport",
            "Номер рейса": "flight_no",
            "Дата вылета": "dep_date"
        })
        # datetime
        df0["dep_date"] = pd.to_datetime(df0["dep_date"], dayfirst=True, errors="coerce")
        dfs.append(df0[["flight_no", "dep_date", "airline", "airport", "passengers", "contract_short"]])

    if not dfs:
        return pd.DataFrame()  # пусто — сигнал

    # склеим всё в один DataFrame
    full = pd.concat(dfs, ignore_index=True)
    return full