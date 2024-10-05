class IssueTrackerApp:
    def __init__(self, issue_tracker_service, ppt_service):
        self.issue_tracker_service = issue_tracker_service
        self.ppt_service = ppt_service

    def generate_active_sprint_ppt(self, board_id, exception_statuses):
        """Generate PowerPoint for active sprint issues from an issue tracker."""

        issues_details = self.issue_tracker_service.fetch_active_sprint_issues(board_id, exception_statuses)
        ppt_file = self.ppt_service.create_ppt(issues_details)

        return ppt_file
