from jira import JIRAError
from Backend.third_parties.issue_tracker.issue_tracking_inteface import IssueTrackingInterface
from Backend.utils.date_helpers.date_formatter import format_date


class JiraImplementation(IssueTrackingInterface):
    def __init__(self, jira_instance):
        self.jira = jira_instance

    def get_active_sprint(self, board_id):
        """Get the active sprint for the given board."""
        sprints = self.jira.sprints(board_id)
        for sprint in sprints:
            if sprint.state.lower() == 'active':
                return sprint
        raise Exception("No active sprint found")

    def fetch_issues_from_sprint(self, sprint_id):
        """Fetch issues from the specified sprint."""
        jql = f"Sprint = {sprint_id}"
        return self.jira.search_issues(jql, expand='changelog')

    def extract_issue_details(self, issue):
        """
        Extracts necessary details from a JIRA issue.

        :param issue: A JIRA issue object.
        :return: A dictionary of extracted issue details.
        """
        details = {
            "title": issue.fields.summary,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "deadline": format_date(issue.fields.customfield_10703) if hasattr(issue.fields,
                                                                               'customfield_10703') and issue.fields.customfield_10703 else " ",
            "krs": issue.fields.customfield_10704 if hasattr(issue.fields,
                                                             'customfield_10704') and issue.fields.customfield_10704 else " ",
            "stakeholder": issue.fields.customfield_10707 if hasattr(issue.fields,
                                                                     'customfield_10707') and issue.fields.customfield_10707 else " ",
            "accomplishments": issue.fields.customfield_10706 if hasattr(issue.fields,
                                                                         'customfield_10706') and issue.fields.customfield_10706 else " ",
            "challenges": issue.fields.customfield_10705 if hasattr(issue.fields,
                                                                    'customfield_10705') and issue.fields.customfield_10705 else " ",
            "status": issue.fields.status.name,
            "estimate": f"{issue.fields.customfield_10107} Hours" if hasattr(issue.fields,
                                                                             'customfield_10107') and issue.fields.customfield_10107 else " ",
            "scope_changed": "Yes" if hasattr(issue.fields,
                                              'customfield_10030') and issue.fields.customfield_10030 else " "
        }

        # Determine the start date as the date when the issue first transitioned to "In Progress"
        changelog = issue.changelog
        start = None
        for history in changelog.histories:
            for item in history.items:
                if item.field == "status" and item.toString == "In Progress":
                    start = history.created.split('T')[0]
                    break
            if start:
                break

        details["start"] = format_date(start) if start else "Not Started"

        # Fetch the last three status changes
        status_changes = []
        for history in reversed(changelog.histories):
            for item in history.items:
                if item.field == "status":
                    mapped_status = item.toString
                    date_formatted = format_date(history.created.split('T')[0])
                    status_changes.append((mapped_status, date_formatted))
            if len(status_changes) == 4:
                break

        details["progress_statuses_dates"] = status_changes[::-1] if status_changes else [("No Status", "N/A")]

        return details

    def list_all_boards(self):
        """List all boards with their names and IDs in Jira."""

        try:
            boards = self.jira.boards()
            if not boards:
                return []

            boards_list = []
            for board in boards:
                board_info = {
                    "id": board.id,
                    "name": board.name
                }
                boards_list.append(board_info)

            return boards_list

        except JIRAError as e:
            raise Exception(f"Failed to fetch boards from JIRA: {e}")

    def list_sprints_for_board(self, board_id):
        """
        List all sprints for a given board in Jira.
        """
        try:
            sprints = self.jira.sprints(board_id)
            sprints_list = []
            for sprint in sprints:
                sprints_list.append({
                    'id': sprint.id,
                    'name': sprint.name,
                    'state': sprint.state
                })
            return sprints_list
        except JIRAError as e:
            raise Exception(f"Failed to fetch sprints for board {board_id}: {e}")
