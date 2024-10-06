import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("USERNAME")
JIRA_PASSWORD = os.getenv("PASSWORD")
APP_PORT = int(os.getenv("APP_PORT", 5000))
