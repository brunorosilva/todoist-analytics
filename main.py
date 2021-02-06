import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
import todoist
from credentials import token
from todoist.managers.completed import CompletedManager
from datetime import datetime


class data_collector():
    def __init__(self, token):
        self.token = token
        try:
            self.api = todoist.TodoistAPI(self.token)
            self.api.sync()
            print("Connected with the api\n\n")
        except:
            print("Please, copy your api key in the credentials.py file")

    def tasks_to_dataframe(self, items):
        df_tasks = pd.DataFrame()
        for item in items:
            df_task = pd.DataFrame({
            "added_by_uid": item['added_by_uid'],
            "assigned_by_uid": item['assigned_by_uid'],
            "checked": item['checked'],
            "child_order": item['child_order'],
            "collapsed": item['collapsed'],
            "content": item['content'],
            "date_added": item['date_added'],
            "date_completed": item['date_completed'],
            "day_order": item['day_order'],
            "due": item['due'],
            "has_more_notes": item['has_more_notes'],
            "id": item['id'],
            "in_history": item['in_history'],
            "is_deleted": item['is_deleted'],
            "labels": item['labels'],
            "parent_id": item['parent_id'],
            "priority": item['priority'],
            "project_id": item['project_id'],
            "responsible_uid": item['responsible_uid'],
            "section_id": item['section_id'],
            "sync_id": item['sync_id'],
            "user_id": item['user_id']})
            df_tasks = df_tasks.append(df_task, ignore_index=True)
        return df_tasks

    def get_done_tasks(self, start_time=0, end_time=datetime.now()):
        
        df_tasks = tasks_to_dataframe(self.api["items"])



        print(pd.DataFrame(tasks_dict))


dc = data_collector(token)
dc.get_done_tasks()
