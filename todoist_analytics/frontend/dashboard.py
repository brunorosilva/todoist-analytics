import streamlit as st
import pandas as pd
import numpy as np
from ..backend.data_collector import DataCollector
from ..backend.preprocess import preprocess
from datetime import datetime, timedelta
from ..credentials import token
import plotly.express as px
from .plots import *


def create_app():
    date_to_filter = st.slider('days back', 0, 30, 8)
    remove_weekends = st.checkbox("Remove Weekends?", False)

    dc = DataCollector(token)
    dc.collect()

    df_full = preprocess(dc)

    filtered_df = df_full.loc[df_full['datehour_completed'] >= pd.to_datetime(
        'today').tz_localize('America/Sao_Paulo') - timedelta(days=date_to_filter)]

    st.title("Todoist Analytics Report")
    st.markdown(
        f"Analyzing data from {filtered_df.completed_date.min()} until {filtered_df.completed_date.max()}")
    st.markdown(
        f"a grand total of {len(filtered_df)} completed tasks in {filtered_df.project_id.nunique()} projects")

    df_all_g = filtered_df[['completed_date', 'project_id', 'id', 'content']].groupby(
        ['completed_date'], as_index=False).nunique()
    df_all_g['completed_date'] = df_all_g['completed_date'].astype(str)
    fig = px.bar(df_all_g, x="completed_date", y="id",
                 title='Daily completed tasks', hover_name='project_id')

    if remove_weekends:
        fig.update_xaxes(
            rangebreaks=[
                {'pattern': 'day of week', 'bounds': [6, 1]}
            ]
        )
    st.plotly_chart(fig)

    z = np.random.randint(2, size=(500,))

    st.plotly_chart(display_years(z, (2019, 2020)))


if __name__ == "__main__":
    app = create_app()
