from Backend.factory.create_third_parties import create_third_parties
from Backend.services.issue_tracker_service import IssueTrackerService
from Backend.services.ppt_service import PptService


def create_services():
    """Factory function to initialize and return all services."""

    third_parties = create_third_parties()

    jira_implementation = third_parties['jira_implementation']

    issue_tracker_service = IssueTrackerService(jira_implementation)
    ppt_service = PptService()

    return {
        'issue_tracker_service': issue_tracker_service,
        'ppt_service': ppt_service
    }
