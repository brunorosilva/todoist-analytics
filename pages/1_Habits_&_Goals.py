import streamlit as st
from datetime import date, timedelta
import calendar
from src.utils import is_data_ready
from src.plots import category_pie, plot_with_average, heatmap_plot, calendar_plot, month_plot


def habits_and_goals_metrics(goal, actual, habits):
    col1, col2, col3 = st.columns(3)
    completed_delta_text = "more than goal" if actual > goal else "less than goal"
    col1.metric("Completed tasks", actual, delta="{} {}".format(actual - goal, completed_delta_text))
    goal_percent = (actual / goal - 1) if goal > 0 else 0
    goal_delta_text = "above goal" if goal_percent > 0 else "below goal"
    col2.metric("Goal", goal, delta="{:.0%} {}".format(goal_percent, goal_delta_text))
    col3.metric("Habits", habits, delta_color="off",
                delta="{:.0%} of completed tasks".format(habits / actual if actual > 0 else 0))


def category_pie_and_plot_with_average(tasks, counts, label, header):
    col1, col2 = st.columns(2)

    with col1:
        st.header("Tasks by project")
        fig1, _ = category_pie(tasks, "project_name")
        st.pyplot(fig1)

    with col2:
        st.header(header)
        fig2, _ = plot_with_average(counts, x_label=label, y_label="# Tasks", figsize=(9, 4), labelrotation=30)
        st.pyplot(fig2)


def render():
    # Title and view type
    st.title("Habits & Goals")

    # Layout of app
    year_col, month_col, day_col = st.columns(3)
    year_tab, quarter_tab, month_tab, week_tab, day_tab = st.tabs(["Year", "Quarter", "Month", "Week", "Day"])

    # Sidebar notes
    st.sidebar.caption("Habits are recurring tasks completed at least twice.")
    st.sidebar.caption("Change your day and week goals in the [productivity settings]("
                       "https://todoist.com/app/settings/productivity) inside of todoist.")

    # Get all tasks
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    # Year help array
    years = tasks["completed_date"].dt.year.unique().tolist()

    # Filter by year
    with year_col:
        year = st.selectbox("Year", years)
        st.caption("This filter affects next filters and all tabs.")

    # Filter tasks of the selected year
    tasks_of_year = tasks[tasks["completed_date"].dt.year == year]

    # Months help arrays
    months = tasks_of_year["completed_date"].dt.month.unique().tolist()
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    # Get all the months in the data and filter for the selected month
    with month_col:
        month_name = st.selectbox("Month", [month_names[m-1] for m in months])
        st.caption("This filter affects day filter as well as quarter, month, week, and day tabs.")

    # Filter tasks of the selected month, get the quarter of the selected month and filter for the selected quarter
    month = month_names.index(month_name) + 1
    quarter = (month - 1) // 3 + 1
    tasks_of_quarter = tasks_of_year[tasks_of_year["completed_date"].dt.quarter == quarter]
    tasks_of_month = tasks_of_quarter[tasks_of_quarter["completed_date"].dt.month == month]

    # Days help array
    days = tasks_of_month["completed_date"].dt.day.unique().tolist()

    # Get all the days in the data and filter for the selected day
    with day_col:
        day = st.selectbox("Day", days)
        st.caption("This filter affects the week tab and day tab.")

    # Get the week that belongs to the selected day, filter for the selected week and filter for the selected day
    start_day = 8 - st.session_state["user"]["start_day"]
    week = (date(year, month, day) + timedelta(days=start_day)) .isocalendar()[1]
    tasks_of_week = tasks_of_year[(tasks_of_year["completed_date"] +
                                   timedelta(days=start_day)).dt.isocalendar().week == week]
    tasks_of_day = tasks_of_week[tasks_of_week["completed_date"].dt.day == day]

    # Filter for habits
    habits = tasks[tasks.duplicated(subset=["task_id"], keep=False)]
    habits_of_year = habits[habits["completed_date"].dt.year == year]
    habits_of_quarter = habits_of_year[habits_of_year["completed_date"].dt.quarter == quarter]
    habits_of_month = habits_of_quarter[habits_of_quarter["completed_date"].dt.month == month]
    habits_of_week = habits_of_year[(habits_of_year["completed_date"] +
                                     timedelta(days=start_day)).dt.isocalendar().week == week]
    habits_of_day = habits_of_week[habits_of_week["completed_date"].dt.day == day]

    # Get the number of aggregated tasks per day
    counts_of_year_per_day = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
    counts_of_quarter_per_day = counts_of_year_per_day[tasks_of_quarter['completed_date'].dt.date]
    counts_of_month_per_day = counts_of_quarter_per_day[tasks_of_month['completed_date'].dt.date]
    counts_of_week_per_day = counts_of_year_per_day[tasks_of_week['completed_date'].dt.date]
    counts_of_day_per_hour = tasks_of_day["task_id"].groupby(by=tasks_of_day['completed_date'].dt.hour).count()

    # Get the number of aggregated tasks per month
    counts_of_year_per_month = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.month).count()
    counts_of_quarter_per_month = counts_of_year_per_month[tasks_of_quarter['completed_date'].dt.month]
    counts_of_year_per_month.set_axis([month_names[i - 1] for i in counts_of_year_per_month.index], inplace=True)
    counts_of_quarter_per_month.set_axis([month_names[i - 1] for i in counts_of_quarter_per_month.index], inplace=True)

    # Get the number of days per time unit
    days_in_year = 366 if calendar.isleap(year) else 365
    months_in_quarter = [quarter * 3 - 2, quarter * 3 - 1, quarter * 3]
    days_in_quarter = sum([calendar.monthrange(year, m)[1] for m in months_in_quarter])
    days_in_month = calendar.monthrange(year, month)[1]

    # Get the goals for each time unit
    daily_goal = st.session_state["user"].get("daily_goal", 0)
    weekly_goal = st.session_state["user"].get("weekly_goal", 0)
    monthly_goal = int(days_in_month / 7) * weekly_goal + (days_in_month % 7) * daily_goal
    quarterly_goal = int(days_in_quarter / 7) * weekly_goal + (days_in_quarter % 7) * daily_goal
    yearly_goal = int(days_in_year / 7) * weekly_goal + (days_in_year % 7) * daily_goal

    # Year tab: heatmap, category pie and plot with average
    with year_tab:
        habits_and_goals_metrics(yearly_goal, tasks_of_year.shape[0], habits_of_year.shape[0])
        st.header("Tasks of the year heatmap")
        fig, _ = heatmap_plot(counts_of_year_per_day)
        st.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_year, counts_of_year_per_month, "Month", "Tasks by month")

    # Quarter tab: calendar, category pie and plot with average
    with quarter_tab:
        habits_and_goals_metrics(quarterly_goal, tasks_of_quarter.shape[0], habits_of_quarter.shape[0])
        st.header("Calendar heatmap view")
        fig, _ = calendar_plot(counts_of_quarter_per_day)
        st.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_quarter, counts_of_quarter_per_month, "Month", "Tasks by month")

    # Month tab: calendar, category pie and plot with average
    with month_tab:
        habits_and_goals_metrics(monthly_goal, tasks_of_month.shape[0], habits_of_month.shape[0])
        st.header("Calendar heatmap view")
        fig, _ = month_plot(counts_of_month_per_day, month)
        _, col, _ = st.columns(3)
        col.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_month, counts_of_month_per_day, "Day", "Tasks by day")

    # Week tab: category pie and plot with average
    with week_tab:
        habits_and_goals_metrics(weekly_goal, tasks_of_week.shape[0], habits_of_week.shape[0])
        category_pie_and_plot_with_average(tasks_of_week, counts_of_week_per_day, "Day", "Tasks by day")

    # Day tab
    with day_tab:
        habits_and_goals_metrics(daily_goal, tasks_of_day.shape[0], habits_of_day.shape[0])
        category_pie_and_plot_with_average(tasks_of_day, counts_of_day_per_hour, "Hour", "Tasks by hour")
        st.header("List of tasks")
        for project in tasks_of_day["project_name"].unique().tolist():
            tasks_in_project = tasks_of_day[tasks_of_day["project_name"] == project]
            project_name = project
            st.subheader(project_name + " (" + str(tasks_in_project.shape[0]) + ")")
            for task in tasks_in_project["content"].tolist():
                st.markdown("✔ " + task)


if __name__ == "__main__":
    if is_data_ready():
        render()
