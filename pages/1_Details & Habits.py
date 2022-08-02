import streamlit as st
import july
from src.utils import is_data_ready


def render():
    ##################################
    # Data
    ##################################

    # Get all tasks
    st.title("Details")
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    ##################################
    # Filters
    ##################################

    habits_col, year_col, month_col, day_col = st.columns(4)

    # Filter for habits only if filter is checked
    with habits_col:
        only_habits = st.selectbox("Habits only", ["No", "Yes"])
        if only_habits == "Yes":
            tasks = tasks[tasks.duplicated(subset=["task_id"], keep=False)]
        st.caption("Habits are recurring tasks completed at least twice.")

    # Get all the years in the data and filter for the selected year
    with year_col:
        years = tasks["completed_date"].dt.year.unique().tolist()
        year = st.selectbox("Year", years)
        tasks_of_year = tasks[tasks["completed_date"].dt.year == year]
        st.caption("This filter affects next filters and all tabs.")

    # Get all the months in the data and filter for the selected month
    with month_col:
        months = tasks_of_year["completed_date"].dt.month.unique().tolist()
        month_names = ['January', 'February', 'March',     'April',   'May',      'June',
                       'July',    'August',   'September', 'October', 'November', 'December']
        month_name = st.selectbox("Month", [month_names[m-1] for m in months])
        month = month_names.index(month_name) + 1
        tasks_of_month = tasks_of_year[tasks_of_year["completed_date"].dt.month == month]
        st.caption("This filter affects day filter, month tab and day tab.")

    # Get all the days in the data and filter for the selected day
    with day_col:
        days = tasks_of_month["completed_date"].dt.day.unique().tolist()
        day = st.selectbox("Day", days)
        tasks_of_day = tasks_of_month[tasks_of_month["completed_date"].dt.day == day]
        st.caption("This filter affects only day tab.")

    ##################################
    # Tabs
    ##################################

    # Different tabs for different grouping options
    year_tab, month_tab, day_tab = st.tabs(["Year", "Month", "Day"])

    with day_tab:
        for project in tasks_of_day["project_name"].unique().tolist():
            if type(project) == str:
                tasks_in_project = tasks_of_day[tasks_of_day["project_name"] == project]
                project_name = project
            else:
                tasks_in_project = tasks_of_day[tasks_of_day["project_name"].isna()]
                project_name = "No project data"
            st.subheader(project_name + " (" + str(tasks_in_project.shape[0]) + ")")
            for task in tasks_in_project["content"].tolist():
                st.markdown("✔ " + task)

    with month_tab:
        counts_of_month = tasks_of_month["task_id"].groupby(by=tasks_of_month['completed_date'].dt.date).count()
        axes = july.month_plot(counts_of_month.index,
                               counts_of_month.values,
                               month=month,
                               cmap="github",
                               value_label=True,
                               colorbar=True)
        st.pyplot(axes.figure)

    with year_tab:
        counts_of_year = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
        axes = july.heatmap(counts_of_year.index,
                            counts_of_year.values,
                            month_grid=True,
                            cmap="github",
                            colorbar=True)
        st.pyplot(axes.figure)


if __name__ == "__main__":
    if is_data_ready():
        render()
