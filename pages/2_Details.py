import streamlit as st


def render():
    st.title("Details Page")


if __name__ == "__main__":
    if 'data_loaded' in st.session_state:
        render()
    else:
        st.write("Go back to the [homepage](/) and load your data first.")
