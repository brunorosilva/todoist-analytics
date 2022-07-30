import streamlit as st
from src.utils import is_data_ready


def render():
    st.title("Habit Tracking")
    st.header("Under construction")


if __name__ == "__main__":
    # Set page config
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon="📊")

    if is_data_ready():
        render()
