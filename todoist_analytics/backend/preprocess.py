from pandas.core.frame import DataFrame
from .data_collector import DataCollector
import pandas as pd
import numpy as np


def preprocess(dc: DataCollector) -> pd.DataFrame:
    df_full = dc.items

    df_full['datehour_completed'] = pd.to_datetime(df_full['completed_date'])
    df_full['datehour_completed'] = pd.DatetimeIndex(
        df_full['datehour_completed']).tz_convert('America/Sao_Paulo')
    df_full['completed_date'] = pd.to_datetime(
        df_full['datehour_completed']).dt.date
    df_full['completed_date_weekday'] = pd.to_datetime(
        df_full['datehour_completed']).dt.day_name()

    return df_full
