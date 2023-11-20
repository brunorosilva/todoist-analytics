from pandas import DataFrame
from streamlit import multiselect


def get_recurrent_tasks(completed_tasks_habits) -> list:
    completed_tasks_habits = completed_tasks_habits.sort_values(
        "completed_date", ascending=False
    )
    recurrent_tasks = (
        completed_tasks_habits.loc[completed_tasks_habits["isRecurrent"] == 1][
            "content"
        ]
        .unique()
        .tolist()
    )

    return recurrent_tasks


def filter_recurrent_task(completed_tasks_habits, recurrent_tasks) -> DataFrame:
    selected_habits = multiselect(
        "Select one or more recurrent tasks, your most recent tasks should apper first",
        recurrent_tasks,
    )

    if len(selected_habits) > 0:
        completed_tasks_habits = completed_tasks_habits.loc[
            (completed_tasks_habits["content"].isin(selected_habits))
        ]
    return completed_tasks_habits
