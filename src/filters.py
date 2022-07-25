from datetime import date, timedelta
import pandas as pd
import streamlit as st
from pandas.core.frame import DataFrame


def date_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    date_filter = st.sidebar.date_input(
        label,
        [completed_tasks.completed_date.min(), completed_tasks.completed_date.max()],
    )

    completed_tasks = completed_tasks.loc[
        (completed_tasks["completed_date"] >= date_filter[0])
        & (completed_tasks["completed_date"] <= date_filter[1])
    ]

    return completed_tasks


def weekend_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    remove_weekends = st.sidebar.checkbox(label, False)
    if remove_weekends:
        completed_tasks = completed_tasks.loc[
            ~(completed_tasks["completed_date_weekday"].isin(["Sunday", "Saturday"]))
        ]

    return completed_tasks, remove_weekends


def last_seven_days_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    view_last_week = st.sidebar.checkbox(label, False)
    if view_last_week:
        completed_tasks = completed_tasks.loc[
            (
                completed_tasks["completed_date"]
                > completed_tasks["completed_date"].max() - timedelta(days=7)
            )
        ]

    return completed_tasks


def last_week_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    view_last_week = st.sidebar.checkbox(label, False)
    if view_last_week:
        completed_tasks["completed_date"] = pd.to_datetime(
            completed_tasks["completed_date"]
        )
        completed_tasks = completed_tasks.loc[
            (
                completed_tasks["completed_date"].dt.week
                == completed_tasks["completed_date"].max().week
            )
            & (
                completed_tasks["completed_date"].dt.year
                == completed_tasks["completed_date"].max().year
            )
        ]

    return completed_tasks


def last_month_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    view_last_week = st.sidebar.checkbox(label, False)
    if view_last_week:
        completed_tasks = completed_tasks.loc[
            (
                completed_tasks["completed_date"]
                >= date(
                    completed_tasks["completed_date"].max().year,
                    completed_tasks["completed_date"].max().month,
                    1,
                )
            )
        ]

    return completed_tasks


def last_year_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    view_last_week = st.sidebar.checkbox(label, False)
    if view_last_week:
        completed_tasks = completed_tasks.loc[
            (
                completed_tasks["completed_date"]
                >= date(completed_tasks["completed_date"].max().year, 1, 1)
            )
        ]

    return completed_tasks


def project_filter(completed_tasks: DataFrame, label: str) -> DataFrame:
    selected_projects = st.sidebar.multiselect(
        label, completed_tasks.project_name.unique()
    )
    if len(selected_projects) != 0:
        completed_tasks = completed_tasks.loc[
            (completed_tasks["project_name"].isin(selected_projects))
        ]

    return completed_tasks


def get_recurrent_tasks(completed_tasks_habits) -> list:
    completed_tasks_habits = completed_tasks_habits.sort_values(
        "completed_date", ascending=False
    )
    recurrent_tasks = (
        completed_tasks_habits.loc[completed_tasks_habits["isRecurrent"] == 1][
            "content"
        ]
        .unique()
        .tolist()
    )

    return recurrent_tasks


def filter_recurrent_task(completed_tasks_habits, recurrent_tasks) -> DataFrame:
    selected_habits = st.multiselect(
        "Select one or more recurrent tasks, your most recent tasks should apper first",
        recurrent_tasks,
    )

    if len(selected_habits) > 0:
        completed_tasks_habits = completed_tasks_habits.loc[
            (completed_tasks_habits["content"].isin(selected_habits))
        ]
    return completed_tasks_habits
