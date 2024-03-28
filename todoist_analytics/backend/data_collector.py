import time
import numpy as np
import pandas as pd
import streamlit as st
from todoist_api_python.api import TodoistAPI
from todoist_analytics.backend.sync_api import TodoistSyncAPI
from todoist_analytics.frontend.colorscale import color_name_to_hex


class DataCollector:
    def __init__(self, token):
        self.token = token
        self.sync_api = TodoistSyncAPI(token)
        self.api = TodoistAPI(token)
        self.current_offset = 0
        self.has_run_user_timezone_once = False

    def get_all_projects(self):
        return self.api.get_projects()

    def get_user_timezone(self):
        if self.has_run_user_timezone_once is False:
            user = self.sync_api.get_users()
            self.user_tz = user["user"]["tz_info"]["timezone"]
            self.has_run_user_timezone_once = True
        else:
            pass
        return self.user_tz


    def collect_completed_tasks(self, offset, items_df, batch_limit=200):
        data = self.sync_api.get_completed_items(limit=batch_limit, offset=offset)
        if data == None:
            time.sleep(3)
            self.collect_completed_tasks(batch_limit, offset, items_df)
        elif len(data["items"]) != 0:
            items_df = self.append_to_properties(data, items_df)
        return items_df

    def append_to_properties(self, data, items_df):
        preprocessed_items = self.preprocess_completed_tasks(
            pd.DataFrame(data["items"]),
            pd.DataFrame.from_dict(data["projects"], orient="index"),
        )
        items_df = pd.concat([items_df, preprocessed_items])
        return items_df

    def collect_all_completed_tasks(self, limit=2000):
        """
        Gets all the tasks and stores them.
        This function may take too long to complete and timeout,
        so a limit is set to prevent this.
        """
        items_df = pd.DataFrame()
        stop_collecting = False
        old_shape = 0
        markdown_placeholder = st.empty()
        while not stop_collecting:
            items_df = self.collect_completed_tasks(self.current_offset, items_df)
            new_shape = items_df.shape[0]
            markdown_placeholder.write(f"Collected {new_shape} tasks, limit is {limit} tasks. (The API is slow)")
            if new_shape != old_shape and new_shape < limit:
                old_shape = new_shape
                self.current_offset = new_shape
            else:
                self.current_offset = new_shape
                stop_collecting = True
        markdown_placeholder.empty()

        return items_df

    @staticmethod
    def state_to_dataframe(state, key):
        data = [d.data for d in state[str(key)]]
        df = pd.DataFrame(data)
        return df

    def collect_active_tasks(self):
        data = self.api.get_tasks()
        active_tasks = self.state_to_dataframe(self.api.state, "items")
        
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
        
        active_tasks = data[keep_columns]
        active_tasks = active_tasks.loc[active_tasks["checked"] == 0]
        
        return active_tasks

    def preprocess_completed_tasks(self, completed_tasks, projects):
        completed_items_keep_columns = [
            "completed_at",
            "content",
            "id",
            "project_id",
            "task_id",
            "user_id",
            "datehour_completed",
            "completed_date",
            "completed_date_weekday",
            "project_name",
            "color",
            "isRecurrent",
            "hex_color",
        ]
        
        projects = projects.rename(columns={"id": "project_id"})
        
        completed_tasks["datehour_completed"] = pd.to_datetime(completed_tasks["completed_at"])
        completed_tasks["datehour_completed"] = pd.DatetimeIndex(completed_tasks["datehour_completed"]).tz_convert(self.get_user_timezone())
        completed_tasks["completed_date"] = pd.to_datetime(completed_tasks["datehour_completed"]).dt.date
        completed_tasks["completed_date_weekday"] = pd.to_datetime(completed_tasks["datehour_completed"]).dt.day_name()
        
        completed_tasks = completed_tasks.merge(
            projects[["project_id", "name", "color"]],
            how="left",
            left_on="project_id",
            right_on="project_id",
        )
        
        completed_tasks = completed_tasks.rename(columns={"name": "project_name"})
        
        completed_date_count = completed_tasks.groupby("task_id").agg({"completed_date": "nunique"})
        completed_date_count["isRecurrent"] = np.where(completed_date_count["completed_date"] > 1, 1, 0)
        completed_date_count.drop(columns="completed_date", inplace=True)
        
        completed_tasks = completed_tasks.merge(completed_date_count, left_on="task_id", right_index=True)
        
        completed_tasks["hex_color"] = completed_tasks["color"].apply(lambda x: color_name_to_hex[x])
        completed_tasks = completed_tasks[completed_items_keep_columns].drop_duplicates().dropna(subset=["completed_date"]).reset_index(drop=True)
        
        return completed_tasks
