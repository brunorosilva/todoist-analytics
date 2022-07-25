import streamlit as st
from src.auth import run_auth
from src.data import get_data


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    st.title("Welcome to Todoist Analytics")
    st.write("This is a simple app to track your habits.")

    token = run_auth()
    if token is not None:
        with st.spinner("Getting your data :)"):
            completed_tasks, active_tasks = get_data(token)
            st.session_state["completed_tasks"] = completed_tasks
            st.session_state["active_tasks"] = active_tasks
            st.session_state["data_loaded"] = True

    # Add message once the data is loaded
    if 'data_loaded' in st.session_state:
        st.info("Your data is loaded, you can start using this app now.")
