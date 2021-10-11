import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame

from todoist_analytics.backend.data_collector import DataCollector


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
    print(completed_tasks.columns)
    print(completed_tasks.shape)
    print(projects["project_id"])
    return completed_tasks


@st.cache(show_spinner=False)  # caching the data and hiding the spinner warning
def get_data(token):
    dc = DataCollector(token)
    dc.collect_all()
    completed_tasks = preprocess(dc)

    return completed_tasks
