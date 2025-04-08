import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from PIL import Image

from todoist_analytics.backend.auth import run_auth
from todoist_analytics.backend.utils import create_color_palette, get_data
from todoist_analytics.constants import TODOIST_CLIENT_ID, TODOIST_CLIENT_SECRET
from todoist_analytics.frontend.plots import (
    analyze_weekly_pain_points,
    calendar_task_plot,
    completed_tasks_per_day_per_project,
    create_metrics_cards,
    day_of_week_ridgeline_plot,
    each_project_total_percentage_plot,
    generate_weekly_review_file,
    one_hundred_stacked_bar_plot_per_project,
    task_completion_by_hour_plot,
    task_completion_trend_plot,
    weekly_completion_trend_plot,
    weekly_review_plot,
)

def create_app():
    todoist_logo = Image.open("assets/images/todoist_logo.png")
    st.set_page_config(
        page_title="Todoist Analytics", layout="wide", page_icon=todoist_logo
    )
    client_id = TODOIST_CLIENT_ID
    client_secret = TODOIST_CLIENT_SECRET
    token = run_auth(client_id=client_id, client_secret=client_secret)
    # Add custom CSS
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .stMetric:hover {
            box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 0.5rem 0.5rem 0 0;
            gap: 1rem;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e0e2e6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title
    st.title("📊 Todoist Analytics")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Date range selector
        st.subheader("Date Range")
        date_range = st.radio(
            "Select date range",
            [
                "All time",
                "Last 30 days",
                "Last 90 days",
                "Last 180 days",
                "Last 365 days",
            ],
            index=0,
        )

        # Convert date range to days
        if date_range == "Last 30 days":
            days = 30
        elif date_range == "Last 90 days":
            days = 90
        elif date_range == "Last 180 days":
            days = 180
        elif date_range == "Last 365 days":
            days = 365
        else:
            days = None

        # Remove weekends option
        remove_weekends = st.checkbox("Remove weekends from calculations", value=False)

    # Main content
    if token:
        # try:
        # Get data
        completed_tasks, active_tasks = get_data(token)
        if days is not None:
            completed_tasks = completed_tasks[
                completed_tasks["completed_date"]
                >= (pd.Timestamp.now() - pd.Timedelta(days=days)).date()
            ]
        if remove_weekends:
            completed_tasks = completed_tasks[
                ~completed_tasks["completed_date_weekday"].isin(["Saturday", "Sunday"])
            ]
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "Overview",
                "Task Completion",
                "Project Analysis",
                "Weekly Review",
                "Settings",
            ]
        )

        # Overview tab
        with tab1:
            st.header("Overview")

            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            create_metrics_cards(completed_tasks, [col1, col2, col3, col4])

            # Task completion trend
            st.subheader("Task Completion Trend")
            st.plotly_chart(
                task_completion_trend_plot(completed_tasks), use_container_width=True
            )

            # Calendar view
            st.subheader("Calendar View")
            st.plotly_chart(
                calendar_task_plot(completed_tasks), use_container_width=True
            )
            st.markdown("---")
        # Task Completion tab
        with tab2:
            st.header("Task Completion")

            # Task completion by hour
            st.subheader("Task Completion by Hour")
            st.plotly_chart(
                task_completion_by_hour_plot(completed_tasks), use_container_width=True
            )

            # Day of week ridgeline plot
            st.subheader("Task Completion by Day of Week")
            st.plotly_chart(
                day_of_week_ridgeline_plot(completed_tasks), use_container_width=True
            )

        # Project Analysis tab
        with tab3:
            st.header("Project Analysis")
            color_palette = create_color_palette(completed_tasks)
            # Project distribution
            st.subheader("Project Distribution")
            st.plotly_chart(
                each_project_total_percentage_plot(completed_tasks, color_palette),
                use_container_width=True,
            )

            # Tasks per project over time
            st.subheader("Tasks per Project Over Time")
            st.plotly_chart(
                completed_tasks_per_day_per_project(completed_tasks, color_palette),
                use_container_width=True,
            )

            # 100% stacked bar plot
            st.subheader("Project Distribution Over Time")
            st.plotly_chart(
                one_hundred_stacked_bar_plot_per_project(
                    completed_tasks, color_palette
                ),
                use_container_width=True,
            )

        # Weekly Review tab
        with tab4:
            st.header("Weekly Review")

            # Weekly completion trend
            st.subheader("Weekly Completion Trend")
            st.plotly_chart(
                weekly_completion_trend_plot(completed_tasks), use_container_width=True
            )

            # Weekly review plot
            st.subheader("Weekly Review: Project Focus")
            st.plotly_chart(
                weekly_review_plot(completed_tasks, active_tasks),
                use_container_width=True,
            )

            # Analyze pain points
            st.subheader("Weekly Analysis")
            pain_points_data = analyze_weekly_pain_points(completed_tasks, active_tasks)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Pain Points")
                for i, point in enumerate(pain_points_data["pain_points"]):
                    st.markdown(f"- {point}")

                    # If this is the overdue tasks pain point and there are overdue tasks
                    if (
                        "overdue tasks" in point.lower()
                        and pain_points_data["overdue_tasks"]
                    ):

                        # Create an expander for the overdue tasks
                        with st.expander("View Overdue Tasks", expanded=False):
                            # Create a DataFrame for the overdue tasks
                            overdue_df = pd.DataFrame(pain_points_data["overdue_tasks"])

                            # Sort by days overdue (descending)
                            overdue_df = overdue_df.sort_values(
                                "days_overdue", ascending=False
                            )

                            # Display the overdue tasks in a table
                            st.dataframe(
                                overdue_df[
                                    [
                                        "content",
                                        "project_name",
                                        "due_date",
                                        "days_overdue",
                                    ]
                                ],
                                column_config={
                                    "content": "Task",
                                    "project_name": "Project",
                                    "due_date": "Due Date",
                                    "days_overdue": st.column_config.NumberColumn(
                                        "Days Overdue",
                                        help="Number of days the task is overdue",
                                        format="%d",
                                    ),
                                },
                                hide_index=True,
                                use_container_width=True,
                            )

                    # If this is the weekend tasks pain point and there are weekend tasks
                    if "weekend" in point.lower() and pain_points_data["weekend_tasks"]:

                        # Create an expander for the weekend tasks
                        with st.expander("View Weekend Tasks", expanded=False):
                            # Create a DataFrame for the weekend tasks
                            weekend_df = pd.DataFrame(pain_points_data["weekend_tasks"])

                            # Sort by due date
                            weekend_df = weekend_df.sort_values("due_date")

                            # Display the weekend tasks in a table
                            st.dataframe(
                                weekend_df[
                                    [
                                        "content",
                                        "project_name",
                                        "due_date",
                                        "day_of_week",
                                    ]
                                ],
                                column_config={
                                    "content": "Task",
                                    "project_name": "Project",
                                    "due_date": "Due Date",
                                    "day_of_week": "Day of Week",
                                },
                                hide_index=True,
                                use_container_width=True,
                            )
                    if (
                        "no due date" in point.lower()
                        and pain_points_data["active_tasks_no_due_date"]
                    ):
                        # Create an expander for the active tasks with no due date
                        with st.expander(
                            "View Active Tasks with No Due Date", expanded=False
                        ):
                            # Create a DataFrame for the active tasks with no due date
                            no_due_date_df = pd.DataFrame(
                                pain_points_data["active_tasks_no_due_date"]
                            )

                            # Display the active tasks with no due date in a table
                            st.dataframe(
                                no_due_date_df[["content", "project_name"]],
                                column_config={
                                    "content": "Task",
                                    "project_name": "Project",
                                },
                                hide_index=True,
                                use_container_width=True,
                            )

            with col2:
                st.markdown("### Recommendations")
                for rec in pain_points_data["recommendations"]:
                    st.markdown(f"- {rec}")

            # Generate weekly review file
            st.subheader("Weekly Review File")

            # Create a dictionary to store SVG content
            plot_images = {}

            # Generate SVG content for plots
            # Generate completed tasks by project plot
            completed_by_project_fig = each_project_total_percentage_plot(
                completed_tasks, color_palette
            )
            svg_content = pio.to_image(completed_by_project_fig, format="svg")
            plot_images["completed_tasks_by_project"] = svg_content

            # Generate active tasks by project plot
            active_by_project_fig = each_project_total_percentage_plot(
                active_tasks, color_palette
            )
            svg_content = pio.to_image(active_by_project_fig, format="svg")
            plot_images["active_tasks_by_project"] = svg_content

            # Generate upcoming tasks by day plot
            if not active_tasks.empty and "due" in active_tasks.columns:
                # Filter for upcoming tasks
                upcoming_tasks = active_tasks[
                    (active_tasks["due"] >= pd.Timestamp.now().normalize())
                    & (
                        active_tasks["due"]
                        <= pd.Timestamp.now().normalize() + pd.Timedelta(days=6)
                    )
                ]

                if not upcoming_tasks.empty:
                    # Group by day of week
                    upcoming_tasks["day_of_week"] = pd.to_datetime(
                        upcoming_tasks["due"]
                    ).dt.day_name()
                    by_day = (
                        upcoming_tasks.groupby("day_of_week")
                        .size()
                        .reset_index(name="count")
                    )

                    # Create a bar chart
                    upcoming_by_day_fig = px.bar(
                        by_day,
                        x="day_of_week",
                        y="count",
                        title="Upcoming Tasks by Day",
                        labels={
                            "day_of_week": "Day of Week",
                            "count": "Number of Tasks",
                        },
                    )
                    svg_content = pio.to_image(upcoming_by_day_fig, format="svg")
                    plot_images["upcoming_tasks_by_day"] = svg_content

            # Generate task completion trend plot
            task_completion_trend_fig = task_completion_trend_plot(completed_tasks)
            svg_content = pio.to_image(task_completion_trend_fig, format="svg")
            plot_images["task_completion_trend"] = svg_content

            # Generate task completion trend plot for 30 days
            task_completion_trend_fig_30_days = task_completion_trend_plot(
                completed_tasks[
                    completed_tasks["completed_date"]
                    >= (pd.Timestamp.now() - pd.Timedelta(days=30))
                ]
            )
            svg_content = pio.to_image(task_completion_trend_fig_30_days, format="svg")
            plot_images["task_completion_trend_30_days"] = svg_content

            # Generate weekly review plot
            weekly_review_fig = weekly_review_plot(completed_tasks, active_tasks)
            svg_content = pio.to_image(weekly_review_fig, format="svg")
            plot_images["weekly_review"] = svg_content

            # Generate the weekly review content with the SVG content
            weekly_review_content = generate_weekly_review_file(
                completed_tasks, active_tasks, plot_images
            )

            # Display the weekly review content
            st.text_area("Weekly Review Content", weekly_review_content, height=500)

            # Add a download button for the weekly review file
            st.download_button(
                label="Download Weekly Review",
                data=weekly_review_content,
                file_name=f"week{pd.Timestamp.now().isocalendar()[1]}.md",
                mime="text/markdown",
            )

        # Settings tab
        with tab5:
            st.header("Settings")

            # API Token info
            st.subheader("API Token")
            st.info(
                "Your API token is not stored. It is only used to fetch data from Todoist. "
                "It is not stored permanently and will need to be re-entered if you refresh the page."
            )

            # Date range info
            st.subheader("Date Range")
            st.info(
                "Select the date range for which you want to analyze your tasks. "
                "This will affect all charts and metrics in the dashboard."
            )

            # Remove weekends info
            st.subheader("Remove Weekends")
            st.info(
                "If enabled, weekends will be excluded from calculations for metrics like 'tasks per day'. "
                "This can give you a more accurate picture of your workday productivity."
            )

    # except Exception as e:
    #     st.error(f"Error: {str(e)}")
    else:
        st.info("Please click the link to get started.")

    return st


if __name__ == "__main__":
    app = create_app()  # noqa
