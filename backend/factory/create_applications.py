from backend.applications.issue_tracker_app import IssueTrackerApp


def create_application(services):
    """
    Creates the application layer by integrating services.

    :param services: Dictionary containing initialized services
    :return: A dictionary containing initialized applications
    """
    issue_tracker_service = services['issue_tracker_service']
    ppt_service = services['ppt_service']

    issue_tracker_app = IssueTrackerApp(issue_tracker_service, ppt_service)

    return {
        'issue_tracker_application': issue_tracker_app,
    }
