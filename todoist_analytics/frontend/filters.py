import numpy as np
import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame


def date_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    date_filter = st.sidebar.date_input(label, [
                                        completed_tasks.completed_date.min(),
                                        completed_tasks.completed_date.max()])

    completed_tasks = completed_tasks.loc[(completed_tasks["completed_date"] >= date_filter[0]) & (
        completed_tasks["completed_date"] <= date_filter[1])]

    return completed_tasks


def weekend_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    remove_weekends = st.sidebar.checkbox(label, False)
    if remove_weekends:
        completed_tasks = completed_tasks.loc[~(
            completed_tasks['completed_date_weekday'].isin(["Sunday", "Saturday"]))]

    return completed_tasks


def project_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    selected_projects = st.sidebar.multiselect(
        label, completed_tasks.project_name.unique())
    if len(selected_projects) != 0:
        completed_tasks = completed_tasks.loc[(
            completed_tasks['project_name'].isin(selected_projects))]

    return completed_tasks
