import pandas as pd
import todoist


class DataCollector:
    def __init__(self, token):
        self.token = token
        self.items = pd.DataFrame()
        self.projects = pd.DataFrame()
        self.got_all_tasks = False
        try:
            self.api = todoist.TodoistAPI(self.token)
            self.api.sync()
            print("Connected with the api\n\n")
        except:
            print("Please, copy your api key in the credentials.py file")

    def collect(self, since=None, until=None):
        data = self.api.completed.get_all(until=until, since=since, limit=200)
        self._append_to_properties(data)

    def _append_to_properties(self, data):
        self.items = self.items.append(pd.DataFrame(data["items"]))
        self.projects = self.projects.append(
            pd.DataFrame.from_dict(data["projects"], orient="index")
        )

    def collect_all(self):
        """
        gets all the tasks and stores it
        """
        self.got_all_tasks = False
        i = 0
        old_shape = 0
        while not self.got_all_tasks:
            data = self.api.completed.get_all(limit=200, offset=i)
            self._append_to_properties(data)
            new_shape = self.items.shape[0]
            if new_shape != old_shape:
                old_shape = new_shape
                i += 200
            else:
                print(f"Got all {len(self.items)} tasks")
                self.got_all_tasks = True
