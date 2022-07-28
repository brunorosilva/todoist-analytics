import pandas as pd
import streamlit as st
from src.auth import run_auth
from src.data import get_data


def render():
    st.title("Welcome to Todoist Analytics")
    st.write("This is a simple app to track your habits.")
    st.info("Your data is loaded, you can start using this app now.")

    # Filter projects dataframe
    projects = st.session_state.get("projects", pd.DataFrame()).copy()  # copy to not change cached data
    projects.drop_duplicates(inplace=True)
    projects["project_name"] = projects["name"]

    # completed_tasks["datehour_completed"] = pd.to_datetime(completed_tasks["completed_date"])
    # completed_tasks["datehour_completed"] = pd.DatetimeIndex(completed_tasks["datehour_completed"]).tz_convert(self.tz)
    # completed_tasks["completed_date"] = pd.to_datetime(completed_tasks["datehour_completed"]).dt.date
    # completed_tasks["completed_date_weekday"] = pd.to_datetime(completed_tasks["datehour_completed"]).dt.day_name()
    # completed_tasks = completed_tasks.merge(projects[["project_id", "name", "color"]],
    #                                         how="left",
    #                                         left_on="project_id",
    #                                         right_on="project_id")
    #
    # completed_tasks = completed_tasks.rename({"name": "project_name"}, axis=1)
    #
    # # creating the recurrent flag column -> not good implementation
    # completed_date_count = completed_tasks.groupby("task_id").agg({"completed_date": "nunique"})
    # completed_date_count["isRecurrent"] = np.where(completed_date_count["completed_date"] > 1, 1, 0)
    # completed_date_count.drop(columns="completed_date", inplace=True)
    # completed_tasks = completed_tasks.merge(completed_date_count, left_on="task_id", right_index=True)
    # completed_tasks["hex_color"] = completed_tasks["color"].apply(lambda x: color_code_to_hex[int(x)]["hex"])
    # completed_tasks = completed_tasks.drop_duplicates().reset_index(drop=True)

    # Filter and enrich completed tasks dataframe
    completed_tasks = st.session_state.get("completed_tasks", pd.DataFrame()).copy()  # copy to not change cached data
    completed_tasks = completed_tasks.merge(projects[["id", "project_name", "color"]],
                                            how="left",
                                            left_on="project_id",
                                            right_on="id",
                                            suffixes=("", "_project"))
    completed_tasks.drop(["project_id", "id_project", "meta_data", "user_id"], axis=1, inplace=True)

    st.header("Completed tasks")
    st.dataframe(completed_tasks)

    # Filter and enrich active tasks dataframe
    active_tasks = st.session_state.get("active_tasks", pd.DataFrame()).copy()  # copy to not change cached data
    active_tasks = active_tasks[active_tasks["checked"] == 0]
    active_tasks = active_tasks[active_tasks["in_history"] == 0]
    active_tasks = active_tasks[active_tasks["is_deleted"] == 0]
    dropped_columns = ["added_by_uid", "assigned_by_uid", "checked", "child_order", "collapsed", "date_completed",
                       "day_order", "has_more_notes", "in_history", "is_deleted", "responsible_uid", "parent_id",
                       "user_id", "sync_id"]
    possible_for_later = ["section_id", "labels"]
    active_tasks.drop(dropped_columns, axis=1, inplace=True)
    active_tasks.drop(possible_for_later, axis=1, inplace=True)

    st.header("Active tasks")
    st.dataframe(active_tasks)


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    if 'data_loaded' not in st.session_state:
        token = run_auth()
        if token is not None:
            with st.spinner("Getting your data :)"):
                completed_tasks, active_tasks, projects = get_data(token)
                st.session_state["completed_tasks"] = completed_tasks
                st.session_state["active_tasks"] = active_tasks
                st.session_state["projects"] = projects
                st.session_state["data_loaded"] = True

    if 'data_loaded' in st.session_state:
        render()
