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
        df_dues = pd.DataFrame()
        i = 0
        for item_i in items:
            
            item = item_i.data # getting the data as a dictionary
            try:
                #print(item['due'])
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

        return df_tasks, df_dues

    def get_done_tasks(self, start_time=0, end_time=datetime.now()):

        items = self.api["items"]
        df_full, df_dues = self.tasks_to_dataframe(items)
        return df_full, df_dues
        
dc = data_collector(token)
df_full, df_dues = dc.get_done_tasks()
df_full.to_csv("sample_data/tasks_{}.csv".format(datetime.today()))
df_dues.to_csv("sample_data/dues{}.csv".format(datetime.today()))
