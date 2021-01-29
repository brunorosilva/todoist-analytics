import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
import todoist
from credentials import token
from todoist.managers.completed import CompletedManager

api = todoist.TodoistAPI(token)
api.sync()

parsed = api.completed.get_all()
print(json.dumps(parsed, indent=4, sort_keys=True)) 
# for item in api.state['items']:
#     if item['date_completed'] is not None:
#         print(item)
