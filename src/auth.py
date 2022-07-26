import asyncio
import requests
import streamlit as st
from src import session_state
from src.credentials import client_id, client_secret


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
    session = session_state.get(token=None)

    # If a token is found return it
    if session.token:
        return session.token

    # Check if code is present in the query parameters
    params = st.experimental_get_query_params()
    code = params.get("code")

    # If no code is found send the user to login using
    if not code:
        st.write(f"""<h2>Please login using this <a target="_self" href="{auth_url}">url</a></h2>""",
                 unsafe_allow_html=True)
    else:
        token = asyncio.run(get_token(code=code))

        if token:
            return token

        st.write(f"""<h2>Page refreshed, please allow again: <a target="_self" href="{auth_url}">url</a></h2>""",
                 unsafe_allow_html=True)
