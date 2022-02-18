import pandas as pd
import streamlit as st
import todoist


class DataCollector:
    def __init__(self, token):
        self.token = token
        self.items = pd.DataFrame()
        self.projects = pd.DataFrame()
        self.got_all_tasks = False
        self.api = todoist.TodoistAPI(self.token)
        self.api.sync()

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

    def _collect_all_completed_tasks(self):
        """
        gets all the tasks and stores it
        """
        self.got_all_tasks = False
        i = 0
        old_shape = 0
        while not self.got_all_tasks:
            self._collect_completed_tasks(limit=200, offset=i)
            new_shape = self.items.shape[0]
            if new_shape != old_shape:
                old_shape = new_shape
                i += 200
            else:
                self.got_all_tasks = True

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
