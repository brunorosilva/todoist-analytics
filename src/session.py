import asyncio
import requests
import streamlit as st
from streamlit.scriptrunner import get_script_run_ctx
from streamlit.server.server import Server
from src.credentials import client_id, client_secret


# SessionState class that has all the information
# Credits to https://github.com/uiucanh/streamlit-google-oauth
class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


# Get function to get any value from session state
# Credits to https://github.com/uiucanh/streamlit-google-oauth
def get_session_state(**kwargs):
    ctx = get_script_run_ctx()
    this_session = None

    session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if not hasattr(s, "_main_dg") and s._uploaded_file_mgr == ctx.uploaded_file_mgr:
            this_session = s

    if this_session is None:
        raise RuntimeError("Oh noes. Couldn't get your Streamlit Session object. "
                           "Are you doing something fancy with threads?")

    # Got the session object! Now let's attach some state into it.
    if not hasattr(this_session, "_custom_session_state"):
        this_session._custom_session_state = SessionState(**kwargs)

    return this_session._custom_session_state


# Gets the token from todoist oauth
async def get_token(code):
    # Post requests for access token
    data = {"client_id": client_id,
            "client_secret": client_secret,
            "code": code}
    response = requests.post("https://todoist.com/oauth/access_token", data=data).json()

    # Check if response return an error message and return accordingly
    if response.get("error") is None:
        return response.get("access_token")
    else:
        return None


# Runs the authorization and returns the token or
def run_auth():
    # Get session token from auth url
    auth_url = f"https://todoist.com/oauth/authorize?client_id={client_id}&scope=data:read&state={client_secret}"
    session = get_session_state(token=None)

    # If a token is found return it
    if session.token:
        return session.token

    # Check if code is present in the query parameters
    params = st.experimental_get_query_params()
    code = params.get("code")

    if not code:
        st.title("Welcome to Todoist analytics")
        st.write(f"""<h2>Please login using this <a target="_self" href="{auth_url}">url</a></h2>""",
                 unsafe_allow_html=True)
    else:
        token = asyncio.run(get_token(code=code))

        if token:
            return token

        st.write(f"""<h1>Page refreshed</h1>
                 <h2>Please allow again: <a target="_self" href="{auth_url}">url</a></h2>""",
                 unsafe_allow_html=True)
