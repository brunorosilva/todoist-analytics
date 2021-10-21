import numpy as np
import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame

from todoist_analytics.backend.data_collector import DataCollector
from todoist_analytics.frontend.colorscale import color_code_to_hex


def preprocess(dc: DataCollector) -> DataFrame:
    completed_tasks = dc.items
    projects = dc.projects
    projects = projects.rename({"id": "project_id"}, axis=1)

    completed_tasks["datehour_completed"] = pd.to_datetime(
        completed_tasks["completed_date"]
    )
    completed_tasks["datehour_completed"] = pd.DatetimeIndex(
        completed_tasks["datehour_completed"]
    ).tz_convert("America/Sao_Paulo")
    completed_tasks["completed_date"] = pd.to_datetime(
        completed_tasks["datehour_completed"]
    ).dt.date
    completed_tasks["completed_date_weekday"] = pd.to_datetime(
        completed_tasks["datehour_completed"]
    ).dt.day_name()
    completed_tasks = completed_tasks.merge(
        projects[["project_id", "name", "color", "inbox_project"]],
        how="left",
        left_on="project_id",
        right_on="project_id",
    )
    completed_tasks = completed_tasks.rename({"name": "project_name"}, axis=1)

    # creating the recurrent flag column -> not good implementation
    completed_date_count = completed_tasks.groupby("task_id").agg(
        {"completed_date": "nunique"}
    )
    completed_date_count["isRecurrent"] = np.where(
        completed_date_count["completed_date"] > 1, 1, 0
    )
    completed_date_count.drop(columns="completed_date", inplace=True)

    completed_tasks = completed_tasks.merge(
        completed_date_count, left_on="task_id", right_index=True
    )

    completed_tasks["hex_color"] = completed_tasks["color"].apply(
        lambda x: color_code_to_hex[int(x)]["hex"]
    )

    return completed_tasks


def create_color_palette(completed_tasks: DataFrame):
    project_id_color = pd.Series(
        completed_tasks.hex_color.values, index=completed_tasks.project_name
    ).to_dict()
    return project_id_color


@st.cache(show_spinner=False)  # caching the data and hiding the spinner warning
def get_data(token):
    dc = DataCollector(token)
    dc.collect_all()
    completed_tasks = preprocess(dc)

    return completed_tasks
