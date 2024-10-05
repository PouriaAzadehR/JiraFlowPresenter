from applications.issue_tracker_app import IssueTrackerApp


def create_application(services):
    """
    Creates the application layer by integrating services.

    :param services: Dictionary containing initialized services
    :return: An instance of IssueTrackerApp
    """
    issue_tracker_service = services['issue_tracker_service']
    ppt_service = services['ppt_service']

    # Initialize the application layer, passing the services
    issue_tracker_app = IssueTrackerApp(issue_tracker_service, ppt_service)

    return issue_tracker_app