import streamlit as st
from src.utils import is_data_ready
from src.plots import category_pie, category_plot, plot_with_average


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

    # Completed tasks timeline
    st.header("Completed tasks by day")
    completed_tasks_per_day = completed_tasks["task_id"].groupby(by=completed_tasks["completed_date"].dt.date)\
                                                        .count().rename("count")
    fig, _ = plot_with_average(completed_tasks_per_day, x_label="Date", y_label="# Tasks")
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

    # Due tasks timeline
    st.header("Due tasks by day")
    due_tasks_per_day = due_tasks["task_id"].groupby(by=due_tasks["due_date"].dt.date)\
                                            .count().rename("count")
    fig, _ = plot_with_average(due_tasks_per_day, x_label="Date", y_label="# Tasks")
    st.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
