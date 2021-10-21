import numpy as np
import streamlit as st

from todoist_analytics.backend.utils import *
from todoist_analytics.credentials import token
from todoist_analytics.frontend.filters import *
from todoist_analytics.frontend.plots import *


def create_app():
    st.set_page_config(page_title="Todoist Analytics")
    st.title("Todoist Analytics Report")

    with st.spinner("Getting your data :)"):
        completed_tasks = get_data(token)

    completed_tasks = date_filter(completed_tasks, "date range filter")
    completed_tasks = last_week_filter(completed_tasks, "filter current week")
    completed_tasks = last_month_filter(completed_tasks, "filter current month")
    completed_tasks = last_year_filter(completed_tasks, "filter current year")
    completed_tasks = weekend_filter(completed_tasks, "remove weekends")
    completed_tasks = project_filter(completed_tasks, "select the desired project")

    create_metrics_cards(completed_tasks, list(st.columns(4)))

    st.markdown(
        f"Analyzing data since {completed_tasks.completed_date.min()} until {completed_tasks.completed_date.max()}"
    )

    completed_tasks_radio = st.radio("Choose your view", ["total", "per project"])

    color_palette = create_color_palette(completed_tasks)

    if completed_tasks_radio == "total":
        st.plotly_chart(completed_tasks_per_day(completed_tasks))
    else:
        st.plotly_chart(
            completed_tasks_per_day_per_project(completed_tasks, color_palette)
        )

    st.plotly_chart(
        one_hundred_stacked_bar_plot_per_project(completed_tasks, color_palette)
    )

    # st.plotly_chart(calendar_plot(completed_tasks))


if __name__ == "__main__":
    app = create_app()
