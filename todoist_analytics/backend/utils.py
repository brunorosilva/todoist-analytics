import numpy as np
import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame

from .data_collector import DataCollector


def preprocess(dc: DataCollector) -> pd.DataFrame:
    df_full = dc.items
    print(df_full.shape)

    df_full['datehour_completed'] = pd.to_datetime(df_full['completed_date'])
    df_full['datehour_completed'] = pd.DatetimeIndex(
        df_full['datehour_completed']).tz_convert('America/Sao_Paulo')
    df_full['completed_date'] = pd.to_datetime(
        df_full['datehour_completed']).dt.date
    df_full['completed_date_weekday'] = pd.to_datetime(
        df_full['datehour_completed']).dt.day_name()

    return df_full


@st.cache
def get_data(token):
    dc = DataCollector(token)
    dc.collect_all()
    completed_tasks = preprocess(dc)

    return completed_tasks
