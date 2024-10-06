from jira import JIRA


def connect_to_jira(jira_url, username, password):
    """Establish connection to Jira and return the connected client."""
    try:
        jira_client = JIRA(server=jira_url, auth=(username, password))
        return jira_client
    except Exception as e:
        raise Exception(f"Failed to connect to Jira: {e}")
