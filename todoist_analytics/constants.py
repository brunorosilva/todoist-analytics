import streamlit as st

TODOIST_SYNC_BASE_API_URL = "https://api.todoist.com/sync/v9"
COMPLETED_URL_ENDPOINT = "completed/get_all"
SYNC_ENDPOINT = "sync"

TODOIST_CLIENT_ID = st.secrets.app_client_id
TODOIST_CLIENT_SECRET = st.secrets.app_secret
