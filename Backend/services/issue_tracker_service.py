class IssueTrackerService:
    def __init__(self, issue_tracker_client):
        self.issue_tracker_client = issue_tracker_client

    def fetch_sprint_issues(self, sprint_id):
        """Fetch the sprint issues from the issue tracker."""
        issues = self.issue_tracker_client.fetch_issues_from_sprint(sprint_id)

        # Extract detailed information from the issues
        issues_details = [self.issue_tracker_client.extract_issue_details(issue) for issue in issues]
        return issues_details

    def get_all_boards(self):
        """Fetch all Jira boards."""
        return self.issue_tracker_client.list_all_boards()

    def get_sprints_for_board(self, board_id):
        """
        Fetch the sprints for a specific board from the issue tracker client.
        """
        return self.issue_tracker_client.list_sprints_for_board(board_id)
