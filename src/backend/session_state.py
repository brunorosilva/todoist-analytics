import streamlit.scriptrunner as ReportThread
from streamlit.server.server import Server
"""
Credits to https://github.com/uiucanh/streamlit-google-oauth
"""

"""Hack to add per-session state to Streamlit.
Usage
-----
>>> import SessionState
>>>
>>> session_state = SessionState.get(user_name='', favorite_color='black')
>>> session_state.user_name
''
>>> session_state.user_name = 'Mary'
>>> session_state.favorite_color
'black'
Since you set user_name above, next time your script runs this will be the
result:
>>> session_state = get(user_name='', favorite_color='black')
>>> session_state.user_name
'Mary'
"""


class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def get(**kwargs):
    ctx = ReportThread.get_script_run_ctx()

    this_session = None

    current_server = Server.get_current()

    if hasattr(current_server, "_session_infos"):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
            # Streamlit < 0.54.0
            (hasattr(s, "_main_dg") and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.65.2
            (
                not hasattr(s, "_main_dg")
                and s._uploaded_file_mgr == ctx.uploaded_file_mgr
            )
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object. "
            "Are you doing something fancy with threads?"
        )

    # Got the session object! Now let's attach some state into it.

    if not hasattr(this_session, "_custom_session_state"):
        this_session._custom_session_state = SessionState(**kwargs)

    return this_session._custom_session_state
