class IssueTrackerApp:
    def __init__(self, issue_tracker_service, ppt_service):
        self.issue_tracker_service = issue_tracker_service
        self.ppt_service = ppt_service

    def generate_sprint_ppt(self, sprint_id):
        """Generate PowerPoint for  sprint issues from an issue tracker."""

        issues_details = self.issue_tracker_service.fetch_sprint_issues(sprint_id)
        ppt_file = self.ppt_service.create_ppt(issues_details)

        return ppt_file

    def get_all_boards(self):
        """Application logic to list all boards."""
        print("are you here? in issue tracker app?")

        return self.issue_tracker_service.get_all_boards()

    def get_sprints_for_board(self, board_id):
        """
        Get the sprints for a specific board by calling the service.
        """
        return self.issue_tracker_service.get_sprints_for_board(board_id)
