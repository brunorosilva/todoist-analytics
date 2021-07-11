from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from ..backend.data_collector import DataCollector
from ..backend.preprocess import preprocess
from ..credentials import token
from .plots import *


def create_app():
    st.title("Todoist Analytics Report")

    date_to_filter = st.slider('days back', 0, 30, 8)
    remove_weekends = st.checkbox("Remove Weekends?", False)

    dc = DataCollector(token)

    if not dc.got_all_tasks:
        dc.collect_all()
        completed_tasks = preprocess(dc)

    completed_tasks = completed_tasks.loc[completed_tasks['datehour_completed'] >= pd.to_datetime(
        'today').tz_localize('America/Sao_Paulo') - timedelta(days=date_to_filter)]

    st.markdown(
        f"Analyzing data from {completed_tasks.completed_date.min()} until {completed_tasks.completed_date.max()}")
    st.markdown(
        f"a grand total of {len(completed_tasks)} completed tasks in {completed_tasks.project_id.nunique()} projects")

    fig = completed_tasks_per_day(completed_tasks)
    if remove_weekends:
        fig.update_xaxes(
            rangebreaks=[
                {'pattern': 'day of week', 'bounds': [6, 1]}
            ]
        )
    st.plotly_chart(fig)

    z = np.random.randint(2, size=(500,))

    st.plotly_chart(calendar_plot(z, (2019, 2020)))


if __name__ == "__main__":
    app = create_app()
