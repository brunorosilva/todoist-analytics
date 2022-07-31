import streamlit as st
from src.utils import is_data_ready


def render():
    st.title("Details Page")
    st.header("Under construction")


if __name__ == "__main__":
    if is_data_ready():
        render()
