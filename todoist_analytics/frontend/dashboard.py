from datetime import timedelta

import streamlit as st

from todoist_analytics.backend.utils import *
from todoist_analytics.credentials import token
from todoist_analytics.frontend.filters import *
from todoist_analytics.frontend.plots import *


def create_app():
    st.title("Todoist Analytics Report")

    # date_to_filter = st.slider('days back', 0, 30, 8)
    
    with st.spinner("Getting your data :)"):
        completed_tasks = get_data(token)    

    completed_tasks = date_filter(completed_tasks, "date range filter")
    completed_tasks = last_week_filter(completed_tasks, "filter current week")
    completed_tasks = last_month_filter(completed_tasks, "filter current month")
    completed_tasks = last_year_filter(completed_tasks, "filter current year")
    completed_tasks = weekend_filter(completed_tasks, "remove weekends")
    completed_tasks = project_filter(completed_tasks, "select the desired project")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("completed tasks", len(completed_tasks.drop_duplicates()))
    col2.metric("projects", completed_tasks.project_id.nunique())
    col3.metric(
        "last seven days completed tasks",
        len(
            completed_tasks.loc[
                (
                    completed_tasks["completed_date"]
                    >= completed_tasks["completed_date"].max() - timedelta(days=7)
                )
            ].drop_duplicates()
        ),
    )
    col4.metric(
        "tasks per day", 
        round(len(completed_tasks.drop_duplicates())/((completed_tasks['completed_date'].max()-completed_tasks['completed_date'].min()).days), 1)
    )


    st.markdown(
        f"Analyzing data since {completed_tasks.completed_date.min()} until {completed_tasks.completed_date.max()}"
    )

    completed_tasks_radio = st.radio("Choose your view", ["total", "per project"])
    
    if completed_tasks_radio == "total":
        st.plotly_chart(completed_tasks_per_day(completed_tasks))
    else:
        st.plotly_chart(completed_tasks_per_day_per_project(completed_tasks))

    st.plotly_chart(one_hundred_stacked_bar_plot_per_project(completed_tasks))
    

    # st.plotly_chart(calendar_plot(completed_tasks))


if __name__ == "__main__":
    app = create_app()
