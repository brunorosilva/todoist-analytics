import streamlit as st
from src.auth import run_auth
from src.data import get_data


def render():
    st.title("Welcome to Todoist Analytics")
    st.write("This is a simple app to track your habits.")
    st.info("Your data is loaded, you can start using this app now.")


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    if 'data_loaded' not in st.session_state:
        token = run_auth()
        if token is not None:
            with st.spinner("Getting your data :)"):
                completed_tasks, active_tasks = get_data(token)
                st.session_state["completed_tasks"] = completed_tasks
                st.session_state["active_tasks"] = active_tasks
                st.session_state["data_loaded"] = True

    if 'data_loaded' in st.session_state:
        render()
