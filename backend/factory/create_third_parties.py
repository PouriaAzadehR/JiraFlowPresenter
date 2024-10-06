import os

from Backend.infra.issue_tracker.jira_connector import connect_to_jira
from Backend.third_parties.issue_tracker.jira.jira_implementation import JiraImplementation


def create_third_parties():
    """Factory function to initialize and return all third-party integrations."""

    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    jira_client = connect_to_jira(jira_url, username, password)

    jira_implementation = JiraImplementation(jira_client)

    return {
        'jira_implementation': jira_implementation
    }
