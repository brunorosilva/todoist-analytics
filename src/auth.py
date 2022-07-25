import asyncio
import requests
import streamlit as st
from src import session_state
from src.credentials import client_id, client_secret


async def get_auth(client_id, client_secret):
    authorization_url = f"https://todoist.com/oauth/authorize?" \
                        f"client_id={client_id}&" \
                        f"scope=data:read&state={client_secret}"
    return authorization_url


async def get_token(client_id, client_secret, code):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }
    token = requests.post("https://todoist.com/oauth/access_token", data=data)
    token = token.json()["access_token"]
    return token


def run_auth():

    # auth stuff
    auth_url = asyncio.run(get_auth(client_id, client_secret))
    session = session_state.get(token=None)

    if session.token is None:
        try:
            code = st.experimental_get_query_params()["code"]
        except:
            st.write(f"""<h2>Please login using this <a target="_self" href="{auth_url}">url</a></h2>""",
                     unsafe_allow_html=True)
        else:
            try:
                token = asyncio.run(get_token(client_id, client_secret, code=code))
            except:
                st.write(
                    f"""<h2>
                    This page was refreshed.
                    Please allow again: <a target="_self"
                    href="{auth_url}">url</a></h2>""",
                    unsafe_allow_html=True,
                )
            else:
                session.token = token
                return session.token

    else:
        return session.token
    # end auth
