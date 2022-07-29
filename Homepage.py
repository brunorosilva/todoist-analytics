import pandas as pd
import streamlit as st
from src.auth import run_auth
from src.data import get_data


def render():
    # Print welcome message
    st.title("Welcome to Todoist Analytics")
    st.caption("This is a simple app to track your habits.")

    st.header("Tasks")
    tasks = st.session_state["tasks"].copy()
    st.write(tasks)
    st.write(tasks.dtypes.astype(str))

    st.header("user")
    st.write(st.session_state["user"])


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    if 'data_loaded' not in st.session_state:
        token = run_auth()

        if token is not None:
            with st.spinner("Getting your data :)"):
                tasks, user = get_data(token)
                st.session_state["tasks"] = tasks
                st.session_state["user"] = user
                st.session_state["data_loaded"] = True
                st.info("Your data is loaded, you can start using this app now.")

    if 'data_loaded' in st.session_state:
        render()
