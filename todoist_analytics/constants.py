import os

import dotenv

dotenv.load_dotenv()
TODOIST_SYNC_BASE_API_URL = "https://api.todoist.com/sync/v9"
COMPLETED_URL_ENDPOINT = "completed/get_all"
SYNC_ENDPOINT = "sync"

TODOIST_CLIENT_ID = os.getenv("DEV_APP_ID")
TODOIST_CLIENT_SECRET = os.getenv("DEV_APP_SECRET")
