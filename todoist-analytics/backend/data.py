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

    def _preprocess(self, data):
        self.items = pd.DataFrame(data['items'])
        self.projects = pd.DataFrame.from_dict(data['projects'], orient='index')

    def collect(self, since=None, until=None):
        data = self.api.completed.get_all(until=until, since=since, limit=200)
        self._preprocess(data)
        

    
