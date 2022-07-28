import time
import pandas as pd
import todoist
import streamlit as st


class DataCollector:
    def __init__(self, token):
        self.token = token
        self.items = pd.DataFrame()
        self.projects = pd.DataFrame()
        self.active_tasks = pd.DataFrame()
        self.api = todoist.api.TodoistAPI(self.token)
        self.api.sync()
        self.current_offset = 0
        self.tz = self.api.state["user"]["tz_info"]["timezone"]
        self._collect_all_completed_tasks()
        self._collect_active_tasks()

    def _collect_all_completed_tasks(self, limit=10000):
        collecting = True
        old_num_items = 0

        while collecting:
            self._collect_completed_tasks(limit=200, offset=self.current_offset)
            current_num_items = self.items.shape[0]
            if current_num_items != old_num_items and current_num_items < limit:
                old_num_items = current_num_items
                self.current_offset += 200
            else:
                self.current_offset = current_num_items
                collecting = False

    def _collect_completed_tasks(self, limit, offset):
        data = self.api.completed.get_all(limit=limit, offset=offset)

        if data == "Service Unavailable\n":
            time.sleep(3)
            self._collect_completed_tasks(limit, offset)
        else:
            if len(data["items"]) != 0:
                items = pd.DataFrame(data["items"])
                projects = pd.DataFrame.from_dict(data["projects"], orient="index")
                self.items = pd.concat([self.items, items])
                self.projects = pd.concat([self.projects, projects])

    def _collect_active_tasks(self):
        self.active_tasks = pd.DataFrame([d.data for d in self.api.state["items"]])
        self.active_tasks = self.active_tasks.loc[self.active_tasks["checked"] == 0]


@st.cache(show_spinner=False)
def get_data(token):
    dc = DataCollector(token)
    return dc.items, dc.active_tasks, dc.projects


color_code_to_hex = {30: "#b8256f",
                     31: "#db4035",
                     32: "#ff9933",
                     33: "#fad000",
                     34: "#afb83b",
                     35: "#7ecc49",
                     36: "#299438",
                     37: "#6accbc",
                     38: "#158fad",
                     39: "#14aaf5",
                     40: "#96c3eb",
                     41: "#4073ff",
                     42: "#884dff",
                     43: "#af38eb",
                     44: "#eb96eb",
                     45: "#e05194",
                     46: "#ff8d85",
                     47: "#808080",
                     48: "#b8b8b8",
                     49: "#ccac93"}
