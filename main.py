import streamlit as st
from PIL import Image
from src.backend.auth import run_auth
from src.backend.utils import get_data
from src.credentials import client_id, client_secret


if __name__ == "__main__":

    # Set page config
    logo = Image.open("img/analytics_logo_300x300.png")
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon=logo)

    st.title("Welcome to Todoist Analytics")
    st.write("This is a simple app to track your habits.")

    token = run_auth(client_id=client_id, client_secret=client_secret)

    if token is not None:
        with st.spinner("Getting your data :)"):
            completed_tasks, active_tasks = get_data(token)
            st.session_state["completed_tasks"] = completed_tasks
            st.session_state["active_tasks"] = active_tasks
            st.session_state["data_loaded"] = True

    # Add message once the data is loaded
    if 'data_loaded' in st.session_state:
        st.info("Your data is loaded, you can start using this app now.")
