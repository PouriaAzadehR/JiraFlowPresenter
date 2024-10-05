from jira import JIRA
from third_parties.issue_tracker.issue_tracking_inteface import IssueTrackingInterface


class JiraImplementation(IssueTrackingInterface):
    def __init__(self, jira_url, username, password):
        self.jira = JIRA(server=jira_url, auth=(username, password))

    def get_active_sprint(self, board_id):
        """Get the active sprint for the given board."""
        sprints = self.jira.sprints(board_id)
        for sprint in sprints:
            if sprint.state.lower() == 'active':
                return sprint
        raise Exception("No active sprint found")

    def fetch_issues_from_sprint(self, sprint_id, exception_statuses):
        """Fetch issues from the specified sprint."""
        exception_statuses_jql = ','.join([f'"{status}"' for status in exception_statuses])
        jql = f"Sprint = {sprint_id} AND status NOT IN ({exception_statuses_jql})"
        return self.jira.search_issues(jql)

    def extract_issue_details(self, issue):
        """Extract details from the issue."""
        return {
            "title": issue.fields.summary,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "deadline": issue.fields.duedate,
            "krs": issue.fields.customfield_10004,  # example for KRs field
            "stakeholder": issue.fields.customfield_10005,
            "accomplishments": issue.fields.customfield_10006,
            "challenges": issue.fields.customfield_10007,
            "status": issue.fields.status.name,
            "start": issue.fields.created,
            "estimate": issue.fields.timeoriginalestimate,
            "scope_changed": "Yes" if issue.fields.customfield_10008 else "No",
            "progress_statuses_dates": [],
            "gantt_chart_image_path": f"{issue.key}_gantt_chart.png"
        }
