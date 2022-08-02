import streamlit as st
from datetime import date
import july
from src.utils import is_data_ready
from src.plots import category_pie, plot_with_average


def render():
    ##################################
    # Data
    ##################################

    # Get all tasks
    st.title("Details & Habits")
    tasks = st.session_state["tasks"].copy()
    tasks = tasks[["task_id", "content", "project_name", "completed_date"]].dropna(subset=["completed_date"])

    # Helper array
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

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
        month_name = st.selectbox("Month", [month_names[m-1] for m in months])
        month = month_names.index(month_name) + 1
        tasks_of_month = tasks_of_year[tasks_of_year["completed_date"].dt.month == month]
        tasks_of_quarter = tasks_of_year[tasks_of_year["completed_date"].dt.quarter == (month - 1) // 3 + 1]
        st.caption("This filter affects day filter, months tabs and days tabs.")

    # Get all the days in the data and filter for the selected day
    with day_col:
        days = tasks_of_month["completed_date"].dt.day.unique().tolist()
        day = st.selectbox("Day", days)
        tasks_of_day = tasks_of_month[tasks_of_month["completed_date"].dt.day == day]
        week_number = date(year, month, day).isocalendar()[1]
        tasks_of_week = tasks_of_year[tasks_of_year["completed_date"].dt.isocalendar().week == week_number]
        st.caption("This filter affects the 7-day tab and day tab.")

    ##################################
    # Tabs
    ##################################

    # Different tabs for different grouping options
    year_tab, quarter_tab, month_tab, week_tab, day_tab = st.tabs(["Year", "Quarter", "Month", "Week", "Day"])

    with year_tab:
        col1, col2 = st.columns(2)

        with col1:
            st.header("Tasks per project")
            fig, _ = category_pie(tasks_of_year, "project_name")
            st.pyplot(fig)

        with col2:
            st.header("Tasks per month")
            tasks_per_month = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.month)\
                                                      .count().rename("count")
            tasks_per_month.set_axis([month_names[i-1] for i in tasks_per_month.index], inplace=True)
            fig, ax = plot_with_average(tasks_per_month, x_label="Month", y_label="# Tasks", figsize=(9, 4))
            ax.tick_params(axis='x', labelrotation=30)
            st.pyplot(fig)

        st.header("Tasks of the year heatmap")
        counts_of_year = tasks_of_year["task_id"].groupby(by=tasks_of_year['completed_date'].dt.date).count()
        ax = july.heatmap(counts_of_year.index,
                          counts_of_year.values,
                          month_grid=True,
                          cmap="github",
                          colorbar=True)
        st.pyplot(ax.figure)

    with quarter_tab:
        col1, col2 = st.columns(2)

        with col1:
            st.header("Tasks per project")
            fig, ax = category_pie(tasks_of_quarter, "project_name")
            st.pyplot(fig)

        with col2:
            st.header("Tasks per month")
            tasks_per_month = tasks_of_quarter["task_id"].groupby(by=tasks_of_quarter['completed_date'].dt.month) \
                                                         .count().rename("count")
            tasks_per_month.set_axis([month_names[i - 1] for i in tasks_per_month.index], inplace=True)
            fig, ax = plot_with_average(tasks_per_month, x_label="Month", y_label="# Tasks", figsize=(9, 4))
            ax.tick_params(axis='x', labelrotation=30)
            st.pyplot(fig)

        st.header("Calendar heatmap view")
        counts_of_month = tasks_of_quarter["task_id"].groupby(by=tasks_of_quarter['completed_date'].dt.date).count()
        axes = july.calendar_plot(counts_of_month.index,
                                  counts_of_month.values,
                                  title=False,
                                  cmap="github",
                                  value_label=True)
        st.pyplot(axes[0].figure)

    with month_tab:
        col1, col2 = st.columns(2)

        with col1:
            st.header("Tasks per project")
            fig, _ = category_pie(tasks_of_month, "project_name")
            st.pyplot(fig)

        with col2:
            st.header("Calendar heatmap view")
            counts_of_month = tasks_of_month["task_id"].groupby(by=tasks_of_month['completed_date'].dt.date).count()
            axes = july.month_plot(counts_of_month.index,
                                   counts_of_month.values,
                                   month=month,
                                   cmap="github",
                                   value_label=True,
                                   colorbar=True)
            st.pyplot(axes.figure)

    with week_tab:
        col1, col2 = st.columns(2)

        with col1:
            st.header("Tasks per project")
            fig, _ = category_pie(tasks_of_week, "project_name")
            st.pyplot(fig)

        with col2:
            st.header("Tasks per day")
            tasks_per_day = tasks_of_week["task_id"].groupby(by=tasks_of_week['completed_date'].dt.date) \
                                                    .count().rename("count")
            fig, ax = plot_with_average(tasks_per_day, x_label="Day", y_label="# Tasks", figsize=(9, 4))
            ax.tick_params(axis='x', labelrotation=30)
            st.pyplot(fig)

    with day_tab:
        col1, col2 = st.columns(2)

        with col1:
            st.header("Tasks per project")
            fig, _ = category_pie(tasks_of_day, "project_name")
            st.pyplot(fig)

        with col2:
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
