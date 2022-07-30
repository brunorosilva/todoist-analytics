import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.auth import run_auth
from src.data import get_data


def render():
    # Print welcome message
    st.title("Welcome to Todoist Analytics")
    st.caption("This is a simple app to track your habits.")

    # Copy data from Todoist
    tasks = st.session_state["tasks"].copy()

    active_tasks = tasks[tasks["priority"] != 0]
    completed_tasks = tasks[tasks["priority"] == 0]
    habits = tasks[tasks["recurring"] == True]

    # Dashboard top section
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Tasks", value=tasks.shape[0])
    col2.metric(label="Completed Tasks", value=completed_tasks.shape[0])
    col3.metric(label="Active Tasks", value=active_tasks.shape[0])
    col4.metric(label="Projects", value=tasks["project_name"].nunique()-1)

    st.header("Completed tasks per day")
    st.bar_chart(tasks.groupby([tasks["completed_date"].dt.date]).content.count())

    completed_tasks_project_counts = completed_tasks["project_name"].value_counts()
    active_tasks_project_counts = active_tasks["project_name"].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        st.header("Completed tasks per project")
        fig, ax = plt.subplots()
        ax.pie(completed_tasks_project_counts.values,
               labels=completed_tasks_project_counts.index,
               explode=[0.1] * len(completed_tasks_project_counts))
        st.pyplot(fig)

    with col2:
        st.header("Active tasks per project")
        fig, ax = plt.subplots()
        ax.pie(active_tasks_project_counts.values,
               labels=active_tasks_project_counts.index,
               explode=[0.1] * len(active_tasks_project_counts))
        col2.pyplot(fig)

    # Table with all values
    st.header("Tasks")
    st.write(tasks)


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    if 'data_loaded' not in st.session_state:
        token = run_auth()

        if token is not None:
            with st.spinner("Getting your data :)"):
                tasks, user = get_data(token)
                st.session_state["tasks"] = tasks
                st.session_state["user"] = user
                st.session_state["data_loaded"] = True
                st.info("Your data is loaded, you can start using this app now.")

    if 'data_loaded' in st.session_state:
        render()
