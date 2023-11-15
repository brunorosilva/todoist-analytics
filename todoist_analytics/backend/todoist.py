import requests

class TodoistAPI:
   def __init__(self, token):
      self.token = token
      self.endpoint = "https://api.todoist.com/sync/v9"
      self.session = requests.Session()
      self.session.headers["Authorization"] = f"Bearer {self.token}"
   
   def sync(self):
      response = self.session.post(f"{self.endpoint}/sync", data={
         "sync_token": "*",
         "resource_types": '["all"]'
      })
      self.state = response.json()
   
   def get_all_completed(self, limit, offset):
      return self.session.get(
         f"{self.endpoint}/completed/get_all",
         params={ "limit": limit, "offset": offset }
      ).json()
