import streamlit as st
import matplotlib.pyplot as plt
from src.utils import is_data_ready


def render():
    # Print welcome message
    st.title("Homepage")

    # Copy data from Todoist
    tasks = st.session_state["tasks"].copy()

    active_tasks = tasks[tasks["priority"] != 0]
    completed_tasks = tasks[tasks["priority"] == 0]

    # Dashboard top section
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Tasks", value=tasks.shape[0])
    col2.metric(label="Completed Tasks", value=completed_tasks.shape[0])
    col3.metric(label="Active Tasks", value=active_tasks.shape[0])
    col4.metric(label="Projects", value=tasks["project_name"].nunique()-1)

    st.header("Completed tasks per day")
    st.line_chart(tasks.groupby([tasks["completed_date"].dt.date]).content.count())

    col1, col2 = st.columns(2)

    with col1:
        st.header("Completed tasks per project")
        completed_tasks_project_counts = completed_tasks["project_name"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(completed_tasks_project_counts.values,
               labels=completed_tasks_project_counts.index,
               explode=[0.1] * len(completed_tasks_project_counts))
        st.pyplot(fig)

    with col2:
        st.header("Active tasks per project")
        active_tasks_project_counts = active_tasks["project_name"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(active_tasks_project_counts.values,
               labels=active_tasks_project_counts.index,
               explode=[0.1] * len(active_tasks_project_counts))
        col2.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
