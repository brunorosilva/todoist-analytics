import requests

from todoist_analytics.constants import (
    COMPLETED_URL_ENDPOINT,
    SYNC_ENDPOINT,
    TODOIST_SYNC_BASE_API_URL,
)


class TodoistSyncAPI:
    def __init__(self, token) -> None:
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_completed_items(self, limit=200, offset=0):
        try:
            completed_params = {
                "limit": limit,
                "offset": offset,
            }
            completed_url = f"{TODOIST_SYNC_BASE_API_URL}/{COMPLETED_URL_ENDPOINT}"
            response = requests.get(
                completed_url, headers=self.headers, params=completed_params
            )

            if response.status_code == 200:
                completed_items = response.json()

                return completed_items

            else:
                print(f"Todoist API returned status code {response.status_code}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def get_users(self):
        try:
            users_call_params = {"resource_types": '["user"]'}
            sync_url = f"{TODOIST_SYNC_BASE_API_URL}/{SYNC_ENDPOINT}"
            response = requests.get(
                sync_url, headers=self.headers, params=users_call_params
            )
            if response.status_code == 200:
                users = response.json()

                return users

            else:
                print(f"Todoist API returned status code {response.status_code}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
