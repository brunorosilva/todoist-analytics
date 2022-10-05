from datetime import date
import streamlit as st
from src.utils import is_data_ready
from src.plots import category_pie, category_plot, heatmap_plot


def render():
    # Get data
    st.title("Homepage" + " - Welcome " + st.session_state["user"]["full_name"])
    tasks = st.session_state["tasks"].copy()
    completed_tasks = tasks.dropna(subset=["completed_date"])
    active_tasks = tasks[tasks["priority"] != "Priority 0"]
    due_tasks = active_tasks.dropna(subset=["due_date"])

    # Metrics top section
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Total Tasks", value=tasks.shape[0])
    col2.metric(label="Completed Tasks", value=completed_tasks.shape[0])
    col3.metric(label="Active Tasks", value=active_tasks.shape[0])
    col4.metric(label="Tasks with due date", value=due_tasks.shape[0])
    col5.metric(label="Projects", value=tasks["project_name"].nunique()-1)

    # Completed tasks heatmap of the current year
    st.header(f"Heatmap of completed task in current year")
    tasks_of_year = completed_tasks[completed_tasks["completed_date"].dt.year == date.today().year]
    counts_of_year_per_day = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
    fig, _ = heatmap_plot(counts_of_year_per_day)
    st.pyplot(fig)

    # Middle section columns
    col1, col2 = st.columns(2)

    # Active tasks per project
    with col1:
        st.header("Active tasks by project")
        fig, _ = category_pie(active_tasks, "project_name")
        st.pyplot(fig)

    # Active tasks per day
    with col2:
        st.header("Active tasks by priority")
        fig, _ = category_plot(active_tasks, "priority")
        st.pyplot(fig)

    # Completed tasks heatmap of the current year
    st.header(f"Heatmap of due task in current year")
    tasks_of_year = due_tasks[due_tasks["due_date"].dt.year == date.today().year]
    counts_of_year_per_day = tasks_of_year["task_id"].groupby(by=tasks_of_year['due_date'].dt.date).count()
    fig, _ = heatmap_plot(counts_of_year_per_day)
    st.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
