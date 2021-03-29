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

    def _tasks_to_dataframe(self, items):
        df_tasks = pd.DataFrame()
        df_dues = pd.DataFrame()
        for item_i in items:
            
            item = item_i.data # getting the data as a dictionary
            try:
                df_due = pd.DataFrame(item['due'], index=[0]) # due date is a dict
            except:
                
                df_due = pd.DataFrame({
                    'date': [0], 
                    'is_recurring': [0], 
                    'lang': [0], 
                    'string': [0], 
                    'timezone': [0]
                })
            
            df_due['id'] =  item['id'] # id associated with this task and due date
            item.pop('due') # removing due date from the full dict
            item.pop('labels') # removing the labels from the full dict
            # this is kind of ugly, maybe worth looking into it sometime (it works)
            
            df_tasks = df_tasks.append(pd.DataFrame(item, index=[0]), ignore_index=True)
            df_dues = df_dues.append(df_due, ignore_index=True)

        self.df_tasks = df_tasks
        self.df_dues  = df_dues

    def _get_tasks(self):

        items = self.api["items"]
        self._tasks_to_dataframe(items)
    
    def _get_projects(self):
        projects = self.api["projects"]
        df_projects = pd.DataFrame()
        for p in projects:
            df_project = pd.DataFrame(p.data, index=[0])
            df_projects = df_projects.append(df_project, ignore_index=True)

        self.df_projects = df_projects

    def _merge_dfs(self):
        self.df_full = self.df_tasks.merge(self.df_projects, left_on='project_id', right_on='project-id')
        self.df_full = self.df_full.merge(self.df_dues, left_on='id', right_on='dues-id')

    def _preprocess(self):

        self._get_tasks()
        self._get_projects()

        for c in self.df_projects.columns:
            self.df_projects = self.df_projects.rename(columns={c:"project-"+c})
        for c in self.df_dues.columns:
            self.df_dues = self.df_dues.rename(columns={c:"dues-"+c})
        
        self._merge_dfs()
        
        self.df_full['datehour_completed'] = pd.to_datetime(self.df_full['date_completed'])
        self.df_full['datehour_completed'] = pd.DatetimeIndex(self.df_full['datehour_completed']).tz_convert(None)

    def collect(self):
        self._preprocess()

        return self.df_full
