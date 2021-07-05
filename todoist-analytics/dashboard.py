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
dc.collect()
df_full = dc.items

df_full['datehour_completed'] = pd.to_datetime(df_full['completed_date'])
df_full['datehour_completed'] = pd.DatetimeIndex(df_full['datehour_completed']).tz_convert('America/Sao_Paulo')

filtered_df = df_full.loc[df_full['datehour_completed'] >= pd.to_datetime('today').tz_localize('America/Sao_Paulo') - timedelta(days=date_to_filter)]
filtered_df['completed_date'] = pd.to_datetime(filtered_df['datehour_completed']).dt.date
filtered_df['completed_date_weekday'] = pd.to_datetime(filtered_df['datehour_completed']).dt.day_name()


st.title("Todoist Analytics Report")
st.markdown(f"Analyzing data from {filtered_df.completed_date.min()} until {filtered_df.completed_date.max()}")
st.markdown(f"a grand total of {len(filtered_df)} completed tasks in {filtered_df.project_id.nunique()} projects")


df_all_g = filtered_df[['completed_date', 'project_id', 'id', 'content']].groupby(['completed_date'], as_index=False).nunique()
df_all_g['completed_date'] = df_all_g['completed_date'].astype(str)
fig = px.bar(df_all_g, x="completed_date", y="id", title='Daily completed tasks', hover_name='project_id')

if remove_weekends:
    fig.update_xaxes(
        rangebreaks=[
            { 'pattern': 'day of week', 'bounds': [6, 1]}
        ]
    )
st.plotly_chart(fig)
