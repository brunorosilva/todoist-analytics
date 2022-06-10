import streamlit as st
from PIL import Image
from todoist_analytics.backend.auth import run_auth
from todoist_analytics.backend.utils import get_data
from todoist_analytics.credentials import client_id, client_secret
from todoist_analytics.frontend import habits, overview


# Object to store all the apps
class MultiApp:
    def __init__(self):
        self.apps = []
        self.token = run_auth(client_id=client_id, client_secret=client_secret)

        if self.token is not None:
            with st.spinner("Getting your data :)"):
                completed_tasks, active_tasks = get_data(self.token)
                st.session_state["completed_tasks"] = completed_tasks
                st.session_state["active_tasks"] = active_tasks
                st.session_state["data_loaded"] = True

    # Adds a new application to the list
    # title: title of the app. Appears in the dropdown in the sidebar.
    # function: the python function to render the app.
    def add_page(self, title, function):
        self.apps.append({"title": title,
                          "function": function})

    # Renders a radio menu with all the apps
    # message: message to display above the radio menu
    # returns the function of the selected app
    def menu(self, message):
        current_app = st.radio(message, self.apps, format_func=lambda application: application['title'])
        return current_app['function']


if __name__ == "__main__":
    # Set page config
    logo = Image.open("assets/images/todoist_logo.png")
    st.set_page_config(page_title="Todoist Analytics", layout="wide", page_icon=logo)

    # Create multiapp
    multi_app = MultiApp()

    # Add all your application here
    multi_app.add_page("Overview", overview.render)
    multi_app.add_page("Habit Tracker", habits.render)

    # Add menu once the data is loaded
    if 'data_loaded' in st.session_state:
        # Add the menu to the sidebar
        with st.sidebar:
            st.title("Choose a view")
            render_page = multi_app.menu("Pages")

        # Render the selected app
        render_page()
