import streamlit as st
from datetime import date, timedelta
from src.utils import is_data_ready
from src.plots import plot_with_average, calendar_plot, month_plot


def habits_and_goals_metrics(goal, actual, habits):
    col1, col2, col3 = st.columns(3)
    habits_delta = (habits / actual) / goal - 1 if actual > 0 and goal > 0 else 0.0
    non_habits_delta = ((actual-habits) / actual) / (1-goal) - 1 if actual > 0 and (1-goal) > 0 else 0.0
    score = 1 + non_habits_delta if habits_delta > 0.0 else habits_delta + 1
    col1.metric("Completed tasks", actual, delta_color="off",
                delta="{:.0%}".format(score))
    col2.metric("Habits", habits,
                delta="{:.0%}".format(habits_delta))
    col3.metric("Non-Habits", actual-habits,
                delta="{:.0%}".format(non_habits_delta))


def render():
    # Title
    st.title("Habits")

    # Layout of app
    week_tab, month_tab, quarter_tab = st.tabs(["Week", "Month", "Quarter"])

    # Sidebar notes
    st.sidebar.caption("Habits are recurring tasks completed at least twice.")
    habit_percentage = st.sidebar.slider(label="Percentage slider",
                                         min_value=1,
                                         max_value=99,
                                         value=30,
                                         format="%i%%") / 100.0

    # Get all tasks
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    # Year help array
    years = tasks["completed_date"].dt.year.unique().tolist()

    # Filter by year
    year = st.sidebar.selectbox("Year", years)

    # Filter tasks of the selected year
    tasks_of_year = tasks[tasks["completed_date"].dt.year == year]

    # Months help arrays
    months = tasks_of_year["completed_date"].dt.month.unique().tolist()
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    # Get all the months in the data and filter for the selected month
    month_name = st.sidebar.selectbox("Month", [month_names[m-1] for m in months])

    # Filter tasks of the selected month, get the quarter of the selected month and filter for the selected quarter
    month = month_names.index(month_name) + 1
    quarter = (month - 1) // 3 + 1
    tasks_of_quarter = tasks_of_year[tasks_of_year["completed_date"].dt.quarter == quarter]
    tasks_of_month = tasks_of_quarter[tasks_of_quarter["completed_date"].dt.month == month]

    # Days help array
    days = tasks_of_month["completed_date"].dt.day.unique().tolist()

    # Get all the days in the data and filter for the selected day
    day = st.sidebar.selectbox("Day", days)
    st.sidebar.date_input("When's your birthday", date.today())

    # Get the week that belongs to the selected day, filter for the selected week and filter for the selected day
    start_day = 8 - st.session_state["user"]["start_day"]
    week = (date(year, month, day) + timedelta(days=start_day)) .isocalendar()[1]
    tasks_of_week = tasks_of_year[(tasks_of_year["completed_date"] +
                                   timedelta(days=start_day)).dt.isocalendar().week == week]

    # Filter for habits
    habits = tasks[tasks.duplicated(subset=["task_id"], keep=False)]
    habits_of_year = habits[habits["completed_date"].dt.year == year]
    habits_of_quarter = habits_of_year[habits_of_year["completed_date"].dt.quarter == quarter]
    habits_of_month = habits_of_quarter[habits_of_quarter["completed_date"].dt.month == month]
    habits_of_week = habits_of_year[(habits_of_year["completed_date"] +
                                     timedelta(days=start_day)).dt.isocalendar().week == week]
    # Get the number of aggregated tasks per day
    counts_of_year_per_day = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
    counts_of_quarter_per_day = counts_of_year_per_day[tasks_of_quarter['completed_date'].dt.date]
    counts_of_month_per_day = counts_of_quarter_per_day[tasks_of_month['completed_date'].dt.date]
    counts_of_week_per_day = counts_of_year_per_day[tasks_of_week['completed_date'].dt.date]

    # Get the number of aggregated tasks per month
    counts_of_year_per_month = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.month).count()
    counts_of_quarter_per_month = counts_of_year_per_month[tasks_of_quarter['completed_date'].dt.month]
    counts_of_year_per_month.set_axis([month_names[i - 1] for i in counts_of_year_per_month.index], inplace=True)
    counts_of_quarter_per_month.set_axis([month_names[i - 1] for i in counts_of_quarter_per_month.index], inplace=True)

    # Quarter tab: calendar, category pie and plot with average
    with quarter_tab:
        habits_and_goals_metrics(habit_percentage, tasks_of_quarter.shape[0], habits_of_quarter.shape[0])
        st.header("Calendar heatmap view")
        fig, _ = calendar_plot(counts_of_quarter_per_day)
        st.pyplot(fig)
        st.header("Tasks by day")
        fig2, _ = plot_with_average(counts_of_quarter_per_day,
                                    x_label="Day",
                                    y_label="# Tasks",
                                    figsize=(9, 4),
                                    labelrotation=30)
        st.pyplot(fig2)

    # Month tab: calendar, category pie and plot with average
    with month_tab:
        habits_and_goals_metrics(habit_percentage, tasks_of_month.shape[0], habits_of_month.shape[0])
        fig, _ = month_plot(counts_of_month_per_day, month)
        fig2, _ = plot_with_average(counts_of_month_per_day,
                                    x_label="Day",
                                    y_label="# Tasks",
                                    figsize=(9, 4),
                                    labelrotation=30)

        col1, col2 = st.columns(2)
        col1.header("Calendar heatmap view")
        col1.pyplot(fig)
        col2.header("Tasks by day")
        col2.pyplot(fig2)

    # Week tab: category pie and plot with average
    with week_tab:
        habits_and_goals_metrics(habit_percentage, tasks_of_week.shape[0], habits_of_week.shape[0])
        fig, _ = plot_with_average(counts_of_week_per_day,
                                   x_label="Day",
                                   y_label="# Tasks",
                                   figsize=(9, 4),
                                   labelrotation=30)
        st.header("Tasks by day")
        st.pyplot(fig)


if __name__ == "__main__":
    if is_data_ready():
        render()
