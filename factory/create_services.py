import os

from infra.issue_tracker.jira_connector import connect_to_jira
from services.issue_tracker_service import IssueTrackerService
from services.ppt_service import PptService


def create_services():
    """Factory function to initialize and return all services."""

    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    jira_client = connect_to_jira(jira_url, username, password)

    issue_tracker_service = IssueTrackerService(jira_client)
    ppt_service = PptService()

    return {
        'issue_tracker_service': issue_tracker_service,
        'ppt_service': ppt_service
    }
