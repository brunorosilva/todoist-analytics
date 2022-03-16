import streamlit as st
from PIL import Image

from todoist_analytics.backend.auth import run_auth
from todoist_analytics.backend.utils import (create_color_palette, get_data,
                                             get_more_data, get_n_calls)
from todoist_analytics.credentials import client_id, client_secret
from todoist_analytics.frontend.filters import (date_filter, last_month_filter,
                                                last_seven_days_filter,
                                                last_week_filter,
                                                last_year_filter,
                                                project_filter, weekend_filter)
from todoist_analytics.frontend.habit_tracker import (filter_recurrent_task,
                                                      get_recurrent_tasks)
from todoist_analytics.frontend.plots import (
    calendar_habits_plot, calendar_task_plot, completed_tasks_per_day,
    completed_tasks_per_day_per_project, create_metrics_cards,
    day_of_week_ridgeline_plot, each_project_total_percentage_plot,
    one_hundred_stacked_bar_plot_per_project)

from todoist_analytics.credentials import client_id, client_secret


def run_setup():
    todoist_logo = Image.open("assets/images/todoist_logo.png")
    st.set_page_config(
        page_title="Todoist Analytics", layout="wide", page_icon=todoist_logo
    )
    st.title("Todoist Analytics Report")

    # token = run_auth(client_id=client_id, client_secret=client_secret)
    token = client_secret
    return token

def start_data_job(token):
    if token is not None:
        with st.spinner("Getting your data :)"):
            completed_tasks, active_tasks, dc = get_data(token)
            completed_tasks_habits = completed_tasks.copy()
        return completed_tasks, completed_tasks_habits, active_tasks, dc

def start_get_more_data_job(token, dc):
    if token is not None:
        with st.spinner("Getting more data!"):
            sing = get_n_calls()
            sing.n_calls += 1
            print("Ncalls is", str(sing.n_calls))
            completed_tasks, active_tasks = get_more_data(
                dc, n_calls=sing.n_calls
            )
            completed_tasks_habits = completed_tasks.copy()

        return completed_tasks, completed_tasks_habits, active_tasks, dc

def create_filters(completed_tasks):
    completed_tasks = date_filter(completed_tasks, "date range filter")
    completed_tasks = last_week_filter(completed_tasks, "filter current week")
    completed_tasks = last_seven_days_filter(
        completed_tasks, "filter last seven days"
    )
    completed_tasks = last_month_filter(completed_tasks, "filter current month")
    completed_tasks = last_year_filter(completed_tasks, "filter current year")
    completed_tasks, remove_weekends = weekend_filter(
        completed_tasks, "remove weekends"
    )
    completed_tasks = project_filter(completed_tasks, "select the desired project")
    return completed_tasks, remove_weekends

def render_plots(completed_tasks, remove_weekends):
    create_metrics_cards(completed_tasks, list(st.columns(4)), remove_weekends)

    st.markdown(
        f"Analyzing data since {completed_tasks.completed_date.min()} until {completed_tasks.completed_date.max()}"
    )

    completed_tasks_radio = st.radio("Choose your view", ["total", "per project"])

    color_palette = create_color_palette(completed_tasks)

    figs = []
    if completed_tasks_radio == "total":
        figs.append(completed_tasks_per_day(completed_tasks))
    else:

        figs.append(
            completed_tasks_per_day_per_project(completed_tasks, color_palette)
        )

    figs.append(
        one_hundred_stacked_bar_plot_per_project(completed_tasks, color_palette)
    )

    figs.append(each_project_total_percentage_plot(completed_tasks, color_palette))

    figs.append(calendar_task_plot(completed_tasks))

    figs.append(day_of_week_ridgeline_plot(completed_tasks))

    if remove_weekends:
        for fig in figs:
            fig.update_xaxes(
                rangebreaks=[
                    {"pattern": "day of week", "bounds": [6, 1]},
                ]
            )

    for fig in figs:
        st.plotly_chart(fig, use_container_width=True)

def render_habits_components(completed_tasks_habits):
    st.markdown("# Habit Tracking")
    st.markdown("The side panel filters do not affect this section")

    recurrent_tasks = get_recurrent_tasks(completed_tasks_habits)
    completed_tasks_habits = filter_recurrent_task(
        completed_tasks_habits, recurrent_tasks
    )
    st.plotly_chart(
        calendar_habits_plot(completed_tasks_habits), use_container_width=True
    )

def create_app():
    token = run_setup()
    sing = get_n_calls()
    get_more_data_button = st.sidebar.button("Click here to get more of your data")
    if sing.n_calls == 1:
        completed_tasks, completed_tasks_habits, active_tasks, dc = start_data_job(token)
    elif get_more_data_button and sing.n_calls > 1:
        completed_tasks, completed_tasks_habits, active_tasks, dc = start_get_more_data_job(dc)
    completed_tasks, remove_weekends = create_filters(completed_tasks)
    render_plots(completed_tasks, remove_weekends)
    render_habits_components(completed_tasks_habits)


if __name__ == "__main__":
    app = create_app()
