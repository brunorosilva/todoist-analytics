import pandas as pd
import streamlit as st
import todoist


class DataCollector:
    def __init__(self, token):
        self.token = token
        self.items = pd.DataFrame()
        self.projects = pd.DataFrame()
        self.api = todoist.TodoistAPI(self.token)
        self.api.sync()
        self.current_offset = 0

    def get_user_timezone(self):
        self.tz = self.api.state["user"]["tz_info"]["timezone"]

    def _collect_active_tasks(self):
        pass

    def _collect_completed_tasks(self, limit, offset):
        data = self.api.completed.get_all(limit=limit, offset=offset)
        self._append_to_properties(data)

    def _append_to_properties(self, data):
        self.items = self.items.append(pd.DataFrame(data["items"]))
        self.projects = self.projects.append(
            pd.DataFrame.from_dict(data["projects"], orient="index")
        )

    def _collect_all_completed_tasks(self, limit=2000):
        """
        gets all the tasks and stores it
        this function may take too long to complete and timeout,
        a limit is set in order to prevent this
        """
        stop_collecting = False
        old_shape = 0

        while not stop_collecting:
            self._collect_completed_tasks(limit=200, offset=self.current_offset)
            new_shape = self.items.shape[0]
            if new_shape != old_shape and new_shape < limit:
                old_shape = new_shape
                self.current_offset += 200
            else:
                self.current_offset = new_shape
                stop_collecting = True

    def _state_to_dataframe(self, state, key):
        f = [d.data for d in state[str(key)]]
        f = pd.DataFrame(f)
        return f

    def _collect_active_tasks(self):
        self.active_tasks = self._state_to_dataframe(self.api.state, "items")
        keep_columns = [
            "checked",
            "content",
            "added_by_uid",
            "description",
            "due",
            "labels",
            "priority",
            "project_id",
            "date_added",
            "id",
        ]
        self.active_tasks = self.active_tasks[keep_columns]
        self.active_tasks = self.active_tasks.loc[self.active_tasks["checked"] == 0]
