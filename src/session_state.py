from streamlit.scriptrunner import get_script_run_ctx
from streamlit.server.server import Server


# SessionState class that has all the information
# Credits to https://github.com/uiucanh/streamlit-google-oauth
class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


# Get function to get any value from session state
# Credits to https://github.com/uiucanh/streamlit-google-oauth
def get(**kwargs):
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
