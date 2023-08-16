import asyncio

import requests
import streamlit as st


async def get_auth(client_id, client_secret):

    authorization_url = f"https://todoist.com/oauth/authorize?client_id={client_id}&scope=data:read&state={client_secret}"
    st.markdown(authorization_url)
    return authorization_url


async def get_token(client_id, client_secret, code):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }
    token = requests.post(f"https://todoist.com/oauth/access_token", data=data)
    token = token.json()["access_token"]
    return token


def run_auth(client_id, client_secret):

    # auth stuff
    auth_url = asyncio.run(get_auth(client_id, client_secret))
    session = st.session_state

    if "token" not in session:
        try:
            code = st.experimental_get_query_params()["code"]
        except:
            st.write(
                f"""<h1>
            Please login using this <a target="_self"
            href="{auth_url}">url</a></h1>""",
                unsafe_allow_html=True,
            )
        else:
            try:
                token = asyncio.run(get_token(client_id, client_secret, code=code))
            except:
                st.write(
                    f"""<h1>
                    This page was refreshed.
                    Please allow again: <a target="_self"
                    href="{auth_url}">url</a></h1>""",
                    unsafe_allow_html=True,
                )
            else:
                session.token = token
                return session.token

    else:
        return session.token
    # end auth
