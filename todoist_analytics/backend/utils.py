import numpy as np
import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame

from todoist_analytics.backend.data_collector import DataCollector




def create_color_palette(completed_tasks: DataFrame):
    project_id_color = pd.Series(
        completed_tasks.hex_color.values, index=completed_tasks.project_name
    ).to_dict()
    return project_id_color


class Singleton:
    _instance = None
    def __init__(self):
        self.n_calls = 1
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


@st.experimental_singleton
def get_n_calls():
    return Singleton()


@st.cache(
    show_spinner=False
)  # caching the data and hiding the spinner warning
def get_data(token):
    dc = DataCollector(token)
    dc._collect_all_completed_tasks()
    dc._collect_active_tasks()
    active_tasks = dc.active_tasks
    completed_tasks = dc.items
    sing = get_n_calls()
    sing.n_calls += 1
    print("get data ran")
    return completed_tasks, active_tasks, dc

@st.cache(
    show_spinner=False
)  # caching the data and hiding the spinner warning
def get_more_data(dc, n_calls):
    limit = 2000 * n_calls
    dc._collect_all_completed_tasks(limit=limit)
    dc._collect_active_tasks()
    active_tasks = dc.active_tasks
    completed_tasks = dc.items
    return completed_tasks, active_tasks


def safe_divide(n, d):
    if d == 0:
        return 0
    else:
        return n / d
