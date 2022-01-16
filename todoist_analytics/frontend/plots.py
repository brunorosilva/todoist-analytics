from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from pandas import DataFrame
from plotly.missing_ipywidgets import FigureWidget
from plotly_calplot import calplot

from ..backend.utils import safe_divide


def create_metrics_cards(completed_tasks: DataFrame, cols: list, remove_weekends: bool):
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
    if remove_weekends:
        cols[3].metric(
            "tasks per day",
            int(
                round(
                    safe_divide(
                        len(completed_tasks),
                        (
                            (
                                np.busday_count(
                                    completed_tasks["completed_date"].min(),
                                    completed_tasks["completed_date"].max(),
                                )
                            )
                            + 1
                        ),
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
    completed_tasks: DataFrame, color_palette: dict
) -> FigureWidget:

    daily_completed_tasks_per_project = (
        completed_tasks[["project_id", "id", "project_name", "content", "hex_color"]]
        .groupby(["project_name", "hex_color"], as_index=False)
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

    # this is lazy code writing, the right way to do this
    # is to use graph_objects Bars (in loop) with texttemplate
    # in order to add a percent sign after the value, but as
    # I'm using plotly express, this is lazy way is much easier
    daily_completed_tasks_per_project["pct_of_total_str"] = (
        daily_completed_tasks_per_project["pct_of_total"].astype(str) + " %"
    )

    # TODO - add this plot to the above one as a subplot
    # TODO - change from express to graph objects
    fig = px.bar(
        daily_completed_tasks_per_project,
        x="pct_of_total",
        y="project_id",
        text="pct_of_total_str",
        orientation="h",
        color="project_name",
        hover_data=["id"],
        hover_name="project_name",
        labels={
            "pct_of_total": "% of total tasks",
            "project_id": "",
            "project_name": "Project",
            "id": "tasks amount",
        },
        color_discrete_sequence=daily_completed_tasks_per_project["hex_color"],
    )
    fig.update_traces(textposition="inside")
    fig.update_layout(title_text="Percentage of tasks per project")
    fig.update_yaxes(visible=False)
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
