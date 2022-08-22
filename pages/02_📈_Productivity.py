import pandas as pd
from datetime import date
import streamlit as st
from src.utils import is_data_ready
from src.plots import plot_with_average, histogram


def render():
    # Title
    st.title("Productivity")

    # Layout of the page
    day_tab, week_tab = st.tabs(["Day", "Week"])

    # Get all tasks
    tasks = st.session_state["tasks"].copy()
    completed_tasks = tasks.dropna(subset=["completed_date"])
    completed_tasks["week"] = completed_tasks["year"].astype(str) + "_" + \
        completed_tasks["week"].map(lambda x: "{:02d}".format(x))

    # Get count of completed tasks per day and week
    completed_tasks_per_day = completed_tasks["task_id"].groupby(by=completed_tasks["completed_date"].dt.date)\
                                                        .count().rename("count")
    completed_tasks_per_week = completed_tasks["task_id"].groupby(by=completed_tasks["week"]).count().rename("count")

    # Figures of counts per day and week
    day_fig, _, day_velocity = plot_with_average(completed_tasks_per_day,
                                                 x_label="Date",
                                                 y_label="# Tasks",
                                                 ema=7)
    week_fig, ax, week_velocity = plot_with_average(completed_tasks_per_week,
                                                    x_label="Week",
                                                    y_label="# Tasks",
                                                    ema=12)
    for i, tick in enumerate(ax.xaxis.get_major_ticks()):
        if i % 15 != 5:
            tick.label1.set_visible(False)

    # Get goals per day and week
    daily_goal = st.session_state["user"].get("daily_goal", 0)
    weekly_goal = st.session_state["user"].get("weekly_goal", 0)

    # Get age of active tasks
    active_tasks = tasks[tasks["added_date"].apply(lambda x: not pd.isnull(x))]
    active_tasks = active_tasks[active_tasks["due_date"].apply(lambda x: pd.isnull(x))]
    active_tasks = active_tasks[active_tasks["recurring"].apply(lambda x: not x)]
    age_in_days = (date.today() - active_tasks["added_date"].dt.date).dt.days.rename("Age In Days")
    age_in_weeks = (age_in_days // 7).rename("Age In Weeks")

    with day_tab:
        # Goals, velocity and recommendation
        col1, col2, col3 = st.columns(3)
        col1.metric("Daily Goal",
                    "{} tasks".format(daily_goal),
                    help="The goal you set for yourself in todoist.")
        col2.metric("Actual Velocity (tasks/day)",
                    "{}".format(round(day_velocity, 1)),
                    help="Calculated using Exponential Moving Average on 7 days (EMA7) for yesterday.")
        col3.metric("Recommended Goal",
                    "{} tasks".format(round(day_velocity * 1.05)),
                    help="5% above actual velocity")
        st.pyplot(day_fig)

        # WIP, age, and lead time
        col1, col2, col3 = st.columns(3)
        col1.metric("Work In Progress",
                    "{} tasks".format(active_tasks.shape[0]),
                    help="Current amount of active tasks.")
        col2.metric("Average Age",
                    "{} days".format(round(age_in_days.mean(), 1)),
                    help="Average age since tasks were created.")
        col3.metric("Lead time",
                    "{} days".format(round(active_tasks.shape[0] / day_velocity, 1)),
                    help="Expected amount of time to complete a task once its created.")
        fig, _ = histogram(age_in_days)
        st.pyplot(fig)

    with week_tab:
        # Goals, velocity and recommendation
        col1, col2, col3 = st.columns(3)
        col1.metric("Weekly Goal",
                    "{} tasks".format(weekly_goal),
                    help="The goal you set for yourself in todoist.")
        col2.metric("Actual Velocity (tasks/week)",
                    "{}".format(round(week_velocity, 1)),
                    help="Calculated using Exponential Moving Average on 12 weeks (EMA12) for last week.")
        col3.metric("Recommended Goal",
                    "{} tasks".format(round(week_velocity * 1.05)),
                    help="5% above actual velocity")
        st.pyplot(week_fig)

        # WIP, age, and lead time
        col1, col2, col3 = st.columns(3)
        col1.metric("Work In Progress",
                    "{} tasks".format(active_tasks.shape[0]),
                    help="Current amount of active tasks.")
        col2.metric("Average Age",
                    "{} weeks".format(round(age_in_weeks.mean(), 1)),
                    help="Average age since tasks were created.")
        col3.metric("Lead time",
                    "{} weeks".format(round(active_tasks.shape[0] / week_velocity, 1)),
                    help="Expected amount of time to complete a task once its created.")
        fig, _ = histogram(age_in_weeks)
        st.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
