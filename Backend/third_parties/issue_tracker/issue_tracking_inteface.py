from abc import ABC, abstractmethod


class IssueTrackingInterface(ABC):
    @abstractmethod
    def get_active_sprint(self, board_id: int):
        """Fetch the active sprint for a given board"""
        pass

    @abstractmethod
    def fetch_issues_from_sprint(self, sprint_id: int):
        """Fetch issues for a given sprint, excluding specified statuses"""
        pass

    @abstractmethod
    def extract_issue_details(self, issue):
        """Extract details for a specific issue"""
        pass

    @abstractmethod
    def list_all_boards(self):
        """Lists all boards with their IDs and names."""
        pass

    @abstractmethod
    def list_sprints_for_board(self, board_id):
        """Lists all Sprints with their IDs and names."""
        pass
