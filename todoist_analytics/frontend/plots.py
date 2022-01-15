import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from pandas import DataFrame
from plotly.missing_ipywidgets import FigureWidget
from plotly.subplots import make_subplots
from plotly_calplot import calplot


def create_metrics_cards(completed_tasks: DataFrame, cols: list, remove_weekends: bool):
    cols[0].metric("completed tasks", len(completed_tasks.drop_duplicates()))
    cols[1].metric("projects", completed_tasks.project_id.nunique())
    cols[2].metric(
        "tasks last 7 days",
        len(
            completed_tasks.loc[
                (
                    completed_tasks["completed_date"]
                    >= completed_tasks["completed_date"].max() - timedelta(days=7)
                )
            ].drop_duplicates()
        ),
    )
    if remove_weekends:
        cols[3].metric(
            "tasks per day",
            int(
                round(
                    len(completed_tasks.drop_duplicates())
                    / (
                        (
                            np.busday_count(
                                completed_tasks["completed_date"].min(),
                                completed_tasks["completed_date"].max(),
                            )
                        )
                    ),
                    0,
                ),
            ),
        )
    else:
        cols[3].metric(
            "tasks per day",
            int(
                round(
                    len(completed_tasks.drop_duplicates())
                    / (
                        (
                            (
                                completed_tasks["completed_date"].max()
                                - completed_tasks["completed_date"].min()
                            ).days
                        )
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
            name="project_id",
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
        hover_name="project_id",
        color_discrete_map=color_palette,
    )
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
                x=aux.index, y=aux[project], name=project, marker_color=project_color
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
    )
    fig.update_layout(
        paper_bgcolor=("#0e1117"),
        plot_bgcolor=("#0e1117"),
    )
    return fig
