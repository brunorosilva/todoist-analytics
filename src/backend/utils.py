import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame

from src.backend.data_collector import DataCollector


def create_color_palette(completed_tasks: DataFrame):
    project_id_color = pd.Series(
        completed_tasks.hex_color.values, index=completed_tasks.project_name
    ).to_dict()
    return project_id_color


@st.cache(show_spinner=False)  # caching the data and hiding the spinner warning
def get_data(token):
    dc = DataCollector(token)
    active_tasks = dc.active_tasks
    completed_tasks = dc.items
    return completed_tasks, active_tasks


def safe_divide(n, d):
    if d == 0:
        return 0
    else:
        return n / d