from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_metrics import metric_row

from todoist_analytics.backend.data_collector import DataCollector
from todoist_analytics.backend.utils import *
from todoist_analytics.credentials import token
from todoist_analytics.frontend.plots import *
from todoist_analytics.frontend.filters import *


def create_app():
    st.title("Todoist Analytics Report")

    # date_to_filter = st.slider('days back', 0, 30, 8)

    completed_tasks = get_data(token)

    # completed_tasks = completed_tasks.loc[completed_tasks['datehour_completed'] >= pd.to_datetime(
    #     'today').tz_localize('America/Sao_Paulo') - timedelta(days=date_to_filter)]

    completed_tasks = date_filter(completed_tasks, "Choose the date range")
    completed_tasks = weekend_filter(completed_tasks, "Remove Weekends?")
    completed_tasks = project_filter(completed_tasks, "Select the desired")

    st.markdown(
        f"Analyzing data since {completed_tasks.completed_date.min()} until {completed_tasks.completed_date.max()}")
    st.markdown(
        f"a grand total of {len(completed_tasks)} completed tasks in {completed_tasks.project_id.nunique()} projects")

    st.plotly_chart(completed_tasks_per_day(completed_tasks))

    metric_row(
        {
            "Metric 1": 100,
            "Metric 2": 200,
            "Metric 3": 300,
            "Metric 4": 400,
            "Metric 5": 500,
        }
    )

    # st.plotly_chart(calendar_plot(completed_tasks))


if __name__ == "__main__":
    app = create_app()
