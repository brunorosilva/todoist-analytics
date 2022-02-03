import urllib
import streamlit as st
from oauthlib.oauth2 import WebApplicationClient
import requests
import asyncio



async def get_auth(client_id, client_secret):

    authorization_url = f"https://todoist.com/oauth/authorize?client_id={client_id}&scope=data:read&state={client_secret}"
    # res = requests.get(authorization_url)
    print(authorization_url)
    return authorization_url

async def get_token(client_id, client_secret):
    code = st.experimental_get_query_params()['code']
    print(code)
    data = {
        "client_id":client_id,
        "client_secret":client_secret,
        "code":code,
    }
    token = requests.post("https://todoist.com/oauth/access_token", data=data)
    token = token.json()['access_token']
    return token