import pandas as pd
import glob
import zipfile
import urllib.request
import os
import streamlit as st

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file:
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                zip_ref.extractall("data_custom")
            files = glob.glob("data_custom/**/*.csv", recursive=True)
        elif uploaded_file.name.endswith('.csv'):
            files = [uploaded_file]
        else:
            st.error("Поддерживаются только файлы .zip или .csv")
            return pd.DataFrame()
    else:
        url = "https://drive.google.com/uc?id=1kXz-DCE2jgKuAfyvlAtri0fOYvRdz1J_&export=download"
        zip_path = "data.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("data")
        files = glob.glob("data/**/*.csv", recursive=True)

    dfs = []
    for f in files:
        try:
            if isinstance(f, str):
                df = pd.read_csv(f, sep=";", encoding="cp1251")
            else:
                df = pd.read_csv(f, sep=";", encoding="cp1251")
        except Exception as e:
            st.warning(f"Не удалось загрузить файл {f}: {e}")
            continue

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df["passengers"] = pd.to_numeric(df.get("Кол-во пасс.", 0), errors="coerce").fillna(0).astype(int)
        df["contract_short"] = df["№ договора"].fillna("Без договора").str.extract(r'([^\\s]+)').fillna("Без договора")
        df = df.rename(columns={"Код а/к": "airline", "Код а/п": "airport", "Номер рейса": "flight_no"})
        df["dep_date"] = pd.to_datetime(df.get("Дата вылета"), dayfirst=True, errors="coerce")
        dfs.append(df)

    if not dfs:
        st.error("Не найдено CSV-файлов для загрузки!")
        return pd.DataFrame()

    all_data = pd.concat(dfs, ignore_index=True)
    return all_data