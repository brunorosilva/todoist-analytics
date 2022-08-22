from datetime import date, timedelta
import pandas as pd
import streamlit as st
from src.utils import is_data_ready


def expandable_with_tasks(task_list, day, expanded=False):
    today = date.today()
    day_goal = st.session_state["user"].get("daily_goal", 0)

    if day < today:
        emoji = "🏆" if task_list.shape[0] > day_goal else "❌"
    elif day == today:
        emoji = "🏆" if task_list["completed_date"].notnull().shape[0] > day_goal else "⌛"
    else:
        emoji = "⌛" if task_list.shape[0] <= day_goal else "➖"

    with st.expander(day.strftime('%A') + " " + emoji + " (" + str(task_list.shape[0]) + ")", expanded=expanded):
        for completed, task in zip(task_list["due_date"].apply(lambda x: x is pd.NaT).tolist(),
                                   task_list["content"].tolist()):
            if completed:
                st.markdown("✔ " + task)
            elif emoji == "🏆":
                st.markdown("➖ " + task)
            else:
                st.markdown("⌛ " + task)


def render():
    # Get tasks
    st.title("Planing")
    tasks = st.session_state["tasks"].copy()

    # Symbols
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Completed", "🏆")
    col2.metric("Failed", "❌")
    col3.metric("Pending", "⌛")
    col4.metric("Done", "✔")
    col5.metric("Extra tasks", "➖")
    col6.metric("Suggestions", "💡")

    # Combine due date and completed date
    week_tasks = tasks.copy()
    week_tasks["date"] = tasks.apply(lambda x: x["due_date"] if x["completed_date"] is pd.NaT else x["completed_date"],
                                     axis=1)

    # Start day and today
    today = date.today()
    start_day = 8 - st.session_state["user"].get("start_day", 1)

    # Get week and year of tasks
    week_tasks["week"] = week_tasks["date"].dt.date.map(lambda x: None if pd.isnull(x) else (x + timedelta(
        days=start_day)).isocalendar()[1])
    week_tasks["year"] = week_tasks["date"].apply(lambda x: x.year).astype('Int64').fillna(0)

    # Filter tasks of the week
    week_tasks = week_tasks[week_tasks["year"] == today.year]
    week_tasks = week_tasks[week_tasks["week"] == today.isocalendar()[1]]
    week_tasks = week_tasks.sort_values(by=["completed_date", "due_date"])

    # Layout of page
    other_col, now_col, suggestions_col = st.columns([1, 2, 1])

    # Group by day in expanders
    for day in week_tasks["date"].apply(lambda x: x.date).unique():
        tasks_in_the_day = week_tasks[week_tasks["date"].apply(lambda x: x.strftime('%A')) == day.strftime('%A')]

        if today == day:
            with now_col:
                expandable_with_tasks(tasks_in_the_day, day, expanded=True)
        else:
            with other_col:
                expandable_with_tasks(tasks_in_the_day, day)

    # Suggestions
    suggestions = tasks.copy()
    suggestions = suggestions[suggestions["completed_date"].isnull()]
    suggestions = suggestions[suggestions["due_date"].isnull()]

    # Rank projects
    st.sidebar.subheader("Rank each project to get suggestions")
    projects = set(suggestions["project_name"].unique())
    sort_project = {}
    for i in range(1, len(projects) + 1):
        project = st.sidebar.selectbox(f"Rank {i}", projects)
        sort_project[project] = i
        projects.remove(project)

    # Rank by age and project
    suggestions["age"] = (date.today() - suggestions["added_date"].dt.date).dt.days
    suggestions["rank"] = (suggestions["age"].max() - suggestions["age"])/suggestions["age"].max() + \
        suggestions["project_name"].map(sort_project)/len(sort_project)
    suggestions = suggestions.sort_values(by=["priority", "rank", "added_date"], ascending=[False, True, True])

    # Display suggestions
    with suggestions_col:
        tasks_left = st.session_state["user"].get("weekly_goal", 0) - week_tasks.shape[0]
        suggestion_list = st.expander("Suggestions 💡", expanded=True)
        more_suggestions = st.expander("More suggestions 💡")

        if tasks_left <= 0:
            tasks_left = 0
            suggestion_list.write("🏆 Great you have planned your week!")

        suggestions = suggestions.head(tasks_left + 10)

        for i, (task_id, content) in enumerate(zip(suggestions["task_id"], suggestions["content"])):
            if i < tasks_left:
                suggestion_list.write("💡 " + content + f" [→ see in todoist](https://todoist.com/app/task/{task_id})")
            else:
                more_suggestions.write("💡 " + content + f" [→ see in todoist](https://todoist.com/app/task/{task_id})")


if __name__ == "__main__":
    if is_data_ready():
        render()
