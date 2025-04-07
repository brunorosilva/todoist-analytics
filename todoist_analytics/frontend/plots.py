import base64
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from pandas import DataFrame
from plotly.colors import n_colors
from plotly.missing_ipywidgets import FigureWidget
from plotly_calplot import calplot


def create_metrics_cards(completed_tasks: DataFrame, cols: list):
    cols[0].metric("completed tasks", len(completed_tasks))
    cols[1].metric("projects", completed_tasks.project_id.nunique())
    cols[2].metric(
        "tasks last 7 days",
        len(
            completed_tasks.loc[
                (
                    completed_tasks["completed_date"]
                    >= completed_tasks["completed_date"].max() - timedelta(days=7)
                )
            ]
        ),
    )
    cols[3].metric(
        "tasks per day",
        int(
            round(
                len(completed_tasks)
                / (
                    (
                        (
                            completed_tasks["completed_date"].max()
                            - completed_tasks["completed_date"].min()
                        ).days
                    )
                    + 1
                ),
                0,
            ),
        ),
    )


def completed_tasks_per_day(completed_tasks: DataFrame) -> FigureWidget:
    daily_completed_tasks = (
        completed_tasks[["completed_date", "project_id", "id", "content", "hex_color"]]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )
    daily_completed_tasks["completed_date"] = daily_completed_tasks[
        "completed_date"
    ].astype(str)

    fig = go.Figure()
    fig.add_traces(
        go.Bar(
            x=daily_completed_tasks["completed_date"].astype(str),
            y=daily_completed_tasks["id"],
            name="Total",
            hovertemplate="<b>Date: %{x}</b><br>%{y} tasks completed",
            marker_line_width=0,
        )
    )
    fig.update_layout(
        yaxis_title="Completed tasks", xaxis_title="Date of completion", width=100
    )

    return fig


def completed_tasks_per_day_per_project(
    completed_tasks: DataFrame, color_palette: dict
) -> FigureWidget:
    daily_completed_tasks_per_project = (
        completed_tasks[
            ["completed_date", "project_id", "id", "project_name", "content"]
        ]
        .groupby(["completed_date", "project_name"], as_index=False)
        .nunique()
    )
    daily_completed_tasks_per_project[
        "completed_date"
    ] = daily_completed_tasks_per_project["completed_date"].astype(str)
    fig = px.bar(
        daily_completed_tasks_per_project,
        x="completed_date",
        y="id",
        color="project_name",
        title="Daily completed tasks",
        color_discrete_map=color_palette,
        labels={
            "project_name": "Project Name",
            "completed_date": "Date",
            "id": "Completed Tasks",
        },
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(barmode="relative", legend_title_text="Project Name")

    return fig


def one_hundred_stacked_bar_plot_per_project(
    completed_tasks: DataFrame, color_palette: dict
) -> FigureWidget:
    daily_completed_tasks_per_project = (
        completed_tasks[
            ["completed_date", "project_id", "id", "project_name", "content"]
        ]
        .groupby(["completed_date", "project_name"], as_index=False)
        .nunique()
    )
    daily_completed_tasks_per_project[
        "completed_date"
    ] = daily_completed_tasks_per_project["completed_date"].astype(str)

    aux = daily_completed_tasks_per_project.copy()
    aux = aux.pivot(
        index=["completed_date"], columns="project_name", values="id"
    ).fillna(0)
    aux = aux.div(aux.sum(axis=1), axis=0)

    fig = go.Figure()

    for project in daily_completed_tasks_per_project["project_name"].unique():
        project_color = color_palette[project]
        fig.add_trace(
            go.Bar(
                x=aux.index,
                y=aux[project],
                name=project,
                marker_color=project_color,
                hovertemplate="<b>Date: %{x}</b><br>%{customdata}% of total",
                customdata=round(aux[project] * 100, 1),
                marker_line_width=0,
            )
        )
    # fig.update_traces(marker=dict(color=color_palette))
    fig.update_layout(barmode="relative", title_text="Percentage of tasks per project")
    return fig


def calendar_task_plot(completed_tasks: DataFrame) -> FigureWidget:
    daily_completed_tasks = (
        completed_tasks[["completed_date", "project_id", "id", "content", "hex_color"]]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )

    daily_completed_tasks["completed_date"] = pd.to_datetime(
        daily_completed_tasks["completed_date"]
    )
    fig = calplot(
        daily_completed_tasks,
        x="completed_date",
        y="id",
        name="Completed Tasks",
        dark_theme=True,
        colorscale="blues",
        gap=0,
        years_title=True,
        title="Complete tasks Calendar view",
    )
    fig.update_layout(
        paper_bgcolor=("#0e1117"),
        plot_bgcolor=("#0e1117"),
    )
    return fig


def each_project_total_percentage_plot(
    completed_tasks: pd.DataFrame, color_palette: dict
) -> go.FigureWidget:
    daily_completed_tasks_per_project = (
        completed_tasks[["project_id", "id", "project_name", "content", "hex_color"]]
        .groupby(["project_name", "hex_color", "project_id"], as_index=False)
        .nunique()
    )

    daily_completed_tasks_per_project["pct_of_total"] = round(
        (
            daily_completed_tasks_per_project["id"].div(
                daily_completed_tasks_per_project["id"].sum()
            )
            * 100
        ),
        1,
    )

    # Sort by decreasing contribution
    daily_completed_tasks_per_project = daily_completed_tasks_per_project.sort_values(
        by="pct_of_total", ascending=True
    )

    # Create stacked horizontal bar plot
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=daily_completed_tasks_per_project["project_name"],
            x=daily_completed_tasks_per_project["pct_of_total"],
            text=(
                daily_completed_tasks_per_project["pct_of_total"].astype(str)
                + " %<br>"
                + daily_completed_tasks_per_project["id"].astype(str)
                + " tasks"
            ),
            textposition="inside",
            marker=dict(
                color=daily_completed_tasks_per_project["hex_color"],
            ),
            orientation="h",
            hoverinfo="y+text",
        )
    )

    fig.update_layout(
        title="Percentage of tasks per project",
        xaxis=dict(title="% of total tasks"),
        yaxis=dict(title="Project"),
    )

    return fig


def calendar_habits_plot(completed_tasks_habits: DataFrame):
    daily_completed_tasks = (
        completed_tasks_habits[
            ["completed_date", "project_id", "id", "content", "hex_color"]
        ]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )

    daily_completed_tasks["completed_date"] = pd.to_datetime(
        daily_completed_tasks["completed_date"]
    )

    # for this plot it'll be used a 100% colorscale
    # therefore if any value is above 0, it'll be
    # shown as the strongest color in the scale

    custom_colorscale = [[0.0, "rgb(200,200,200)"], [1.0, "rgb(200,200,200)"]]
    fig = calplot(
        daily_completed_tasks,
        x="completed_date",
        y="id",
        name="Completed Recurrent Tasks",
        dark_theme=True,
        colorscale=custom_colorscale,
        gap=0,
        years_title=True,
    )
    fig.update_layout(
        paper_bgcolor=("#0e1117"),
        plot_bgcolor=("#0e1117"),
    )
    return fig


def day_of_week_ridgeline_plot(completed_tasks: DataFrame):
    colors = n_colors("rgb(230,230,250)", "rgb(100,230,250)", 7, colortype="rgb")

    # rigdeline plot
    daily_completed_tasks = (
        completed_tasks[["completed_date", "project_id", "id", "content", "hex_color"]]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )

    daily_completed_tasks["completed_date"] = pd.to_datetime(
        daily_completed_tasks["completed_date"]
    )

    daily_completed_tasks["weekday"] = daily_completed_tasks[
        "completed_date"
    ].dt.weekday
    daily_completed_tasks["weekday_name"] = daily_completed_tasks[
        "completed_date"
    ].dt.day_name()

    fig = go.Figure()
    for i, weekday in enumerate(
        sorted(daily_completed_tasks["weekday"].unique(), reverse=True)
    ):
        average_of_weekday = round(
            daily_completed_tasks.loc[daily_completed_tasks["weekday"] == weekday][
                "id"
            ].mean()
        )
        daily_completed_tasks["weekday_name_with_average"] = daily_completed_tasks[
            "weekday_name"
        ].apply(lambda x: str(x) + "<br>mean " + str(average_of_weekday))

        fig.add_trace(
            go.Violin(
                x=daily_completed_tasks.loc[
                    daily_completed_tasks["weekday"] == weekday
                ]["id"],
                y=daily_completed_tasks.loc[
                    daily_completed_tasks["weekday"] == weekday
                ]["weekday_name_with_average"],
                line_color=colors[i],
                orientation="h",
                side="positive",
                meanline_visible=True,
                width=1,
                name="distribution",
                hoveron="violins",
            )
        )
    fig.update_traces(points=False, spanmode="hard")
    fig.update_layout(
        title="Completed Tasks per Weekday",
        showlegend=False,
        xaxis=dict(tickmode="linear", tick0=1, dtick=1, showgrid=False),
    )
    fig.update_xaxes(rangemode="tozero")
    return fig


def task_completion_trend_plot(completed_tasks: DataFrame) -> FigureWidget:
    """
    Creates a line plot showing the trend of completed tasks over time with a moving average.

    Args:
        completed_tasks: DataFrame containing completed tasks data

    Returns:
        FigureWidget: Plotly figure object
    """
    # Group by date and count tasks
    daily_completed_tasks = (
        completed_tasks[["completed_date", "id"]]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )

    # Convert to datetime
    daily_completed_tasks["completed_date"] = pd.to_datetime(
        daily_completed_tasks["completed_date"]
    )

    # Sort by date
    daily_completed_tasks = daily_completed_tasks.sort_values("completed_date")

    # Calculate 7-day moving average
    daily_completed_tasks["7_day_avg"] = (
        daily_completed_tasks["id"].rolling(window=7, min_periods=1).mean()
    )

    # Create the figure
    fig = go.Figure()

    # Add daily tasks as a bar chart
    fig.add_trace(
        go.Bar(
            x=daily_completed_tasks["completed_date"],
            y=daily_completed_tasks["id"],
            name="Daily Tasks",
            marker_color="rgba(100, 149, 237, 0.5)",
            hovertemplate="<b>Date: %{x}</b><br>%{y} tasks completed",
        )
    )

    # Add 7-day moving average as a line
    fig.add_trace(
        go.Scatter(
            x=daily_completed_tasks["completed_date"],
            y=daily_completed_tasks["7_day_avg"],
            name="7-Day Average",
            line=dict(color="rgb(255, 165, 0)", width=3),
            hovertemplate="<b>Date: %{x}</b><br>%{y:.1f} tasks (7-day average)",
        )
    )

    # Update layout
    fig.update_layout(
        title="Task Completion Trend",
        xaxis_title="Date",
        yaxis_title="Number of Completed Tasks",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def task_completion_by_hour_plot(completed_tasks: DataFrame) -> FigureWidget:
    """
    Creates a heatmap showing when tasks are completed throughout the day.

    Args:
        completed_tasks: DataFrame containing completed tasks data

    Returns:
        FigureWidget: Plotly figure object
    """
    # Extract hour from completed_date
    completed_tasks["hour"] = pd.to_datetime(
        completed_tasks["completed_datehour"]
    ).dt.hour

    # Group by hour and count tasks
    hourly_completed_tasks = (
        completed_tasks[["hour", "id"]].groupby(["hour"], as_index=False).nunique()
    )

    # Create the figure
    fig = go.Figure()

    # Add hourly tasks as a bar chart
    fig.add_trace(
        go.Bar(
            x=hourly_completed_tasks["hour"],
            y=round(hourly_completed_tasks["id"] / 7),
            name="Tasks by Hour",
            marker_color="rgba(100, 149, 237, 0.7)",
            hovertemplate="<b>Hour: %{x}:00</b><br>%{y} tasks completed",
        )
    )

    # Update layout
    fig.update_layout(
        title="Task Completion by Hour of Day",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Completed Tasks",
        xaxis=dict(
            tickmode="array",
            ticktext=[f"{i:02d}:00" for i in range(24)],
            tickvals=list(range(24)),
        ),
    )

    return fig


def weekly_review_plot(
    completed_tasks: DataFrame, active_tasks: DataFrame
) -> FigureWidget:
    """
    Creates a comprehensive weekly review visualization showing past week's performance
    and planning for the upcoming week.

    Args:
        completed_tasks: DataFrame containing completed tasks data
        active_tasks: DataFrame containing active tasks data

    Returns:
        FigureWidget: Plotly figure object
    """
    # Convert dates to datetime
    completed_tasks["completed_date"] = pd.to_datetime(
        completed_tasks["completed_date"]
    )
    active_tasks["due"] = pd.to_datetime(active_tasks["due"])
    # Get the current date
    current_date = pd.Timestamp.now().normalize()

    # Calculate the start of the current week (Monday)
    start_of_week = current_date - pd.Timedelta(days=current_date.weekday())

    # Calculate the end of the current week (Sunday)
    end_of_week = start_of_week + pd.Timedelta(days=6)

    # Calculate the start of the previous week
    start_of_prev_week = start_of_week - pd.Timedelta(days=7)

    # Calculate the end of the previous week
    end_of_prev_week = start_of_week - pd.Timedelta(days=1)

    # Calculate the start of the next week
    start_of_next_week = start_of_week + pd.Timedelta(days=7)

    # Filter completed tasks for the previous week
    prev_week_completed = completed_tasks[
        (completed_tasks["completed_date"] >= start_of_prev_week)
        & (completed_tasks["completed_date"] <= end_of_prev_week)
    ]

    # Filter active tasks for the current and next week
    current_and_next_week_tasks = active_tasks[
        (active_tasks["due"] >= start_of_week)
        & (active_tasks["due"] <= start_of_next_week + pd.Timedelta(days=6))
    ]

    # Group completed tasks by project for the previous week
    prev_week_by_project = (
        prev_week_completed[["project_name", "id"]]
        .groupby(["project_name"], as_index=False)
        .nunique()
    )

    # Sort by number of tasks
    prev_week_by_project = prev_week_by_project.sort_values("id", ascending=False)

    # Group active tasks by project for the current and next week
    upcoming_by_project = (
        current_and_next_week_tasks[["project_name", "id"]]
        .groupby(["project_name"], as_index=False)
        .nunique()
    )

    # Sort by number of tasks
    upcoming_by_project = upcoming_by_project.sort_values("id", ascending=False)

    # Create a subplot with 2 rows and 1 column
    fig = go.Figure()

    # Add previous week's completed tasks by project
    fig.add_trace(
        go.Bar(
            y=prev_week_by_project["project_name"],
            x=prev_week_by_project["id"],
            name="Last Week Completed",
            orientation="h",
            marker_color="rgba(100, 149, 237, 0.7)",
            hovertemplate="<b>%{y}</b><br>%{x} tasks completed last week",
        )
    )

    # Add upcoming tasks by project
    fig.add_trace(
        go.Bar(
            y=upcoming_by_project["project_name"],
            x=upcoming_by_project["id"],
            name="Upcoming Tasks",
            orientation="h",
            marker_color="rgba(255, 165, 0, 0.7)",
            hovertemplate="<b>%{y}</b><br>%{x} tasks due this/next week",
        )
    )

    # Update layout
    fig.update_layout(
        title="Weekly Review: Project Focus",
        xaxis_title="Number of Tasks",
        yaxis_title="Project",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
    )

    return fig


def weekly_completion_trend_plot(completed_tasks: DataFrame) -> FigureWidget:
    """
    Creates a line plot showing the completion trend for the last 7 days and the next 7 days.

    Args:
        completed_tasks: DataFrame containing completed tasks data

    Returns:
        FigureWidget: Plotly figure object
    """
    # Convert dates to datetime
    completed_tasks["completed_date"] = pd.to_datetime(
        completed_tasks["completed_date"]
    )

    # Get the current date
    current_date = pd.Timestamp.now().normalize()

    # Calculate the start of the previous week
    start_of_prev_week = current_date - pd.Timedelta(weeks=1)

    # Filter completed tasks for the last 7 days
    last_7_days = completed_tasks[
        (completed_tasks["completed_date"] >= start_of_prev_week)
        & (completed_tasks["completed_date"] <= current_date)
    ]

    # Group by date and count tasks
    daily_completed_tasks = (
        last_7_days[["completed_date", "id", "hex_color"]]
        .groupby(["completed_date", "hex_color"], as_index=False)
        .nunique()
    )

    # Sort by date
    daily_completed_tasks = (
        daily_completed_tasks.groupby("completed_date", as_index=False)
        .sum()
        .sort_values("id", ascending=False)
    )

    # Create the figure
    fig = go.Figure()

    # Add daily tasks as a bar chart with hex colors
    fig.add_trace(
        go.Bar(
            x=daily_completed_tasks["completed_date"],
            y=daily_completed_tasks["id"],
            name="Completed Tasks",
            # marker_color=daily_completed_tasks["hex_color"],
            hovertemplate="<b>Date: %{x}</b><br>%{y} tasks completed",
        )
    )

    # Add a vertical line for today - using a shape instead of add_vline
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(
            color="red",
            width=1,
            dash="dash",
        ),
    )

    # Add annotation for the vertical line
    fig.add_annotation(
        x=current_date,
        y=1,
        yref="paper",
        text="Today",
        showarrow=False,
        font=dict(color="red"),
    )

    # Update layout
    fig.update_layout(
        title="Last 7 Days Completion Trend",
        xaxis_title="Date",
        yaxis_title="Number of Completed Tasks",
        hovermode="x",
        # legend=dict(
        #     orientation="h",
        #     yanchor="bottom",
        #     y=1.02,
        #     xanchor="right",
        #     x=1
        # ),
        height=400,
    )

    return fig


def analyze_weekly_pain_points(
    completed_tasks: DataFrame, active_tasks: DataFrame
) -> dict:
    """
    Analyzes task data to identify pain points and provide recommendations for the upcoming week.

    Args:
        completed_tasks: DataFrame containing completed tasks data
        active_tasks: DataFrame containing active tasks data

    Returns:
        dict: Dictionary containing pain points, recommendations, and detailed data for UI elements
    """
    # Convert dates to datetime
    completed_tasks["completed_date"] = pd.to_datetime(
        completed_tasks["completed_date"]
    )
    active_tasks["due"] = pd.to_datetime(active_tasks["due"])

    # Get the current date
    current_date = pd.Timestamp.now().normalize()

    # Calculate the start of the current week (Monday)
    start_of_week = current_date - pd.Timedelta(days=current_date.weekday())

    # Calculate the end of the current week (Sunday)
    end_of_week = start_of_week + pd.Timedelta(days=6)

    # Calculate the start of the previous week
    start_of_prev_week = start_of_week - pd.Timedelta(days=7)

    # Calculate the end of the previous week
    end_of_prev_week = start_of_week - pd.Timedelta(days=1)

    # Calculate the start of the next week
    start_of_next_week = start_of_week + pd.Timedelta(days=7)

    # Filter completed tasks for the previous week
    prev_week_completed = completed_tasks[
        (completed_tasks["completed_date"] >= start_of_prev_week)
        & (completed_tasks["completed_date"] <= end_of_prev_week)
    ]

    # Filter active tasks for the current and next week
    current_and_next_week_tasks = active_tasks[
        (active_tasks["due"] >= start_of_week)
        & (active_tasks["due"] <= start_of_next_week + pd.Timedelta(days=6))
    ]

    # Identify pain points and generate recommendations
    pain_points = []
    recommendations = []
    overdue_tasks_data = []
    weekend_tasks_data = []
    active_tasks_no_due_date_data = []

    # 1. Check for overdue tasks
    overdue_tasks = active_tasks[active_tasks["due"] < current_date]
    if len(overdue_tasks) > 0:
        pain_points.append(
            f"You have {len(overdue_tasks)} overdue tasks that need attention."
        )
        recommendations.append(
            "Consider reviewing and either completing or rescheduling overdue tasks."
        )

        # Prepare overdue tasks data for the dropdown
        for _, task in overdue_tasks.iterrows():
            overdue_tasks_data.append(
                {
                    "id": task["id"],
                    "content": task["content"],
                    "project_name": task["project_name"],
                    "due_date": task["due"].strftime("%Y-%m-%d"),
                    "days_overdue": (current_date - task["due"]).days,
                }
            )

    # 2. Check for high task load in the upcoming week using 7-day moving average
    # Calculate the 7-day moving average of completed tasks
    daily_completed_tasks = (
        completed_tasks[["completed_date", "id"]]
        .groupby(["completed_date"], as_index=False)
        .nunique()
    )

    # Sort by date
    daily_completed_tasks = daily_completed_tasks.sort_values("completed_date")

    # Calculate 7-day moving average
    daily_completed_tasks["7_day_avg"] = (
        daily_completed_tasks["id"].rolling(window=7, min_periods=1).mean()
    )

    # Get the most recent 7-day average
    recent_avg = (
        daily_completed_tasks["7_day_avg"].iloc[-1]
        if not daily_completed_tasks.empty
        else 0
    )

    # Count upcoming tasks
    upcoming_tasks = current_and_next_week_tasks[
        current_and_next_week_tasks["due"] >= current_date
    ]
    upcoming_count = len(upcoming_tasks)

    # Compare upcoming tasks with the 7-day moving average
    if (
        upcoming_count / (upcoming_tasks["due"].max() - current_date).days
        > recent_avg * 1.5
    ):  # 50% more than your average
        pain_points.append(
            f"You have {upcoming_count} tasks due in the next {int((upcoming_tasks['due'].max() - current_date).days)} days, which is significantly more than your usual workload of {int(recent_avg)} tasks per day."
        )
        recommendations.append(
            "Consider breaking down large tasks or delegating some work if possible."
        )
    elif (
        upcoming_count / (upcoming_tasks["due"].max() - current_date).days
        > recent_avg * 1.2
    ):  # 20% more than your average
        pain_points.append(
            f"You have {upcoming_count} tasks due in the next {int((upcoming_tasks['due'].max() - current_date).days)} days, which is slightly more than your usual workload of {int(recent_avg)} tasks per day."
        )
        recommendations.append(
            "Plan your time carefully to ensure you can handle this slightly increased workload."
        )
    else:
        pain_points.append(
            f"You have {upcoming_count} tasks due in the next {int((upcoming_tasks['due'].max() - current_date).days)} days, which is within your usual workload of {int(recent_avg)} tasks per day."
        )
        recommendations.append(
            "You seem to be managing your workload well. Keep up the good work!"
        )
    # 3. Check for project balance
    prev_week_by_project = (
        prev_week_completed[["project_name", "id"]]
        .groupby(["project_name"], as_index=False)
        .nunique()
    )

    upcoming_by_project = (
        current_and_next_week_tasks[["project_name", "id"]]
        .groupby(["project_name"], as_index=False)
        .nunique()
    )

    # Check if there's a significant shift in project focus
    if len(prev_week_by_project) > 0 and len(upcoming_by_project) > 0:
        top_prev_project = prev_week_by_project.iloc[0]["project_name"]
        top_upcoming_project = upcoming_by_project.iloc[0]["project_name"]

        if top_prev_project != top_upcoming_project:
            pain_points.append(
                f"Your focus is shifting from '{top_prev_project}' to '{top_upcoming_project}' this week."
            )
            recommendations.append(
                "Make sure this shift in focus is intentional and aligns with your priorities."
            )

    # 4. Check for weekend tasks
    weekend_tasks = upcoming_tasks[upcoming_tasks["due"].dt.weekday >= 5]
    if len(weekend_tasks) > 0:
        pain_points.append(f"You have {len(weekend_tasks)} tasks due on the weekend.")
        recommendations.append(
            "Consider if these weekend tasks could be completed earlier to give yourself a break."
        )

        # Prepare weekend tasks data for the dropdown
        for _, task in weekend_tasks.iterrows():
            weekend_tasks_data.append(
                {
                    "id": task["id"],
                    "content": task["content"],
                    "project_name": task["project_name"],
                    "due_date": task["due"].strftime("%Y-%m-%d"),
                    "day_of_week": task["due"].strftime("%A"),
                }
            )

    # 5. Check for task completion pattern
    if len(prev_week_completed) > 0:
        # Check if most tasks were completed at the end of the week
        end_of_week_tasks = prev_week_completed[
            prev_week_completed["completed_date"]
            >= end_of_prev_week - pd.Timedelta(days=2)
        ]
        if (
            len(end_of_week_tasks) / len(prev_week_completed) > 0.7
        ):  # More than 70% at end of week
            pain_points.append(
                "You tend to complete most tasks at the end of the week."
            )
            recommendations.append(
                "Consider distributing your workload more evenly throughout the week."
            )

    # 6. Check for active tasks with no due date
    active_tasks_no_due_date = active_tasks[active_tasks["due"].isna()]
    if len(active_tasks_no_due_date) > 0:
        pain_points.append(
            f"You have {len(active_tasks_no_due_date)} active tasks with no due date."
        )
        recommendations.append(
            "Consider setting a due date for these tasks to help you stay on track."
        )
        for _, task in active_tasks_no_due_date.iterrows():
            active_tasks_no_due_date_data.append(
                {
                    "id": task["id"],
                    "content": task["content"],
                    "project_name": task["project_name"],
                    "due_date": task["due"],
                }
            )

    # If no specific pain points were identified, provide general insights
    if not pain_points:
        pain_points.append(
            "No significant pain points identified from your recent task data."
        )
        recommendations.append(
            "Keep up the good work! Consider setting more challenging goals if you're consistently meeting your current ones."
        )

    return {
        "pain_points": pain_points,
        "recommendations": recommendations,
        "overdue_tasks": overdue_tasks_data,
        "weekend_tasks": weekend_tasks_data,
        "active_tasks_no_due_date": active_tasks_no_due_date_data,
    }


def generate_weekly_review_file(
    completed_tasks: DataFrame, active_tasks: DataFrame, plot_images: dict
) -> str:
    """
    Generates a structured weekly review file based on the template in week13.md.

    Args:
        completed_tasks: DataFrame containing completed tasks data
        active_tasks: DataFrame containing active tasks data
        plot_images: Dictionary containing SVG content for plots

    Returns:
        str: The content of the weekly review file
    """
    # Get the current date
    current_date = pd.Timestamp.now().normalize()

    # Calculate the start and end of the current week
    start_of_week = current_date - pd.Timedelta(days=current_date.weekday())
    end_of_week = start_of_week + pd.Timedelta(days=6)

    # Format the date range for the title
    start_date_str = start_of_week.strftime("%d/%b/%y")
    end_date_str = end_of_week.strftime("%d/%b/%y")

    # Get the week number
    week_number = current_date.isocalendar()[1]

    # Start building the weekly review content
    content = f"# Week {week_number} - {start_date_str} - {end_date_str}\n\n"

    # 1. Declutter and mind dump - 10 min
    content += "## Declutter and mind dump - 10 min\n"
    content += "```\n"
    content += "Tidy your workspace, file away your notes, and get all tasks out of your head and into your task management system\n"
    content += "```\n\n"

    # Add a placeholder for the user to fill in
    content += "Add your mind dump here...\n\n"

    # 2. Reflect on this past week - 10 min
    content += "## Reflect on this past week - 10 min\n"
    content += "```\n"
    content += "Review your completed tasks, calendar, notes and goals. Compare your plan to what actually happened. What went well? What didn't\n"
    content += "```\n\n"

    # Add completed tasks summary
    last_week_completed = completed_tasks[
        (completed_tasks["completed_date"] >= start_of_week - pd.Timedelta(days=7))
        & (completed_tasks["completed_date"] < start_of_week)
    ]

    if not last_week_completed.empty:
        content += "### Completed Tasks Summary\n"
        content += f"- Total tasks completed: {len(last_week_completed)}\n"

        # Group by project
        by_project = (
            last_week_completed.groupby("project_name")
            .size()
            .sort_values(ascending=False)
        )
        content += "- Tasks by project:\n"
        for project, count in by_project.items():
            content += f"  - {project}: {count} tasks\n"

        content += "\n"

        # Add a plot of completed tasks by project
        content += "#### Completed Tasks by Project\n"
        svg_content = plot_images.get("completed_tasks_by_project", "")
        b64 = base64.b64encode(svg_content).decode("utf-8")
        content += f"![Completed Tasks by Project](data:image/svg+xml;base64,{b64})\n\n"

    # Add a placeholder for the user to fill in
    content += "Add your reflection here...\n\n"

    # 3. Get current on goals & projects - 15 min
    content += "## Get current on goals & projects - 15 min\n"
    content += "```\n"
    content += "What progress have you made on each of your top priorities? What needs to be updated? What needs to happen next?\n"
    content += "```\n\n"

    # Add active tasks summary
    if not active_tasks.empty:
        content += "### Current Active Tasks\n"
        content += f"- Total active tasks: {len(active_tasks)}\n"

        # Group by project
        by_project = (
            active_tasks.groupby("project_name").size().sort_values(ascending=False)
        )
        content += "- Tasks by project:\n"
        for project, count in by_project.items():
            content += f"  - {project}: {count} tasks\n"

        content += "\n"

        # Add a plot of active tasks by project
        content += "#### Active Tasks by Project\n"
        svg_content = plot_images.get("active_tasks_by_project", "")
        b64 = base64.b64encode(svg_content).decode("utf-8")
        content += f"![Active Tasks by Project](data:image/svg+xml;base64,{b64})\n\n"

        # Add tasks with no due date summary
        tasks_no_due_date = active_tasks[active_tasks["due"].isna()]
        if not tasks_no_due_date.empty:
            content += "### Tasks with No Due Date\n"
            content += f"- Total tasks with no due date: {len(tasks_no_due_date)}\n"

            # Group by project
            no_due_by_project = (
                tasks_no_due_date.groupby("project_name")
                .size()
                .sort_values(ascending=False)
            )
            content += "- Tasks by project:\n"
            for project, count in no_due_by_project.items():
                content += f"  - {project}: {count} tasks\n"
    # Add a placeholder for the user to fill in
    content += "Add your goals and projects update here...\n\n"

    # 4. Plan the week ahead - 15 min
    content += "## Plan the week ahead - 15 min\n"
    content += "```\n"
    content += "What are your most important tasks and events each day of this week? Write them down\n"
    content += "```\n\n"

    # Add upcoming tasks summary
    upcoming_tasks = active_tasks[
        (active_tasks["due"] >= start_of_week) & (active_tasks["due"] <= end_of_week)
    ]

    if not upcoming_tasks.empty:
        content += "### Upcoming Tasks This Week\n"
        content += f"- Total tasks due this week: {len(upcoming_tasks)}\n"

        # Group by day of week
        upcoming_tasks["day_of_week"] = pd.to_datetime(
            upcoming_tasks["due"]
        ).dt.day_name()
        by_day = (
            upcoming_tasks.groupby("day_of_week").size().sort_values(ascending=False)
        )
        content += "- Tasks by day:\n"
        for day, count in by_day.items():
            content += f"  - {day}: {count} tasks\n"

        content += "\n"

        # Add a plot of upcoming tasks by day
        content += "#### Upcoming Tasks by Day\n"
        svg_content = plot_images.get("upcoming_tasks_by_day", "")
        b64 = base64.b64encode(svg_content).decode("utf-8")
        content += f"![Upcoming Tasks by Day](data:image/svg+xml;base64,{b64})\n\n"

    # Add placeholders for each day of the week
    for i in range(7):
        day = start_of_week + pd.Timedelta(days=i)
        day_name = day.strftime("%A")
        content += f"### {day_name}\n"
        content += "- [ ] \n\n"

    content += "### If it fits\n\n"
    content += "### Next week\n\n"

    # 5. Think bigger - 10 min
    content += "## Think bigger - 10 min\n"
    content += "```\n"
    content += 'Review your "someday maybe" projects list. What things are you excited about right now? What new things do you want to learn?\n'
    content += "```\n\n"

    # Add a placeholder for the user to fill in
    content += "Add your bigger thinking here...\n\n"

    # 6. Add task completion trend
    content += "## Task Completion Trend\n"
    svg_content = plot_images.get("task_completion_trend", "")
    b64 = base64.b64encode(svg_content).decode("utf-8")
    content += f"![Task Completion Trend](data:image/svg+xml;base64,{b64})\n\n"

    # 7. Add task completion trend for 30 days
    content += "## Task Completion Trend for 30 days\n"
    svg_content = plot_images.get("task_completion_trend_30_days", "")
    b64 = base64.b64encode(svg_content).decode("utf-8")
    content += (
        f"![Task Completion Trend for 30 days](data:image/svg+xml;base64,{b64})\n\n"
    )

    # 8. Add weekly review visualization
    content += "## Weekly Review Visualization\n"
    svg_content = plot_images.get("weekly_review", "")
    b64 = base64.b64encode(svg_content).decode("utf-8")
    content += f"![Weekly Review](data:image/svg+xml;base64,{b64})\n\n"

    return content
