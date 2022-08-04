import streamlit as st
from datetime import date
from src.utils import is_data_ready
from src.plots import category_pie, plot_with_average, heatmap_plot, calendar_plot, month_plot


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
    st.title("Details")
    with st.sidebar:
        view_type = st.radio("Select type:", ["All", "Habits", "Goals"])
        st.caption("Habits are recurring tasks completed at least twice.")

    # Layout of app
    year_col, month_col, day_col = st.columns(3)
    year_tab, quarter_tab, month_tab, week_tab, day_tab = st.tabs(["Year", "Quarter", "Month", "Week", "Day"])

    # Get all tasks
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    # Filter for habits only if habits filter is checked
    if view_type == "Habits":
        tasks = tasks[tasks.duplicated(subset=["task_id"], keep=False)]

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
    week = date(year, month, day).isocalendar()[1]
    tasks_of_week = tasks_of_year[tasks_of_year["completed_date"].dt.isocalendar().week == week]
    tasks_of_day = tasks_of_week[tasks_of_week["completed_date"].dt.day == day]

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

    # Year tab: heatmap, category pie and plot with average
    with year_tab:
        st.header("Tasks of the year heatmap")
        fig, _ = heatmap_plot(counts_of_year_per_day)
        st.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_year, counts_of_year_per_month, "Month", "Tasks by month")

    # Quarter tab: calendar, category pie and plot with average
    with quarter_tab:
        st.header("Calendar heatmap view")
        fig, _ = calendar_plot(counts_of_quarter_per_day)
        st.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_quarter, counts_of_quarter_per_month, "Month", "Tasks by month")

    # Month tab: calendar, category pie and plot with average
    with month_tab:
        st.header("Calendar heatmap view")
        fig, _ = month_plot(counts_of_month_per_day, month)
        _, col, _ = st.columns(3)
        col.pyplot(fig)
        category_pie_and_plot_with_average(tasks_of_month, counts_of_month_per_day, "Day", "Tasks by day")

    # Week tab: ?????, category pie and plot with average
    with week_tab:
        category_pie_and_plot_with_average(tasks_of_week, counts_of_week_per_day, "Day", "Tasks by day")

    # Day tab
    with day_tab:
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
