import streamlit as st
from src.session import run_auth
from src.data import DataCollector
from PIL import Image


@st.cache(show_spinner=False)
def get_data(token):
    dc = DataCollector(token)
    return dc.tasks, dc.user


def is_data_ready():
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")
    image = Image.open('img/analytics_logo_300x300.png')
    st.sidebar.image(image, caption='An app to track your tasks, habits and more.')

    # Check if user is authenticated and load data
    if 'data_loaded' not in st.session_state:
        token = run_auth()

        if token is not None:
            with st.spinner("Getting your data :)"):
                tasks, user = get_data(token)
                st.session_state["tasks"] = tasks
                st.session_state["user"] = user
                st.session_state["data_loaded"] = True
                st.info("Your data is loaded, you can start using this app now.")

    # If user is authenticated, return True
    return 'data_loaded' in st.session_state
