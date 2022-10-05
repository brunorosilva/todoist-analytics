import streamlit as st
from src.utils import is_data_ready
from src.plots import calendar_plot, month_plot


def tasks_and_habits_metrics(all_tasks, all_habits, m, goal, a, b):
    n_tasks = all_tasks[all_tasks["completed_date"].dt.month == m].shape[0]
    n_habits = all_habits[all_habits["completed_date"].dt.month == m].shape[0]
    with a:
        st.metric("Completed tasks", n_tasks,
                  delta="{:.0%}".format((n_habits / n_tasks) / goal if n_tasks > 0 else 0))
    with b:
        st.metric("Habits", n_habits,
                  delta="{:.0%}".format((n_habits / n_tasks) / goal - 1 if n_tasks > 0 else 0))

def render():
    # Title
    st.title("Habits")

    # Sidebar notes
    st.sidebar.caption("Habits are recurring tasks completed at least twice.")
    habit_percentage = st.sidebar.slider(label="Percentage slider",
                                         min_value=0,
                                         max_value=100,
                                         value=30,
                                         format="%i%%") / 100.0

    # Get all tasks
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    # Year help array
    years = tasks["completed_date"].dt.year.unique().tolist()

    # Filter by year
    with st.sidebar:
        year = st.selectbox("Year", years)

    # Filter tasks of the selected year
    tasks_of_year = tasks[tasks["completed_date"].dt.year == year]

    # Months help arrays
    months = tasks_of_year["completed_date"].dt.month.unique().tolist()
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    # Get all the months in the data and filter for the selected month
    with st.sidebar:
        month_name = st.selectbox("Month", [month_names[m-1] for m in months])

    # Filter tasks of the selected month, get the quarter of the selected month and filter for the selected quarter
    month = month_names.index(month_name) + 1
    tasks_of_lasts_months = tasks_of_year[tasks_of_year["completed_date"].apply(lambda x: x.month == month or
                                                                                x.month == month-1 or
                                                                                x.month == month-2)]
    # Filter for habits
    habits = tasks[tasks.duplicated(subset=["task_id"], keep=False)]
    habits_of_year = habits[habits["completed_date"].dt.year == year]
    habits_of_lasts_months = habits_of_year[tasks_of_year["completed_date"].apply(lambda x: x.month == month or
                                                                                  x.month == month-1 or
                                                                                  x.month == month-2)]
    # Get the number of aggregated tasks per day
    counts_of_year_per_day = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
    counts_of_lasts_months_per_day = counts_of_year_per_day[tasks_of_lasts_months['completed_date'].dt.date]

    # Habits percentages and number of tasks
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    tasks_and_habits_metrics(tasks_of_lasts_months, habits_of_lasts_months, month-2, habit_percentage, col1, col2)
    tasks_and_habits_metrics(tasks_of_lasts_months, habits_of_lasts_months, month-1, habit_percentage, col3, col4)
    tasks_and_habits_metrics(tasks_of_lasts_months, habits_of_lasts_months, month-0, habit_percentage, col5, col6)

    # Heatmap of last 3 months
    fig, _ = calendar_plot(counts_of_lasts_months_per_day)
    st.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
