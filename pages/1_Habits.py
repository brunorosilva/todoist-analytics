import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import july
from july.utils import date_range
from src.utils import is_data_ready


def render():
    st.title("Habits")
    tasks = st.session_state["tasks"].copy()
    habits = tasks[tasks["recurring"].fillna(False)].dropna(subset=["completed_date"])
    habits = habits[["task_id", "content", "project_name", "completed_date", "color"]]

    # Filter preparation
    years = habits["completed_date"].dt.year.unique().tolist()

    # Get and print the counts per day
    counts_per_day = habits["task_id"].groupby(by=habits['completed_date'].dt.date).count()
    axes = july.heatmap(counts_per_day.index, counts_per_day.values, cmap="github", colorbar=True)
    axes.get_yaxis().set_ticks([])
    st.pyplot(axes.figure)

    tab1, tab2, tab3 = st.tabs(["Weekly", "Monthly", "Yearly"])

    with tab1:
        st.write(habits)

    with tab2:
        year = st.selectbox("Year", years)
        filtered_habits = habits[habits["completed_date"].dt.year == year]
        filtered_counts = filtered_habits["task_id"].groupby(by=filtered_habits['completed_date'].dt.date).count()
        axes = july.calendar_plot(filtered_counts.index, filtered_counts.values, value_label=True, cmap="github")
        if type(axes[0]) == np.ndarray:
            st.pyplot(axes[0][0].figure)
        else:
            print(axes[0])
            st.pyplot(axes[0].figure)


    with tab3:
        col1, col2 = st.columns([3, 1])
        with col1:
            for year in years:
                filtered_habits = habits[habits["completed_date"].dt.year == year]
                filtered_counts = filtered_habits["task_id"].groupby(
                    by=filtered_habits['completed_date'].dt.date).count()
                axes = july.heatmap(filtered_counts.index, filtered_counts.values, cmap="github", colorbar=True)
                axes.get_yaxis().set_ticks([])
                st.pyplot(axes.figure)
                # axes = july.calendar_plot(dates, data, value_label=True, cmap="github")
                # fig = axes[0][0].figure
                # st.pyplot(fig)
            # fig, ax = plt.subplots()
            # july.heatmap(dates, data, month=7, year=2022, value_label=True, cmap="github", ax=ax)
            # st.pyplot(fig)



if __name__ == "__main__":
    if is_data_ready():
        render()
