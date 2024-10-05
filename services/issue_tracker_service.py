class IssueTrackerService:
    def __init__(self, issue_tracker_client):
        self.issue_tracker_client = issue_tracker_client

    def fetch_active_sprint_issues(self, board_id, exception_statuses):
        """Fetch the active sprint issues from the issue tracker."""
        active_sprint = self.issue_tracker_client.get_active_sprint(board_id)
        issues = self.issue_tracker_client.fetch_issues_from_sprint(active_sprint.id, exception_statuses)

        # Extract detailed information from the issues
        issues_details = [self.issue_tracker_client.extract_issue_details(issue) for issue in issues]
        return issues_details
