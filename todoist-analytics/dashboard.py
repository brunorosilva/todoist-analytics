import streamlit as st
import pandas as pd
import numpy as np
from data import data_collector
from datetime import datetime, timedelta
from credentials import token
import plotly.express as px

date_to_filter = st.slider('days back', 0, 30, 8)  # min: 0h, max: 23h, default: 17h

dc = data_collector(token)
df_full = dc.collect()
df_full['datehour_completed'] = pd.to_datetime(df_full['date_completed'])
df_full['datehour_completed'] = pd.DatetimeIndex(df_full['datehour_completed']).tz_convert(None)

filtered_df = df_full[df_full['datehour_completed'] >= datetime.today() - timedelta(days=date_to_filter)]
filtered_df['date_completed'] = pd.to_datetime(filtered_df['datehour_completed']).dt.date

st.title("Todoist Analytics Report")



df_all_g = filtered_df[['date_completed', 'project-id', 'id', 'content']].groupby(['date_completed'], as_index=False).nunique()


fig = px.bar(df_all_g, x="date_completed", y="id", title='Daily completed tasks', hover_name='project-id')
st.plotly_chart(fig)
