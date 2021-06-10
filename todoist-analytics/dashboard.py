import streamlit as st
import pandas as pd
import numpy as np
from data import data_collector
from datetime import datetime, timedelta
from credentials import token
import plotly.express as px

date_to_filter = st.slider('days back', 0, 30, 8) 
remove_weekends = st.checkbox("Remove Weekends?", False)

dc = data_collector(token)
df_full = dc.collect()
df_full['datehour_completed'] = pd.to_datetime(df_full['date_completed'])
df_full['datehour_completed'] = pd.DatetimeIndex(df_full['datehour_completed']).tz_convert(None)

filtered_df = df_full.loc[df_full['datehour_completed'] >= datetime.today() - timedelta(days=date_to_filter)]
filtered_df['date_completed'] = pd.to_datetime(filtered_df['datehour_completed']).dt.date
filtered_df['date_completed_weekday'] = pd.to_datetime(filtered_df['datehour_completed']).dt.day_name()


st.title("Todoist Analytics Report")
st.markdown(f"Analyzing data from {filtered_df.date_completed.min()} until {filtered_df.date_completed.max()}")
st.markdown(f"a grand total of {filtered_df.id.nunique()} completed tasks in {filtered_df.project_id.nunique()} projects")


df_all_g = filtered_df[['date_completed', 'project-id', 'id', 'content']].groupby(['date_completed'], as_index=False).nunique()
df_all_g['date_completed'] = df_all_g['date_completed'].astype(str)
fig = px.bar(df_all_g, x="date_completed", y="id", title='Daily completed tasks', hover_name='project-id')

if remove_weekends:
    fig.update_xaxes(
        rangebreaks=[
            { 'pattern': 'day of week', 'bounds': [6, 1]}
        ]
    )
st.plotly_chart(fig)
